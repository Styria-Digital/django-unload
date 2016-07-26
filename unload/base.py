# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

from distutils.version import StrictVersion

from django.template.base import (
    Lexer, Template as BaseTemplate, InvalidTemplateLibrary)

from .settings import (DJANGO_VERSION, BUILT_IN_TAGS, I18N_TAGS, L10N_TAGS,
                       CACHE_TAGS, STATIC_TAGS, BUILT_IN_FILTERS)

if StrictVersion(DJANGO_VERSION) > StrictVersion('1.8'):
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

    def list_duplicates(self):
        """
        List duplicate results, i.e. duplicate library, tag or filter loads.
        If possible, tries to combine the results in the same row.

        :returns: table (list of lists), header (list of header names)
        """

        temp_table = {}
        # Find duplicate library loads
        for module in self.loaded_modules:
            lines = self.loaded_modules[module]
            lines_str = ', '.join(map(str, lines))
            if len(lines) > 1 and lines_str not in temp_table.keys():
                temp_table[lines_str] = [module, None]

        # Find duplicate member loads
        for member in self.loaded_members:
            lines = self.loaded_members[member]
            lines_str = ', '.join(map(str, lines))
            if len(lines) > 1:
                if lines_str not in temp_table.keys():
                    temp_table[lines_str] = [None, member]
                else:
                    temp_table[lines_str][1] = member

        # Prepare output format
        headers = ['Duplicate module', 'Duplicate tag/filter', 'Line number']
        table = []
        if temp_table:
            for key in temp_table:
                row = temp_table[key]
                row.append(key)
                table.append(row)

        return table, headers

    def list_unutilized_items(self):
        """
        List unutilized modules, tags and filters in a single table
        """
        modules = []
        members = []
        # List unutilized modules
        if self.utilized_modules:
            for module in self.utilized_modules:
                if not self.utilized_modules[module]:
                    modules.append(module)

        # List unutilized tags/filters
        if self.utilized_members:
            for member in self.utilized_members:
                if not self.utilized_members[member]:
                    members.append(member)

        if len(modules) > len(members):
            diff = len(modules) - len(members)
            members += [None] * diff
        else:
            diff = len(members) - len(modules)
            modules += [None] * diff

        headers = ['Unutilized module', 'Unutilized tag/filter']
        table = zip(modules, members)

        return table, headers

    def _get_templatetags_members(self):
        """
        Get the names of tags and filters from available templatetags modules.

        :returns: {'somelib': [tags]}, {'somelib': [filters]}
        """
        tags = {}
        filters = {}
        for module in self.loaded_modules:
            try:
                lib = get_library(module)
            except InvalidTemplateLibrary:
                msg = ('Unable to locate the loaded library! Library: {}; '
                       'Template: {}\n').format(module, self.name)
                sys.stdout.write(msg)
                tags[module] = []
                continue
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
