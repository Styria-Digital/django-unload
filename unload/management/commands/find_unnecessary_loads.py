# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from distutils.version import StrictVersion

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _

from ...logic import list_unnecessary_loads
from ...settings import DJANGO_VERSION

if StrictVersion(DJANGO_VERSION) < StrictVersion('1.8'):
    raise NotImplementedError('Minimal supported version of Django: 1.8')
elif StrictVersion(DJANGO_VERSION) > StrictVersion('1.9'):
    raise NotImplementedError('Django version {} is not yet supported'.format(
                                DJANGO_VERSION))


class Command(BaseCommand):
    help = 'List unutilized templatetag libraries'

    def add_arguments(self, parser):
        parser.add_argument(
            '-a', '--app', nargs='?', type=str, action='store', required=False,
            help=_('The label of the application that needs to be scanned'))

    def handle(self, *args, **options):
        # Find the app
        app_label = options.get('app', None)
        self.stdout.write(
            'Has issues: {}'.format(str(list_unnecessary_loads(app_label))))
