# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template.base import Template as BaseTemplate

from .compat import get_lexer
from .settings import BUILT_IN_TAGS, BUILT_IN_TAG_VALUES, BUILT_IN_FILTERS
from .utils import get_filters, get_templatetag_members, update_dictionary


class Template(BaseTemplate):
    """
    An override of Django's Template class.

    After calling the parent class, the template is analyzed for duplicates
    and unnecessary loads.

    Additional attributes:
    :tokens: a list of tokens found in the template
    :loaded_modules: a dictionary of loaded modules
    :loaded_members: a dictionary of loaded tags/filters
    :used_tags: a list of custom tags used in the template
    :used_filters: a list of custom filters used in the template
    :tags: a dictionary of custom tags loaded into the template
    :filters: a dictionary of custom filters loaded into the template
    :utilized_modules: a dictionary of utilization statuses
    :utilized_members: a dictionary of utilization statuses
    """

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
        self.tags, self.filters = get_templatetag_members(
            self.name, self.loaded_modules)
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
                temp_table[lines_str] = [module, []]

        # Find duplicate member loads
        for member in self.loaded_members:
            lines = self.loaded_members[member]
            lines_str = ', '.join(map(str, lines))

            if len(lines) > 1:
                temp_table[lines_str][1].append(member)

        for key in temp_table:
            if temp_table[key][1] == []:
                temp_table[key][1] = None
            else:
                temp_table[key][1] = '; '.join(temp_table[key][1])

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

        return list(table), headers

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

    def _get_tokens(self):
        """
        Get the list of tokens from the template source.

        A modified version of Django's compile_nodelist method (Template class)
        https://github.com/django/django/blob/master/django/template/base.py#L221

        :returns: a list of Tokens
        """
        lexer = get_lexer(
            template_string=self.source,
            origin=self.origin,
            debug=self.engine.debug
        )

        return lexer.tokenize()

    def _parse_load_block(self):
        """
        Get the names of loaded templatetags modules as well as individually
        loaded tags and the line numbers they are located at.

        :returns: {'module': [line_numbers]}, {'member': [line_numbers]}
        """

        modules = {}
        members = {}

        for token in self.tokens:
            token_content = token.split_contents()
            # Extract load blocks
            if token.token_type == 2 and token_content[0] == 'load':
                # FROM syntax is used; individual members are loaded
                if len(token_content) >= 4 and token_content[-2] == 'from':
                    # Add loaded module
                    module = token_content[-1]
                    modules = update_dictionary(modules, module, token.lineno)
                    # Add loaded members
                    loaded_members = token_content[1:-2]
                    for member in loaded_members:
                        members = update_dictionary(
                            members, member, token.lineno)
                # Regular syntax
                else:
                    # Multiple modules can be imported in the same load block
                    templatetags_modules = token_content[1:]
                    for module in templatetags_modules:
                        modules = update_dictionary(
                            modules, module, token.lineno)

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
                    token_content[0] not in BUILT_IN_TAG_VALUES):
                # Extract only the name of the template tag (ignore arguments)
                used_tags.append(token_content[0])

        return used_tags

    def _get_used_filters(self):
        """
        Get the list of custom filters used in the template.

        :returns: a list of custom filter names
        """
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
