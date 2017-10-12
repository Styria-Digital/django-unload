# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from django.conf import settings
from django.test import TestCase

from unload.logic import process_template, list_unnecessary_loads
from unload.utils import get_djangotemplates_engines, get_app


class TestLogic(TestCase):

    def test_process_template(self):
        templates_dir = settings.TEMPLATES[0]['DIRS'][0]
        dt_engines = get_djangotemplates_engines()
        app = get_app('app')
        app_path = os.path.join(app.path, 'templates')

        master_template = os.path.join(templates_dir, 'master.html')
        status = process_template(master_template, dt_engines[0].engine)
        self.assertFalse(status)

        tag_template = os.path.join(
            app_path, 'app', 'tags', 'tag_template.html')
        status = process_template(tag_template, dt_engines[0].engine)
        self.assertFalse(status)

        double_loads = os.path.join(
            app_path, 'app', 'templates', 'double_loads.html')
        status = process_template(double_loads, dt_engines[0].engine)
        self.assertTrue(status)

        double_member_load = os.path.join(
            app_path, 'app', 'templates', 'double_member_load.html')
        status = process_template(double_member_load, dt_engines[0].engine)
        self.assertTrue(status)

        from_syntax_with_tags = os.path.join(app_path, 'app', 'templates',
                                             'from_syntax_with_tags.html')
        status = process_template(from_syntax_with_tags, dt_engines[0].engine)
        self.assertFalse(status)

        from_syntax_without_tags = os.path.join(
            app_path, 'app', 'templates', 'from_syntax_without_tags.html')
        status = process_template(from_syntax_without_tags,
                                  dt_engines[0].engine)
        self.assertTrue(status)

        only_filter = os.path.join(
            app_path, 'app', 'templates', 'only_filter.html')
        status = process_template(only_filter, dt_engines[0].engine)
        self.assertFalse(status)

        with_tags = os.path.join(
            app_path, 'app', 'templates', 'with_tags.html')
        status = process_template(with_tags, dt_engines[0].engine)
        self.assertFalse(status)

        without_tags = os.path.join(
            app_path, 'app', 'templates', 'without_tags.html')
        status = process_template(without_tags, dt_engines[0].engine)
        self.assertTrue(status)

    def test_list_unnecessary_loads(self):
        status = list_unnecessary_loads()
        self.assertTrue(status)

        status = list_unnecessary_loads('app')
        self.assertTrue(status)

        status = list_unnecessary_loads('empty')
        self.assertFalse(status)

        status = list_unnecessary_loads('clean')
        self.assertFalse(status)
