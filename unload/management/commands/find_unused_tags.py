# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from os import getcwdu
from os.path import isfile, join
from sys import version_info

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _


class Command(BaseCommand):
    help = 'List unused template tags'

    def add_arguments(self, parser):
        parser.add_argument(
            '-a', '--app', nargs='?', type=str, action='store', required=False,
            help=_('The name of the application that needs to be scanned'))

    def handle(self, *args, **options):
        # Get the current working directory
        cwd = getcwdu()

        # Must be called from the Django project's directory
        if not isfile(join(cwd, 'manage.py')):
            msg = 'manage.py not found in the current working directory'
            version_major = version_info[0]
            if version_major == 3:
                raise FileNotFoundError(msg)
            else:
                raise EnvironmentError(msg)

        app = options.get('app')
