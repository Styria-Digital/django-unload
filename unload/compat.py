# -*- coding: utf-8 -*-

from __future__ import unicode_literals

try:
    from django.template.base import Lexer, DebugLexer
except ImportError:
    from django.template.base import Lexer
    from django.template.debug import DebugLexer

# InvalidTemplateLibrary was moved to django.template.library in
# Django 1.9
try:
    from django.template.library import InvalidTemplateLibrary
except ImportError:
    from django.template.base import InvalidTemplateLibrary

# The Django's template module was reorganized in 1.9.
try:
    from django.template.backends.django import get_installed_libraries
    from django.template.library import import_library
except ImportError:
    from django.template.base import get_library
    get_installed_libraries = None
    import_library = None


def get_lexer(template_string, origin=None, debug=False):
    """Get the Lexer instance.

    Depends on the engine's debug status.

    Args:
        template_string {str}: template's contents
        origin {Origin}: object
        debug {bool}: debug status

    Returns:
        {Lexer} or {DebugLexer} object

    """
    if debug:
        lexer_class = DebugLexer
    else:
        lexer_class = Lexer

    try:
        return lexer_class(template_string)
    except TypeError:
        return lexer_class(template_string, origin)


def get_templatetag_library(module):
    """Get the templatetag module's Library instance.

    Needed for extracting template tags and filters.

    Args:
        module {str}: module's name (e.g. 'app_tags')

    Returns:
        {Library}

    Raises:
        {AttributeError}: nonexistent module
        {InvalidTemplateLibrary}: the module does not have a variable
            named `register`

    """
    try:
        if import_library is not None and get_installed_libraries is not None:
            return import_library(get_installed_libraries().get(module))
        else:
            return get_library(module)
    except (AttributeError, InvalidTemplateLibrary):
        raise
