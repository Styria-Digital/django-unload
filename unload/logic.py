# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template.base import TemplateSyntaxError
from django.template.loader import get_template

from .base import Template
from .utils import open_template
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
        print filepath
        return

    engine = base_template.template.engine
    source = open_template(filepath=filepath,
                           encoding=engine.file_charset)

    template = Template(template_string=source, engine=engine, name=filepath)
