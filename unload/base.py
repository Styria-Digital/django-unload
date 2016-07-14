# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template.base import Lexer, Template as BaseTemplate


class Template(BaseTemplate):

    def __init__(self, template_string, origin=None, name=None, engine=None):
        super(Template, self).__init__(template_string, origin, name, engine)

        # Used for backwards compatibility (implemented in Django 1.9)
        if not hasattr(self, 'source'):
            self.source = template_string

        self.tokens = self._get_tokens()

        if not self.tokens:
            raise ValueError('No tokens in the template!')
        else:
            self.templatetags_modules = self._get_templatetags_modules()

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

    def _get_templatetags_modules(self):
        """
        Returns a dictionary of loaded templatetags modules and a list of line
        numbers they are located at.

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
