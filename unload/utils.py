# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import django
import io

from importlib import import_module
from inspect import getmembers
from pkgutil import walk_packages

from django.apps import apps


def get_app(app_label):
    """
    Get the app object.

    :app_label: the app's label submitted by the user
    :returns: AppConfig
    """
    try:
        app = apps.get_app_config(app_label)
    except LookupError as le:
        raise le

    return app


def get_contents(filepath, encoding='UTF-8'):
    """
    Read the contents of the template file.

    A modified version of Django's get_contents method (Loader class)
    https://github.com/django/django/blob/master/django/template/loaders/filesystem.py#L22

    :filepath: absolute path to the template file
    :encoding: a string representing the engine's encoding
    :returns: contents of the template as a string
    """
    with io.open(filepath, encoding=encoding) as fp:
        return fp.read()


def get_templatetags_modules():
    """
    Find all templatetag modules in the project and the names of their tags and
    filters.

    :returns: {'module_name': [[tag_names], [filter_names]]}
    """
    module_tags = {}
    django_path = django.__path__[0]
    for module_loader, name, ispkg in walk_packages(django_path):
        if not ispkg and 'templatetags' in name:
            # Get the tags and filters registered in the module
            tags, filters = get_module_members(name)
            # Format the module's name in order to correspond to the name in
            # the load tag (remove "<app_name>.templatetags." from the name)
            split_name = name.split('.')
            idx = split_name.index('templatetags')
            module_name = '.'.join(split_name[idx + 1:])

            module_tags[module_name] = [tags, filters]

    return module_tags


def get_module_members(module_name):
    """
    Load the specified module and get the names of the registered tags and
    filters.

    :module_name: the module's name (e.g. package.subpackage.module)

    :returns: [tag_names], [filter_names]
    """
    tags = []
    filters = []

    module = import_module(module_name)
    members = getmembers(module)
    library_tuples = [elem for elem in members if isinstance(
        elem[1], django.template.Library)]

    if library_tuples:
        for lib_tup in library_tuples:
            lib_var, lib_obj = lib_tup
            tags += lib_obj.tags.keys()
            filters += lib_obj.filters.keys()
    else:
        raise ValueError('Not a valid tag library: {}'.format(module_name))

    return tags, filters
