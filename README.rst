README
======

.. image:: https://travis-ci.org/Styria-Digital/django-unload.svg?branch=master
    :target: https://travis-ci.org/Styria-Digital/django-unload

.. image:: https://coveralls.io/repos/github/Styria-Digital/django-unload/badge.svg?branch=master
    :target: https://coveralls.io/github/Styria-Digital/django-unload?branch=master

.. image:: https://img.shields.io/pypi/v/django-unload.svg
    :target: https://pypi.python.org/pypi/django-unload
    :alt: Version


Requirements
------------

* Python 2.7+, 3.4+
* Django 1.8 (1.9 support will be added later)
* Tabulate


Installation
------------
To install the package, type:

    ``$ pip install django-unload``

Setup
-----

Ensure that ``'unload'`` is in your project's ``INSTALLED_APPS``::

   INSTALLED_APPS = [
       ...
       'unload',
       ...
   ]

Usage
-----
The plugin is used as a command line tool. It can either be used to scan all template files in the project or the templates in the specified Django app.

Scan all template files in the project: ``$ python manage.py find_unnecessary_loads``.

Scan all template files in the specified app: ``$ python manage.py find_unnecessary_loads --app <app_name>``.

**Warning**

1. The assumption is that all your 3rd party packages located in the *INSTALLED_APPS* setting (e.g. django-debug-toolbar) are installed using *pip*. The plugin uses *pip* to differentiate the project's templates from the templates located in the installed apps;

2. If you get a *TemplateSyntaxError*, the template in question is probably outdated and/or has not been used in a while;

Output
------
The output is sent to the console. Although all template files are scanned, only templates with issues and the issues in question are displayed. The issues are displayed in two tables:

1. The first table points to duplicate loads;

2. The second table simply lists unutilized modules, tags and filters;

Example
-------
/path/to/template.html

+--------------------+------------------------+---------------+
| Duplicate module   |   Duplicate tag/filter | Line number   |
+====================+========================+===============+
| some_module        |                        | 10, 23        |
+--------------------+------------------------+---------------+
| some_other_module  | some_tag               | 14, 47        |
+--------------------+------------------------+---------------+

+---------------------------+-------------------------+
| Unutilized module         |   Unutilized tag/filter |
+===========================+=========================+
| some_module               | some_tag                |
+---------------------------+-------------------------+
| some_other_module         | some_filter             |
+---------------------------+-------------------------+
