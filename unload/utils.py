# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import io
import os
import sys
from copy import deepcopy
from mimetypes import guess_type

from django.apps import apps
from django.conf import settings
from django.template.backends.django import DjangoTemplates
from tabulate import tabulate

from pip import get_installed_distributions

from .compat import InvalidTemplateLibrary, get_templatetag_library


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


def get_templates(directory, pkg_locations, app=None):
    """
    Traverse the project's template directories and get the paths of template
    files.

    :directory: String; path to directory
    :pkg_locations: a list of paths of 3rd party packages
    :app: AppConfig object

    :reeturns: a list of paths to template files
    """
    templates = []
    within_project = True
    for location in pkg_locations:
        if directory.startswith(location):
            within_project = False
            break
    # Get the template files from the directory
    if within_project:
        # Only one app needs to be scanned
        if app:
            if directory.startswith(app.path):
                templates = get_template_files(directory)
        else:
            templates += get_template_files(directory)

    return templates


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


def get_djangotemplates_engines():
    """
    Create template engines from the parameters in the settings file.

    :returns: a list of DjangoTemplates instances
    """
    engines = []
    template_settings = settings.TEMPLATES

    for params in template_settings:
        copied_params = deepcopy(params)
        backend = copied_params.pop('BACKEND')

        if backend == 'django.template.backends.django.DjangoTemplates':
            copied_params['NAME'] = 'django'
            engines.append(DjangoTemplates(params=copied_params))
        else:
            output_message(reason=2)

    return engines


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


def get_package_locations():
    """
    Get the paths of directories where 3rd packages are installed.

    :returns: a list of absolute paths
    """
    pkg_locations = []
    installed_pkgs = get_installed_distributions(local_only=True,
                                                 include_editables=False)
    for pkg in installed_pkgs:
        if pkg.location not in pkg_locations:
            pkg_locations.append(pkg.location)

    return pkg_locations


def get_template_files(template_dir):
    """
    Scan the provided template directory and its subdirectories for template
    files.

    :returns: a list of absolute paths to template files
    """
    templates = []
    for dirpath, dirnames, filenames in os.walk(template_dir):
        for filename in filenames:
            filetype = guess_type(filename)
            if filetype != (None, None):
                maintype, subtype = filetype[0].split('/')
                if maintype == 'text':
                    templates.append(os.path.join(dirpath, filename))

    return templates


def get_templatetag_members(template_name, loaded_modules, output=sys.stdout):
    """
    Get the names of tags and filters from available templatetags modules.

    :returns: {'somelib': [tags]}, {'somelib': [filters]}
    """
    tags = {}
    filters = {}
    for module in loaded_modules:
        try:
            lib = get_templatetag_library(module)
        except (AttributeError, InvalidTemplateLibrary):
            msg = ('Unable to locate the loaded library! Library: {}; '
                   'Template: {}\n').format(module, template_name)
            output.write(msg)
            tags[module] = []
            continue
        tags[module] = lib.tags.keys()
        filters[module] = lib.filters.keys()

    return tags, filters


def output_template_name(template_name, output=sys.stdout):
    """
    Output the template's name.

    :template_name: String
    :output: output destination (console=sys.stdout; testing=StringIO)
    """
    output.write('=' * len(template_name) + '\n')
    output.write(template_name + '\n')


def output_as_table(table, headers, output=sys.stdout, tablefmt='psql'):
    """
    Outputs the results in the desired format

    :table: a list of lists
    :headers: a list of strings
    :output: output destination (console=sys.stdout; testing=StringIO)
    :tablefmt: String (specific to the tabulate library)
    """
    output.write(tabulate(table, headers, tablefmt=tablefmt) + '\n')


def output_message(reason, output=sys.stdout):
    """
    Output a message to the console.

    :reason: Integer (see the dictionary below)
    :output: output destination (console=sys.stdout; testing=StringIO)
    """
    reasons = {
        1: 'No templates were found!',
        2: 'Only the Django Template Engine is currently supported!',
        3: 'Your templates are clean!'
    }
    output.write(reasons[reason] + '\n')


def update_dictionary(dictionary, key, value):
    """
    Add the key-value pair to the dictionary and return the dictionary.

    :dictionary: dict object
    :key: String (e.g. module name)
    :value: Integer (e.g. line number)
    :returns: dict object
    """
    if key not in dictionary:
        dictionary[key] = [value]
    else:
        # The same key can appear on multiple lines
        if value not in dictionary[key]:
            dictionary[key].append(value)

    return dictionary
