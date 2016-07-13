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
