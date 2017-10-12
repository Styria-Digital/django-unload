#!/usr/bin/env python

import os

from setuptools import find_packages, setup

setup(
    name='django-unload',
    version='0.4',
    url="https://github.com/Styria-Digital/django-unload",
    author='Styria Digital Services',
    description='Remove unused custom Django template tags and filters',
    long_description=open(
            os.path.join(os.path.dirname(__file__), 'README.rst')
    ).read(),
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    keywords='django template tag filter',
    install_requires=[
        'django>=1.8,<2.0',
        'tabulate==0.7.5',
    ],
    extras_require={
        'dev': [
            'autopep8==1.3.3',
            'flake8==3.4.1',
            'ipdb==0.10.3',
            'isort==4.2.15'
        ],
        'test': [
            'coverage==4.4.1',
            'pytest==3.2.3',
            'pytest-cov==2.5.1',
            'pytest-django==3.1.2',
            'pytest-runner==2.12.1',
            'pytest-sugar==0.9.0',
            'tox==2.9.1'
        ],
        'docs': [
            'sphinx==1.6.4',
            'sphinx-rtd-theme==0.2.4'
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
