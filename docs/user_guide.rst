User Guide
**********

*django-unload* is used as a command line tool. It can either be used to scan all template files in the project or the templates in the specified Django app.

In order for the plugin to function properly, all third-pary packages located in the *INSTALLED_APPS* setting (e.g. django-debug-toolbar) should be installed using *pip*. *django-unload* uses *pip* to differentiate between the project's templates and the templates of packages located in the installed apps (e.g. admin templates).

Scan the project
================

To scan all template files in the project, type:

    ``$ python manage.py find_unnecessary_loads``.

Scan an app
===========

To scan a specific app, type:

    ``$ python manage.py find_unnecessary_loads --app <app_name>``.


Output
======

The output is sent to the console. Although all template files are scanned, only templates with issues and the issues in question are displayed. The issues are displayed in two tables:

1. The first table points to duplicate loads;

    +--------------------+------------------------+---------------+
    | Duplicate module   |   Duplicate tag/filter | Line number   |
    +====================+========================+===============+
    | some_module        |                        | 10, 23        |
    +--------------------+------------------------+---------------+
    | some_other_module  | some_tag               | 14, 47        |
    +--------------------+------------------------+---------------+


2. The second table simply lists unutilized modules, tags and filters;

    +---------------------------+-------------------------+
    | Unutilized module         |   Unutilized tag/filter |
    +===========================+=========================+
    | some_module               | some_tag                |
    +---------------------------+-------------------------+
    | some_other_module         | some_filter             |
    +---------------------------+-------------------------+


**WARNING:** If you get a *TemplateSyntaxError*, the template in question is probably outdated and/or has not been used in a while.

Example Output
==============


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
