# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from os import getcwdu
from os.path import isfile, join
from sys import version_info

from django.apps import apps
from django.conf import settings


def get_project_path():
    """Get the project path"""

    # Get the project path from the project's settings.py
    if hasattr(settings, 'BASE_DIR'):
        path = settings.BASE_DIR
    elif hasattr(settings, 'PROJECT_PATH'):
        path = settings.PROJECT_PATH
    elif hasattr(settings, 'PROJECT_ROOT'):
        path = settings.PROJECT_ROOT
    # Get the current working directory
    else:
        path = getcwdu()

    # manage.py should be in the project's root directory
    if not isfile(join(path, 'manage.py')):
        msg = "manage.py not found in the project's root directory"
        version_major = version_info[0]
        if version_major == 3:
            raise FileNotFoundError(msg)
        else:
            raise EnvironmentError(msg)
    else:
        return path


def get_app(app_name):
    """Get the app object"""
    try:
        app = apps.get_app_config(app_name)
    except LookupError as le:
        raise le

    return app
