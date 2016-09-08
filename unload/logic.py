# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import sys

from .base import Template
from .utils import (get_contents, get_package_locations, get_template_files,
                    get_djangotemplates_engines, output_as_table,
                    output_template_name, output_message)


def list_unnecessary_loads(app=None):
    """
    Scan the project directory tree for template files and process each and
    every one of them.

    :app: AppConfig object

    :returns: None (outputs to the console)
    """

    dt_engines = get_djangotemplates_engines()

    for dt_engine in dt_engines:
        templates = []
        # Get the locations of installed packages
        pkg_locations = get_package_locations()
        # Get template directories located within the project
        for directory in dt_engine.template_dirs:
            within_project = True
            for location in pkg_locations:
                if directory.startswith(location):
                    within_project = False
                    break
            # Get the template files from the directory
            if within_project:
                # Only one app needs to be scanned
                if app:
                    if directory.startswith(app.path):
                        templates = get_template_files(directory)
                        break
                else:
                    templates += get_template_files(directory)

        if templates:
            has_issues = False
            for template in templates:
                status = process_template(template, dt_engine.engine)
                if status:
                    has_issues = status
            if not has_issues:
                output_message(reason=3)
        else:
            output_message(reason=1)


def process_template(filepath, engine):
    """
    Process the specified template

    :filepath: String; the absolute path to the template file
    :engine: Engine object

    :returns: Boolean (does the template file have issues or not)
    """
    has_issues = False
    add_newline = False
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
        add_newline = True
        has_issues = True
    # Display the table that contains duplicate loads
    if duplicate_table:
        output_as_table(table=duplicate_table,
                        headers=duplicate_headers, output=sys.stdout)
    # Display the table that contains unutilized loads
    if unutilized_table:
        output_as_table(table=unutilized_table,
                        headers=unutilized_headers, output=sys.stdout)

    if add_newline:
        sys.stdout.write('\n')

    return has_issues
