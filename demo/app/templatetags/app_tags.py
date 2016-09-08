# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import template

register = template.Library()


@register.inclusion_tag('app/tags/tag_template.html')
def example_inclusion_tag():
    """
    An example of an inclusion tag.
    """
    return {'tag_name': 'example_inclusion_tag'}


@register.simple_tag
def example_simple_tag(*args):
    """
    An example of a simple tag.
    """
    return 'example_simple_tag'


@register.assignment_tag
def example_assignment_tag():
    """
    An example of an assignment tag.

    From the Django documentation:
        Deprecated since version 1.9:
        simple_tag can now store results in a template variable and should be
        used instead.
    """
    return 'example_assignment_tag'


@register.filter(name='plus')
def addition(value, arg=1):
    return value + arg
