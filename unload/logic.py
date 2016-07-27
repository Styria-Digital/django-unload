# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

from tabulate import tabulate

from django.template.base import TemplateSyntaxError
from django.template.loader import get_template
from pprint import pprint
from django.template.backends.django import DjangoTemplates
from django.conf import settings

from .base import Template
from .utils import get_contents, get_package_locations, get_template_files
from .search import AppSearch, ProjectSearch


def find_unused_tags(app=None):
    """
    To be changed in the near future!
    """
    template_settings = settings.TEMPLATES
    for params in template_settings:
        backend = params.pop('BACKEND')

        if backend == 'django.template.backends.django.DjangoTemplates':
            templates = []

            params['NAME'] = 'django'
            django_templates = DjangoTemplates(params=params)

            # Get the locations of installed packages
            pkg_locations = get_package_locations()
            # Get template directories located within the project
            for directory in django_templates.template_dirs:
                within_project = True
                for location in pkg_locations:
                    if directory.startswith(location):
                        within_project = False
                        break
                # Only one app needs to be scanned
                if app:
                    if not directory.startswith(app.path):
                        continue
                # Get the template files from the directory
                if within_project:
                    templates += get_template_files(directory)

        if templates:
            for template in templates:
                process_template(template, django_templates.engine)


def process_template(filepath, engine):
    """
    To be changed in the near future!
    """

    source = get_contents(filepath=filepath,
                          encoding=engine.file_charset)

    template = Template(template_string=source, engine=engine, name=filepath)
    duplicate_table, duplicate_headers = template.list_duplicates()
    unutilized_table, unutilized_headers = template.list_unutilized_items()
    add_newline = False
    if duplicate_table or unutilized_table:
        sys.stdout.write(template.name + '\n')
        add_newline = True
    if duplicate_table:
        sys.stdout.write(tabulate(duplicate_table, duplicate_headers,
                                  tablefmt='psql') + '\n')
    if unutilized_table:
        sys.stdout.write(tabulate(unutilized_table, unutilized_headers,
                                  tablefmt='psql') + '\n')

    if add_newline:
        sys.stdout.write('\n')
