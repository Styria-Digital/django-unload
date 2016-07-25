# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

from django.template.base import Lexer, Template as BaseTemplate

from .settings import (DJANGO_VERSION, BUILT_IN_TAGS, I18N_TAGS, L10N_TAGS,
                       CACHE_TAGS, STATIC_TAGS, BUILT_IN_FILTERS)

if DJANGO_VERSION > (1, 8):
    from django.template.base import get_library


class Template(BaseTemplate):

    def __init__(self, template_string, origin=None, name=None, engine=None):
        super(Template, self).__init__(template_string, origin, name, engine)

        # Used for backwards compatibility (implemented in Django 1.9)
        if not hasattr(self, 'source'):
            self.source = template_string

        self.tokens = self._get_tokens()
        # The manually specified (loaded) modules and members (tags/filters)
        self.loaded_modules, self.loaded_members = self._parse_load_block()
        self.used_tags = self._get_used_tags()
        self.used_filters = self._get_used_filters()
        # Get the tags and filters available to this template
        self.tags, self.filters = self._get_templatetags_members()
        # Find utilized modules, tags and filters
        self.utilized_modules = self._get_utilized_modules()
        self.utilized_members = self._get_utilized_members()

    def evaluate(self):
        """
        A public method for outputting the evaluation results to the console.

        :returns: None
        """
        sys.stdout.write("\nEvaluating template: {}\n".format(self.name))
        self._list_duplicate_module_loads()
        self._list_duplicate_member_loads()
        self._list_unutilized_modules()
        self._list_unutilized_members()

    def _list_duplicate_module_loads(self):
        """
        List duplicate module loads and the line numbers they are located at.

        :returns: None
        """
        if self.loaded_modules:
            sys.stdout.write("Duplicate module loads:\n")
            duplicate_module_loads = False
            for module in self.loaded_modules:
                if len(self.loaded_modules[module]) > 1:
                    lines = self.loaded_modules[module]
                    duplicate_module_loads = True
                    sys.stdout.write("\t{} || {}\n".format(
                        module, ', '.join(map(str, lines))))
            # No duplicate module loads were found
            if not duplicate_module_loads:
                sys.stdout.write("\tNo duplicate member loads!\n")

    def _list_duplicate_member_loads(self):
        """
        List duplicate loads of tags and filters and the line numbers they are
        located at.

        :returns: None
        """
        if self.loaded_members:
            sys.stdout.write("Duplicate member loads:\n")
            duplicate_member_loads = False
            for member in self.loaded_members:
                if len(self.loaded_members[member]) > 1:
                    lines = self.loaded_members[member]
                    duplicate_member_loads = True
                    sys.stdout.write("\t{} || {}\n".format(
                        member, ', '.join(map(str, lines))))
            # No duplicate member loads were found
            if not duplicate_member_loads:
                sys.stdout.write("\tNo duplicate member loads!\n")

    def _list_unutilized_modules(self):
        """
        List unutilized modules.

        :returns: None
        """
        if self.utilized_modules:
            sys.stdout.write("Searching for unutilized modules...\n")
            unutilized_modules = []
            for module in self.utilized_modules:
                if not self.utilized_modules[module]:
                    unutilized_modules.append(module)

            if unutilized_modules:
                sys.stdout.write("\tUnutilized modules: {}\n".format(
                    ', '.join(unutilized_modules)))
            else:
                sys.stdout.write("\tAll modules are utilized!\n")

    def _list_unutilized_members(self):
        """
        List unutilized tags and filters.

        :returns: None
        """
        if self.utilized_members:
            sys.stdout.write("Searching for unutilized members...\n")
            unutilized_members = []
            for member in self.utilized_members:
                if not self.utilized_members[member]:
                    unutilized_members.append(member)

            if unutilized_members:
                sys.stdout.write("\tUnutilized modules: {}\n".format(
                    ', '.join(unutilized_members)))
            else:
                sys.stdout.write("\tAll modules are utilized!\n")

    def _get_utilized_members(self):
        """
        Separates the loaded tags based on their utilization.

        :returns: {'tag_name': Boolean}
        """
        utilized_members = {}

        for member in self.loaded_members:
            utilized = False
            if member in self.used_tags or member in self.used_filters:
                utilized = True
            utilized_members[member] = utilized

        return utilized_members

    def _get_utilized_modules(self):
        """
        Separates the loaded modules based on their utilization.

        :returns: {'module_name': Boolean}
        """
        utilized_modules = {}

        for module in self.loaded_modules:
            utilized = False

            for tag in self.used_tags:
                if tag in self.tags[module]:
                    utilized = True
                    break

            if not utilized and self.used_filters:
                for custom_filter in self.used_filters:
                    if custom_filter in self.filters[module]:
                        utilized = True
                        break

            utilized_modules[module] = utilized

        return utilized_modules

    def _get_templatetags_members(self):
        """
        Get the names of tags and filters from available templatetags modules.

        :returns: {'somelib': [tags]}, {'somelib': [filters]}
        """
        tags = {}
        filters = {}
        for module in self.loaded_modules:
            lib = get_library(module)
            tags[module] = lib.tags.keys()
            filters[module] = lib.filters.keys()

        return tags, filters

    def _get_tokens(self):
        """
        Get the list of tokens from the template source.

        A modified version of Django's compile_nodelist method (Template class)
        https://github.com/django/django/blob/master/django/template/base.py#L221

        :returns: a list of Tokens
        """
        # From Django's source code
        if self.engine.debug:
            from django.template.debug import DebugLexer
            lexer = DebugLexer(self.source, self.origin)
        else:
            lexer = Lexer(self.source, self.origin)

        return lexer.tokenize()

    def _parse_load_block(self):
        """
        Get the names of loaded templatetags modules as well as individually
        loaded tags and the line numbers they are located at.

        :returns: {'module': [line_numbers]}, {'member': [line_numbers]}
        """

        def add_module(modules, module, line_number):
            """
            Add the module's name and its line number to the modules dictionary

            :modules: the modules dictionary
            :module: the module's name
            :line_number: the line number at which the module is loaded
            :returns: a modified modules dictionary
            """
            if module not in modules:
                modules[module] = [line_number]
            else:
                # The same module can be loaded multiple times
                if line_number not in modules[module]:
                    modules[module].append(line_number)

            return modules

        def add_member(members, member, line_number):
            """
            Add the member's (tag/filter) name and its line number to the
            members dictionary.

            :members: the members dictionary
            :member: the member's name
            :line_number: the line number at which the member is loaded
            :returns: a modified members dictionary
            """
            if member not in members:
                members[member] = [line_number]
            else:
                # The same member can be loaded multiple times
                if line_number not in members[member]:
                    members[member].append(line_number)

            return members

        modules = {}
        members = {}

        for token in self.tokens:
            token_content = token.split_contents()
            # Extract load blocks
            if token.token_type == 2 and token_content[0] == 'load':
                # FROM syntax is used; individual members are loaded
                if token_content >= 4 and token_content[-2] == 'from':
                    # Add loaded module
                    module = token_content[-1]
                    modules = add_module(modules, module, token.lineno)
                    # Add loaded members
                    loaded_members = token_content[1:-2]
                    for member in loaded_members:
                        members = add_member(members, member, token.lineno)
                # Regular syntax
                else:
                    # Multiple modules can be imported in the same load block
                    templatetags_modules = token_content[1:]
                    for module in templatetags_modules:
                        modules = add_module(modules, module, token.lineno)

        return modules, members

    def _get_used_tags(self):
        """
        Get the list of custom template tags used in the template.

        :returns: a list of custom tag names
        """
        used_tags = []
        for token in self.tokens:
            token_content = token.split_contents()
            # Extract blocks that do not contain one of the built-in tags
            if (token.token_type == 2 and
                    token_content[0] not in BUILT_IN_TAGS.keys() and
                    # Skip built-in 'end' tags
                    token_content[0] not in set(BUILT_IN_TAGS.values()) and
                    token_content[0] not in set(I18N_TAGS.values()) and
                    token_content[0] not in set(L10N_TAGS.values()) and
                    token_content[0] not in set(STATIC_TAGS.values()) and
                    token_content[0] not in set(CACHE_TAGS.values())):
                # Extract only the name of the template tag (ignore arguments)
                used_tags.append(token_content[0])

        return used_tags

    def _get_used_filters(self):
        """
        Get the list of custom filters used in the template.

        :returns: a list of custom filter names
        """

        def get_filters(content):
            """
            Get filter names from the token's content.

            WARNING: Multiple filters can be used simultaneously, e.g.:
                {{ some_list|safeseq|join:", " }}

            :content: String; the token's content
            :returns: a list of filter names
            """
            filters = []
            split_content = content.split('|')

            for item in split_content[1:]:
                if ':' in item:
                    item = item[:item.index(':')]
                filters.append(item)

            return filters

        used_filters = []

        for token in self.tokens:
            filters = []
            token_content = token.split_contents()

            # Variable token
            if token.token_type == 1 and '|' in token_content[0]:
                filters += get_filters(token_content[0])

            # Tag token
            elif token.token_type == 2:
                if '|' in ' '.join(token_content):
                    for item in token_content:
                        if '|' in item:
                            filters += get_filters(item)

            # Exclude built-in filters
            for filter_name in filters:
                if (filter_name not in BUILT_IN_FILTERS and
                        filter_name not in used_filters):
                    used_filters.append(filter_name)

        return used_filters
