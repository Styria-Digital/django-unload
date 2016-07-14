# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template.base import Lexer, Template as BaseTemplate


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


class Template(BaseTemplate):

    def __init__(self, template_string, origin=None, name=None, engine=None):
        super(Template, self).__init__(template_string, origin, name, engine)

        # Used for backwards compatibility (implemented in Django 1.9)
        if not hasattr(self, 'source'):
            self.source = template_string

        self.tokens = self._get_tokens()

        if not self.tokens:
            self.loaded_modules = None
            self.loaded_templatetags = None
            self.status = 'No tokens found in the template'
        else:
            self.loaded_modules = self._get_loaded_templatetags_modules()
            self.loaded_templatetags = self._get_loaded_templatetags()
            # A placeholder (to be defined after the template is analyzed)
            self.status = None

    def _get_tokens(self):
        """
        Get the list of tokens from the template source.

        :returns: a list of Tokens
        """
        if self.engine.debug:
            from django.template.debug import DebugLexer
            lexer_class = DebugLexer
        else:
            lexer_class = Lexer

        lexer = lexer_class(self.source, self.origin)
        return lexer.tokenize()

    def _get_loaded_templatetags_modules(self):
        """
        Get the names of loaded templatetags modules and the line numbers they
        are located at.

        :returns: { 'module_name': [line_numbers] }
        """

        modules = {}
        for token in self.tokens:
            token_content = token.split_contents()
            # Extract load blocks
            if token.token_type == 2 and token_content[0] == 'load':
                templatetags_modules = token_content[1:]
                # Multiple modules can be imported in the same load block
                for module in templatetags_modules:
                    if module not in modules:
                        modules[module] = [token.lineno]
                    else:
                        # The same module can be imported multiple times
                        if token.lineno not in modules[module]:
                            modules[module].append(token.lineno)

        return modules

    def _get_loaded_templatetags(self):
        """
        Get the list of custom template tags used in the template.

        :returns: a list of custom template tags
        """
        loaded_tags = []
        for token in self.tokens:
            token_content = token.split_contents()
            # Extract blocks that do not contain one of the built-in tags
            if token.token_type == 2 and\
                    token_content[0] not in BUILT_IN_TAGS and\
                    token_content[0] not in list(set(BUILT_IN_TAGS.values())):
                # Extract only the name of the template tag (ignore arguments)
                loaded_tags.append(token_content[0])

        return loaded_tags
