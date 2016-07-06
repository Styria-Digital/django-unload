# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from django.template.loaders.app_directories import get_app_template_dirs


class SearchApp(object):
    def __init__(self, app, *args, **kwargs):
        self.app = app

    def find_unused_tags(self):
        templates = self.get_all_templates()

    def get_all_templates(self):
        template_dirs = self.get_all_template_dirs()

        templates = []
        for template_dir in template_dirs:
            for dirpath, dirnames, filenames in os.walk(template_dir):
                for filename in filenames:
                    if filename.endswith('.html'):
                        templates.append(os.path.join(dirpath, filename))

        return templates

    def get_all_template_dirs(self):
        app_temp_dirs = get_app_template_dirs('templates')
        template_dirs = [d for d in app_temp_dirs if self.app.path in d]
        return template_dirs
