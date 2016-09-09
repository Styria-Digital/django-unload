#!/usr/bin/env python

import os
from setuptools import find_packages, setup

setup(
    name='django-unload',
    version='0.3.1',
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
        'django>=1.8, <1.9',
        'tabulate==0.7.5',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
