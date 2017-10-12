# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import sys

from django.apps.config import AppConfig
from django.conf import settings
from django.test import TestCase
from django.test.utils import override_settings

from unload.utils import (get_app,
                          get_contents,
                          get_djangotemplates_engines,
                          get_filters,
                          get_package_locations,
                          get_template_files,
                          get_templates,
                          get_templatetag_members,
                          output_as_table,
                          output_message,
                          output_template_name,
                          update_dictionary)

PYTHON_VERSION = sys.version_info

if PYTHON_VERSION.major == 2:
    from StringIO import StringIO
elif PYTHON_VERSION.major == 3:
    from io import StringIO


class TestUtils(TestCase):

    def test_get_app(self):
        """
        Tests the get_app function.
        """
        # Try to fetch a non-existing app
        with self.assertRaises(LookupError):
            get_app('dummy_app')
        # Fetch the demo app and evaluate it
        app = get_app('app')
        self.assertEqual(app.label, 'app')
        self.assertIsInstance(app, AppConfig)

    def test_get_templates(self):
        templates_dir = settings.TEMPLATES[0]['DIRS'][0]
        empty_dir = templates_dir.replace('templates', 'empty_dir')
        master_template = os.path.join(templates_dir, 'master.html')
        pkg_locations = get_package_locations()
        app = get_app('app')
        app_path = os.path.join(app.path, 'templates')
        # Test templates directory
        templates = get_templates(templates_dir, pkg_locations)
        self.assertIn(master_template, templates)
        # Test empty directory
        templates = get_templates(empty_dir, pkg_locations)
        self.assertEqual(templates, [])
        # Test app directory
        templates = get_templates(app_path, pkg_locations, app)
        self.assertEqual(8, len(templates))
        self.assertIn(os.path.join(app_path, 'app', 'tags',
                                   'tag_template.html'), templates)
        self.assertIn(os.path.join(app_path, 'app', 'templates',
                                   'double_loads.html'), templates)
        self.assertIn(os.path.join(app_path, 'app', 'templates',
                                   'double_member_load.html'), templates)
        self.assertIn(os.path.join(app_path, 'app', 'templates',
                                   'from_syntax_with_tags.html'), templates)
        self.assertIn(os.path.join(app_path, 'app', 'templates',
                                   'from_syntax_without_tags.html'), templates)
        self.assertIn(os.path.join(app_path, 'app', 'templates',
                                   'only_filter.html'), templates)
        self.assertIn(os.path.join(app_path, 'app', 'templates',
                                   'with_tags.html'), templates)
        self.assertIn(os.path.join(app_path, 'app', 'templates',
                                   'without_tags.html'), templates)
        # Test external directory
        templates = get_templates(pkg_locations[0], pkg_locations)
        self.assertEqual(templates, [])

    def test_get_contents(self):
        """
        Test the get_contents function on the master.html template. Avoid
        using the DjangoTemplates class due to frequent changes between
        versions.
        """
        templates_dir = settings.TEMPLATES[0]['DIRS'][0]
        master_html = templates_dir + '/master.html'
        contents = get_contents(filepath=master_html)
        self.assertIn('DOCTYPE', contents)
        self.assertIn('html', contents)
        self.assertIn('head', contents)
        self.assertIn('title', contents)
        self.assertIn('body', contents)
        self.assertIn('{% block title %}', contents)
        self.assertIn('{% block body %}', contents)

    def test_get_djangotemplates_engines(self):
        dt_engines = get_djangotemplates_engines()
        self.assertEqual(1, len(dt_engines))
        engine = dt_engines[0]
        self.assertEqual('django', engine.name)
        self.assertTrue(engine.app_dirs)
        self.assertEqual(1, len(engine.dirs))
        self.assertTrue(engine.dirs[0].endswith('/demo/templates'))

    @override_settings(TEMPLATES=[{'BACKEND': 'foo.bar.Baz'}])
    def test_other_template_engines(self):
        dt_engines = get_djangotemplates_engines()
        self.assertEqual(0, len(dt_engines))

    def test_get_filters(self):
        token_content = '{{ somevariable|cut:"0" }}'
        filters = get_filters(token_content)
        self.assertIn('cut', filters)
        self.assertNotIn('somevariable', filters)
        self.assertNotIn('0', filters)

    def test_get_package_locations(self):
        """
        Get the directory path containing the installed 3rd party packages (in
        this instance the site-packages directory located in .tox/).
        """
        end_of_path = ('/lib/python{0}.{1}/site-packages').format(
            PYTHON_VERSION.major, PYTHON_VERSION.minor)
        pkg_locations = get_package_locations()
        for location in pkg_locations:
            self.assertTrue(location.endswith(end_of_path))

    def test_get_template_files(self):
        """
        Test the location of the master.html template file.
        """
        templates_dir = settings.TEMPLATES[0]['DIRS'][0]
        master_html = os.path.join(templates_dir, 'master.html')
        template_files = get_template_files(templates_dir)
        self.assertIn(master_html, template_files)

    def test_get_templatetag_members(self):
        output = StringIO()
        template_name = 'example.html'
        loaded_modules = {'app_tags': [1]}
        tags, filters = get_templatetag_members(template_name,
                                                loaded_modules, output)
        self.assertEqual(1, len(tags.keys()))
        self.assertIn('app_tags', tags.keys())
        self.assertIn('example_simple_tag', tags['app_tags'])
        self.assertIn('example_inclusion_tag', tags['app_tags'])
        self.assertIn('example_assignment_tag', tags['app_tags'])
        self.assertIn('app_tags', filters.keys())
        self.assertIn('plus', filters['app_tags'])
        self.assertEqual('', output.getvalue())

        # Add a non existing templatetag modules
        loaded_modules['some_lib'] = [1]
        tags, filters = get_templatetag_members(template_name,
                                                loaded_modules, output)
        self.assertEqual(output.getvalue().strip(),
                         ('Unable to locate the loaded library! '
                          'Library: some_lib; Template: example.html'))

    def test_start_output(self):
        """
        Test output to console.
        """
        output = StringIO()
        template_name = 'example.html'
        output_template_name(template_name=template_name, output=output)
        self.assertIn(template_name + '\n', output.getvalue())

    def test_output_as_table(self):
        """
        Test the output of results.

        The examples were taken from: https://pypi.python.org/pypi/tabulate
        """
        output = StringIO()
        table = [["spam", 42], ["eggs", 451], ["bacon", 0]]
        headers = ["item", "qty"]
        output_as_table(table=table, headers=headers, output=output)
        for header in headers:
            self.assertIn(header, output.getvalue())
        for row in table:
            for value in row:
                self.assertIn(str(value), output.getvalue())

    def test_output_message(self):
        output = StringIO()
        output_message(1, output)
        self.assertEqual(output.getvalue().strip(), 'No templates were found!')

        output = StringIO()
        output_message(2, output)
        self.assertEqual(output.getvalue().strip(),
                         ('Only the Django Template Engine is currently '
                          'supported!'))

        output = StringIO()
        output_message(3, output)
        self.assertEqual(output.getvalue().strip(),
                         'Your templates are clean!')

    def test_update_dictionary(self):
        dictionary = {}
        # Add new data
        dictionary = update_dictionary(dictionary=dictionary,
                                       key='module', value=1)
        self.assertIn('module', dictionary.keys())
        self.assertEqual(1, len(dictionary.keys()))
        self.assertEqual([1], dictionary.get('module'))
        # Repeat
        dictionary = update_dictionary(dictionary=dictionary,
                                       key='module', value=1)
        self.assertIn('module', dictionary.keys())
        self.assertEqual(1, len(dictionary.keys()))
        self.assertEqual([1], dictionary.get('module'))
        # Add new line number
        dictionary = update_dictionary(dictionary=dictionary,
                                       key='module', value=2)
        self.assertIn('module', dictionary.keys())
        self.assertEqual(1, len(dictionary.keys()))
        self.assertEqual([1, 2], dictionary.get('module'))
