# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import io

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


def open_template(filepath, encoding='UTF-8'):
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
