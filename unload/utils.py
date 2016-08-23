# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import io
import os
from mimetypes import guess_type

from pip import get_installed_distributions

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
            maintype, subtype = filetype[0].split('/')
            if maintype == 'text':
                templates.append(os.path.join(dirpath, filename))

    return templates
