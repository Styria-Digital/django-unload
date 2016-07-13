# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.template.loader import get_template

from .base import Template
from .utils import open_template
from .search import AppSearch, ProjectSearch


def find_unused_tags(app=None):

    app_search = None
    project_search = None

    if app:
        app_search = AppSearch(app=app)
    else:
        project_search = ProjectSearch()

    if project_search:
        for template_path in project_search.project_templates:
            process_template(template_path)
            import ipdb; ipdb.set_trace()


def process_template(filepath):
    base_template = get_template(filepath)
    engine = base_template.template.engine
    source = open_template(filepath=filepath,
                           encoding=engine.file_charset)

    template = Template(template_string=source, engine=engine)
