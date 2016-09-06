# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os

from django.apps import apps
from django.conf import settings
from django.test import TestCase

from ..base import Template
from ..utils import get_contents


class TestBase(TestCase):

    @classmethod
    def setUpClass(cls):
        """
        The setUpClass is used because the templates paths are not changed in
        the following tests.
        """
        super(TestBase, cls).setUpClass()
        # Find directories with templates
        templates_dir = settings.TEMPLATES[0]['DIRS'][0]
        app = apps.get_app_config('app')
        app_templates = os.path.join(app.path, 'templates', 'app', 'templates')
        app_tags = os.path.join(app.path, 'templates', 'app', 'tags')
        # Save the path of each template for further testing
        cls.master_template = os.path.join(templates_dir, 'master.html')
        cls.tag_template = os.path.join(app_tags, 'tag_template.html')
        cls.double_loads = os.path.join(app_templates, 'double_loads.html')
        cls.with_tags = os.path.join(app_templates, 'with_tags.html')
        cls.without_tags = os.path.join(app_templates, 'without_tags.html')
        cls.from_syntax_with_tags = os.path.join(app_templates,
                                                 'from_syntax_with_tags.html')
        cls.from_syntax_without_tags = os.path.join(app_templates,
                                                    'from_syntax_without_tags.html')

    def test_get_tokens_master_template(self):
        master_template = Template(
            template_string=get_contents(self.master_template),
            name=self.master_template)

        block_token = False
        endblock_token = False

        for token in master_template.tokens:
            if token.token_type == 2:
                contents = token.split_contents()
                if contents[0] == 'block':
                    block_token = True
                elif contents[0] == 'endblock':
                    endblock_token = True

        self.assertTrue(block_token)
        self.assertTrue(endblock_token)

    def test_get_tokens_tag_template(self):
        # Test tag template
        tag_template = Template(
            template_string=get_contents(self.tag_template),
            name=self.tag_template)
        self.assertEqual(tag_template.tokens[1].contents, 'tag_name')

    def test_get_tokens_double_loads(self):
        # Test double loads
        double_loads = Template(
            template_string=get_contents(self.double_loads),
            name=self.double_loads)

        extends_token = False
        load_token = 0
        block_token = False
        endblock_token = False

        for token in double_loads.tokens:
            if token.token_type == 2:
                contents = token.split_contents()
                if contents[0] == 'extends':
                    extends_token = True
                elif contents[0] == 'load':
                    load_token += 1
                elif contents[0] == 'block':
                    block_token = True
                elif contents[0] == 'endblock':
                    endblock_token = True

        self.assertTrue(extends_token)
        self.assertEqual(2, load_token)
        self.assertTrue(block_token)
        self.assertTrue(endblock_token)

    def test_get_tokens_with_tags(self):
        with_tags = Template(
            template_string=get_contents(self.with_tags),
            name=self.with_tags)

        extends_token = False
        load_token = 0
        block_token = False
        endblock_token = False
        example_inclusion_tag_token = False
        example_simple_tag_token = False
        example_assignment_tag_token = False

        for token in with_tags.tokens:
            if token.token_type == 2:
                contents = token.split_contents()
                if contents[0] == 'extends':
                    extends_token = True
                elif contents[0] == 'load':
                    load_token += 1
                elif contents[0] == 'block':
                    block_token = True
                elif contents[0] == 'endblock':
                    endblock_token = True
                elif contents[0] == 'example_inclusion_tag':
                    example_inclusion_tag_token = True
                elif contents[0] == 'example_simple_tag':
                    example_simple_tag_token = True
                elif contents[0] == 'example_assignment_tag':
                    example_assignment_tag_token = True

        self.assertTrue(extends_token)
        self.assertEqual(1, load_token)
        self.assertTrue(block_token)
        self.assertTrue(endblock_token)
        self.assertTrue(example_inclusion_tag_token)
        self.assertTrue(example_simple_tag_token)
        self.assertTrue(example_assignment_tag_token)

    def test_get_tokens_from_syntax_with_tags(self):
        from_syntax_with_tags = Template(
            template_string=get_contents(self.from_syntax_with_tags),
            name=self.from_syntax_with_tags)

        extends_token = False
        load_token = 0
        block_token = False
        endblock_token = False
        example_inclusion_tag_token = False
        example_simple_tag_token = False
        example_assignment_tag_token = False

        for token in from_syntax_with_tags.tokens:
            if token.token_type == 2:
                contents = token.split_contents()
                if contents[0] == 'extends':
                    extends_token = True
                elif contents[0] == 'load' and contents[-2] == 'from':
                    load_token += 1
                elif contents[0] == 'block':
                    block_token = True
                elif contents[0] == 'endblock':
                    endblock_token = True
                elif contents[0] == 'example_inclusion_tag':
                    example_inclusion_tag_token = True
                elif contents[0] == 'example_simple_tag':
                    example_simple_tag_token = True
                elif contents[0] == 'example_assignment_tag':
                    example_assignment_tag_token = True

        self.assertTrue(extends_token)
        self.assertEqual(1, load_token)
        self.assertTrue(block_token)
        self.assertTrue(endblock_token)
        self.assertTrue(example_inclusion_tag_token)
        self.assertTrue(example_simple_tag_token)
        self.assertTrue(example_assignment_tag_token)

    def test_get_tokens_without_tags(self):
        # Test double loads
        without_tags = Template(
            template_string=get_contents(self.without_tags),
            name=self.without_tags)

        extends_token = False
        load_token = 0
        block_token = False
        endblock_token = False

        for token in without_tags.tokens:
            if token.token_type == 2:
                contents = token.split_contents()
                if contents[0] == 'extends':
                    extends_token = True
                elif contents[0] == 'load':
                    load_token += 1
                elif contents[0] == 'block':
                    block_token = True
                elif contents[0] == 'endblock':
                    endblock_token = True

        self.assertTrue(extends_token)
        self.assertEqual(1, load_token)
        self.assertTrue(block_token)
        self.assertTrue(endblock_token)

    def test_get_tokens_from_syntax_without_tags(self):
        # Test double loads
        from_syntax_without_tags = Template(
            template_string=get_contents(self.from_syntax_without_tags),
            name=self.from_syntax_without_tags)

        extends_token = False
        load_token = 0
        block_token = False
        endblock_token = False

        for token in from_syntax_without_tags.tokens:
            if token.token_type == 2:
                contents = token.split_contents()
                if contents[0] == 'extends':
                    extends_token = True
                elif contents[0] == 'load' and contents[-2] == 'from':
                    load_token += 1
                elif contents[0] == 'block':
                    block_token = True
                elif contents[0] == 'endblock':
                    endblock_token = True

        self.assertTrue(extends_token)
        self.assertEqual(1, load_token)
        self.assertTrue(block_token)
        self.assertTrue(endblock_token)

    def test_parse_load_block(self):

        master_template = Template(
            template_string=get_contents(self.master_template),
            name=self.master_template)
        self.assertEqual(master_template.loaded_modules, {})
        self.assertEqual(master_template.loaded_members, {})

        tag_template = Template(
            template_string=get_contents(self.tag_template),
            name=self.tag_template)
        self.assertEqual(tag_template.loaded_modules, {})
        self.assertEqual(tag_template.loaded_members, {})

        double_loads = Template(
            template_string=get_contents(self.double_loads),
            name=self.double_loads)
        self.assertEqual(double_loads.loaded_modules,
                         {'app_tags': [2, 3]})
        self.assertEqual(double_loads.loaded_members, {})

        with_tags = Template(
            template_string=get_contents(self.with_tags),
            name=self.with_tags)
        self.assertEqual(with_tags.loaded_modules,
                         {'app_tags': [2]})
        self.assertEqual(with_tags.loaded_members, {})

        from_syntax_with_tags = Template(
            template_string=get_contents(self.from_syntax_with_tags),
            name=self.from_syntax_with_tags)
        self.assertEqual(from_syntax_with_tags.loaded_modules,
                         {'app_tags': [2]})
        self.assertEqual(from_syntax_with_tags.loaded_members,
                         {
                            'example_assignment_tag': [2],
                            'example_inclusion_tag': [2],
                            'example_simple_tag': [2],
                            'plus': [2]
                         })

        without_tags = Template(
            template_string=get_contents(self.without_tags),
            name=self.without_tags)
        self.assertEqual(without_tags.loaded_modules,
                         {'app_tags': [2]})
        self.assertEqual(without_tags.loaded_members, {})

        from_syntax_without_tags = Template(
            template_string=get_contents(self.from_syntax_without_tags),
            name=self.from_syntax_without_tags)
        self.assertEqual(from_syntax_without_tags.loaded_modules,
                         {'app_tags': [2]})
        self.assertEqual(from_syntax_without_tags.loaded_members,
                         {
                            'example_simple_tag': [2],
                            'plus': [2]
                         })


