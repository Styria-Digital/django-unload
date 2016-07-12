# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
from mimetypes import guess_type

from django.apps import apps
from django.conf import settings
from django.template.loaders.app_directories import get_app_template_dirs


class BaseSearch(object):

    def get_templates(self, template_dir):
        """
        Get absolute paths to the templates located in the directory. All text
        files are considered to be templates.

        :template_dir: the absolute path to the template directory
        :returns: a list of absolute paths to the templates located in the
                  directory
        """

        templates = []

        # No template directories were found
        if not template_dir:
            return templates

        for dirpath, dirnames, filenames in os.walk(template_dir):
            for filename in filenames:
                filetype = guess_type(filename)
                maintype, subtype = filetype[0].split('/')
                if maintype == 'text':
                    templates.append(os.path.join(dirpath, filename))

        return templates

    def get_app_template_dir(self, app_config):
        """
        Get the absolute path to the app's template directory.

        :app_config: AppConfig object
        :returns: full path to the app's template directory
        """
        app_temp_dirs = get_app_template_dirs('templates')
        for d in app_temp_dirs:
            if app_config.path in d:
                return d


class ProjectSearch(BaseSearch):
    """
    Find all templates in the project.
    """

    def __init__(self):
        super(ProjectSearch, self).__init__()
        self.project_templates = self.get_project_templates()
        self.app_templates = self.get_app_templates()

    def get_project_templates(self):
        """
        Get all templates from the directories specified in the TEMPLATES
        variable in settings.py.

        :returns: a list of full paths to templates
        """
        templates = []
        for templates_setting in settings.TEMPLATES:
            for directory in templates_setting['DIRS']:
                templates += self.get_templates(template_dir=directory)

        return templates

    def get_app_templates(self):
        """
        Get all templates that belong to apps installed in the project.

        :returns: a list of AppSearch objects
        """
        app_configs = apps.get_app_configs()

        app_searches = []
        for app in app_configs:
            app_search = AppSearch(app)
            if app_search.templates:
                app_searches.append(app_search)

        return app_searches


class AppSearch(BaseSearch):
    """
    Find all templates that belong to a certain app.
    """

    def __init__(self, app):
        super(AppSearch, self).__init__()
        self.app = app
        self.templates = self.get_templates(self.get_app_template_dir(app))
