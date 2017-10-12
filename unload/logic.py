# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

from .base import Template
from .utils import (get_app,
                    get_contents,
                    get_package_locations,
                    get_djangotemplates_engines,
                    output_as_table,
                    output_template_name,
                    output_message,
                    get_templates)


def list_unnecessary_loads(app_label=None):
    """
    Scan the project directory tree for template files and process each and
    every one of them.

    :app_label: String; app label supplied by the user

    :returns: None (outputs to the console)
    """
    if app_label:
        app = get_app(app_label)
    else:
        app = None

    dt_engines = get_djangotemplates_engines()

    for dt_engine in dt_engines:
        has_issues = False
        templates = []
        # Get the locations of installed packages
        pkg_locations = get_package_locations()
        # Get template directories located within the project
        for directory in dt_engine.template_dirs:
            templates += get_templates(directory, pkg_locations, app)

        if templates:
            for template in templates:
                status = process_template(template, dt_engine.engine)
                if status:
                    has_issues = status
            if not has_issues:
                output_message(reason=3)
        else:
            output_message(reason=1)

    return has_issues


def process_template(filepath, engine):
    """
    Process the specified template

    :filepath: String; the absolute path to the template file
    :engine: Engine object

    :returns: Boolean (does the template file have issues or not)
    """
    has_issues = False
    # Get the template's contents
    source = get_contents(filepath=filepath,
                          encoding=engine.file_charset)
    # Create and process the template
    template = Template(template_string=source, engine=engine, name=filepath)
    # Prepare output
    duplicate_table, duplicate_headers = template.list_duplicates()
    unutilized_table, unutilized_headers = template.list_unutilized_items()
    if duplicate_table or unutilized_table:
        output_template_name(template_name=template.name, output=sys.stdout)
        has_issues = True
    # Display the table that contains duplicate loads
    if duplicate_table:
        output_as_table(table=duplicate_table,
                        headers=duplicate_headers, output=sys.stdout)
    # Display the table that contains unutilized loads
    if unutilized_table:
        output_as_table(table=unutilized_table,
                        headers=unutilized_headers, output=sys.stdout)

    return has_issues
