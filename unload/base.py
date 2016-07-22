# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template.base import Lexer, Template as BaseTemplate

from .settings import DJANGO_VERSION

if DJANGO_VERSION > (1, 8):
    from django.template.base import get_library


# https://docs.djangoproject.com/en/1.9/ref/templates/builtins/#built-in-tag-reference
BUILT_IN_TAGS = {
    'as': None,
    'autoescape': 'endautoescape',
    'block': 'endblock',
    'blocktrans': 'endblocktrans',
    'comment': 'endcomment',
    'csrf_token': None,
    'cycle': None,
    'debug': None,
    'extends': None,
    'filter': 'endfilter',
    'firstof': None,
    'for': 'endfor',
    'elif': None,
    'else': None,
    'empty': None,
    'if': 'endif',
    'ifchanged': 'endifchanged',
    'ifequal': 'endifequal',
    'ifnotequal': 'endifnotequal',
    'in': None,
    'include': None,
    'load': None,
    'lorem': None,
    'not': None,
    'now': None,
    'spaceless': 'endspaceless',
    'ssi': None,
    'templatetag': None,
    'url': None,
    'verbatim': 'endverbatim',
    'widthratio': None,
    'with': 'endwith'
}

I18N_TAGS = {
    'trans': 'endtrans',
    'blocktrans': 'endblocktrans',
    'plural': None,
    'get_language_info_list': None,
    'get_available_languages': None,
    'get_language_info': None,
    'language': None,
    'get_current_language': None,
    'get_current_language_bidi': None
}

L10N_TAGS = {
    'localize': 'endlocalize'
}

CACHE_TAGS = {
    'cache': 'endcache'
}

STATIC_TAGS = {
    'static': None,
    'get_media_prefix': None,
    'get_static_prefix': None
}


class Template(BaseTemplate):

    def __init__(self, template_string, origin=None, name=None, engine=None):
        super(Template, self).__init__(template_string, origin, name, engine)

        # Used for backwards compatibility (implemented in Django 1.9)
        if not hasattr(self, 'source'):
            self.source = template_string

        self.tokens = self._get_tokens()
        # The modules and tags manually specified (loaded) by the developer
        self.loaded_modules, self.loaded_tags = self._parse_load_block()
        self.used_tags = self._get_used_templatetags()
        # Get the tags and filters available to this template
        self.tags, self.filters = self._get_templatetags_members()
        self.utilized_modules = self.get_utilized_modules()
        self.utilized_tags = self.get_utilized_tags()

    def get_utilized_tags(self):
        pass

    def get_utilized_modules(self):
        """
        Separates the loaded modules based on their usage.

        :returns: {'module_name': Boolean}
        """
        module_used = {}
        for module in self.loaded_modules:
            used = False
            for tag in self.used_templatetags:
                if tag in self.tags[module]:
                    used = True
            module_used[module] = used
        return module_used

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

    def _get_used_templatetags(self):
        """
        Get the list of custom template tags used in the template.

        :returns: a list of custom template tags
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
