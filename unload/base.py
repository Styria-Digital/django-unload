# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template.base import Lexer, Template as BaseTemplate

from .settings import (DJANGO_VERSION, BUILT_IN_TAGS, I18N_TAGS, L10N_TAGS,
                       CACHE_TAGS, STATIC_TAGS, BUILT_IN_FILTERS,
                       CACHE_FILTERS, FUTURE_FILTERS, I18N_FILTERS,
                       L10N_FILTERS, STATIC_FILTERS, TZ_FILTERS)

if DJANGO_VERSION > (1, 8):
    from django.template.base import get_library


class Template(BaseTemplate):

    def __init__(self, template_string, origin=None, name=None, engine=None):
        super(Template, self).__init__(template_string, origin, name, engine)

        # Used for backwards compatibility (implemented in Django 1.9)
        if not hasattr(self, 'source'):
            self.source = template_string

        self.tokens = self._get_tokens()
        # The modules and tags manually specified (loaded) by the developer
        self.loaded_modules, self.loaded_tags = self._parse_load_block()
        self.used_tags = self._get_used_tags()
        self.used_filters = self._get_used_filters()
        # Get the tags and filters available to this template
        self.tags, self.filters = self._get_templatetags_members()
        # Find utilized tags and filters
        self.utilized_modules = self.get_utilized_modules()
        self.utilized_tags = self.get_utilized_tags()

    def get_utilized_tags(self):
        """
        Separates the loaded tags based on their utilization.

        :returns: {'tag_name': Boolean}
        """
        utilized_tags = {}

        for tag in self.loaded_tags:
            utilized = False
            if tag in self.used_tags:
                utilized = True
            utilized_tags[tag] = utilized

        return utilized_tags

    def get_utilized_modules(self):
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

        :returns: {'module_name': [line_numbers]}, {'tag_name': [line_numbers]}
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

        def add_tag(tags, tag, line_number):
            """
            Add the tag's name and its line number to the tags dictionary

            :tags: the tags dictionary
            :tag: the tag's name
            :line_number: the line number at which the tag is loaded
            :returns: a modified tags dictionary
            """
            if tag not in tags:
                tags[tag] = [line_number]
            else:
                # The same tag can be loaded multiple times
                if line_number not in tags[tag]:
                    tags[tag].append(line_number)

            return tags

        modules = {}
        tags = {}

        for token in self.tokens:
            token_content = token.split_contents()
            # Extract load blocks
            if token.token_type == 2 and token_content[0] == 'load':
                # FROM syntax is used; individual tags are loaded
                if token_content >= 4 and token_content[-2] == 'from':
                    # Add loaded module
                    module = token_content[-1]
                    modules = add_module(modules, module, token.lineno)
                    # Add loaded tags
                    loaded_tags = token_content[1:-2]
                    for tag in loaded_tags:
                        tags = add_tag(tags, tag, token.lineno)
                # Regular syntax
                else:
                    # Multiple modules can be imported in the same load block
                    templatetags_modules = token_content[1:]
                    for module in templatetags_modules:
                        modules = add_module(modules, module, token.lineno)

        return modules, tags

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
