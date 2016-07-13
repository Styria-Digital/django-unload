# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from ...search import ProjectSearch, AppSearch
from ...utils import get_app


class Command(BaseCommand):
    help = 'List unused template tags'

    def add_arguments(self, parser):
        parser.add_argument(
            '-a', '--app', nargs='?', type=str, action='store', required=False,
            help=_('The name of the application that needs to be scanned'))

    def handle(self, *args, **options):

        app_name = options.get('app')
        if app_name:
            app = get_app(app_name)
            AppSearch(app=app)
        else:
            ProjectSearch()
