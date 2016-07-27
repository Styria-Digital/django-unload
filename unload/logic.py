# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

from tabulate import tabulate

from django.template.base import TemplateSyntaxError
from django.template.loader import get_template

from .base import Template
from .utils import get_contents
from .search import AppSearch, ProjectSearch


def find_unused_tags(app=None):
    """
    To be changed in the near future!
    """
    app_search = None
    project_search = None

    if app:
        app_search = AppSearch(app=app)
        process_app_templates(app_search=app_search)
    else:
        project_search = ProjectSearch()

        for template_path in project_search.project_templates:
            process_template(template_path)

        for app_search in project_search.app_templates:
            process_app_templates(app_search=app_search)


def process_app_templates(app_search):
    """
    To be changed in the near future!
    """
    for template_path in app_search.templates:
        process_template(template_path)


def process_template(filepath):
    """
    To be changed in the near future!
    """
    try:
        base_template = get_template(filepath)
    except TemplateSyntaxError as tse:
        return sys.stdout.write('Unable to open template: {}\n'.format(filepath))

    engine = base_template.template.engine
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
