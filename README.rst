README
======

**Work in progress!**

Requirements
------------

* Python 2.7+, 3.3+
* Django 1.8 (1.9 support will be added later)


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

Output
------
The output is sent to the console. Although all template files are scanned, only templates with issues and the issues in question are displayed. The issues are displayed in two tables:

1. The first table points to duplicate loads which can sometimes be identical. The second table

2. The second table simply lists unutilized modules, tags and filters.

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
| some_other_module         | some_filter             |
+---------------------------+-------------------------+
