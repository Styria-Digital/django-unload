# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO


class TestCommand(TestCase):

    def test_find_unnecessary_loads(self):
        output = StringIO()
        call_command('find_unnecessary_loads', stdout=output)
        self.assertEqual('Has issues: True', output.getvalue().strip())

        output = StringIO()
        call_command('find_unnecessary_loads', app='app', stdout=output)
        self.assertEqual('Has issues: True', output.getvalue().strip())

        output = StringIO()
        call_command('find_unnecessary_loads', app='clean', stdout=output)
        self.assertEqual('Has issues: False', output.getvalue().strip())

        output = StringIO()
        call_command('find_unnecessary_loads', app='empty', stdout=output)
        self.assertEqual('Has issues: False', output.getvalue().strip())
