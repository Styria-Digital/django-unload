# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.apps import apps


def get_app(app_name):
    """Get the app object"""
    try:
        app = apps.get_app_config(app_name)
    except LookupError as le:
        raise le

    return app
