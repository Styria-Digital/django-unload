Installation
************

Requirements
============

* Python 2.7+, 3.4+
* Django 1.8 (1.9 support will be added later)
* Tabulate

Installation
============

To install the package, type:

    ``$ pip install django-unload``

Setup
=====

Ensure that ``'unload'`` is in your project's ``INSTALLED_APPS``::

   INSTALLED_APPS = [
       ...
       'unload',
       ...
   ]

Development and testing
-----------------------

Contributions are always welcome. Once you've forked and cloned the repo, install the development and testing requirements:

``$ pip install -e .[dev,test]``

To make sure everything is installed correctly, run the test suite using ``pytest`` or ``tox``:

``$ pytest``

or

``$ tox``
