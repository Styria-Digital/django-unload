# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

from django import VERSION as DJANGO_VERSION
from django.apps.config import AppConfig
from django.conf import settings
from django.test import TestCase

from ..utils import (get_app, get_contents, get_filters, get_package_locations,
                     get_template_files, output_template_name, output_as_table,
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
        end_of_path = ('.tox/py{0}{1}-django{2}{3}/lib/'
                       'python{0}.{1}/site-packages').format(
            PYTHON_VERSION.major, PYTHON_VERSION.minor,
            DJANGO_VERSION[0], DJANGO_VERSION[1])
        pkg_locations = get_package_locations()
        for location in pkg_locations:
            self.assertTrue(location.endswith(end_of_path))

    def test_get_template_files(self):
        """
        Test the location of the master.html template file.
        """
        templates_dir = settings.TEMPLATES[0]['DIRS'][0]
        master_html = templates_dir + '/master.html'
        template_files = get_template_files(templates_dir)
        self.assertIn(master_html, template_files)

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
