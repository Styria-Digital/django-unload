# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import io

from django.apps import apps


def get_app(app_name):
    """
    Get the app object.

    :returns: AppConfig
    """
    try:
        app = apps.get_app_config(app_name)
    except LookupError as le:
        raise le

    return app


def open_template(filepath, encoding='UTF-8'):
    """
    Read the contents of the template file.

    :filepath: absolute path to the template file
    :returns: contents of the template as a string
    """
    with io.open(filepath, encoding=encoding) as fp:
        return fp.read()
