#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import io
from os.path import join, dirname
from setuptools import setup


def get_version(package):
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search('__version__ = [\'"]([^\'"]+)[\'"]', init_py).group(1)


def get_packages(package):
    return [dirpath for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}

# use io.open until python2.7 support is dropped
with io.open("README.md", encoding="utf8") as f:
    readme = f.read()

with io.open("CHANGELOG.md", encoding="utf8") as f:
    changelog = f.read()


setup(
    name='jalali-django-admin-rangefilter',
    version=get_version('rangefilter2'),
    url='https://github.com/nshayanfar/jalali-django-admin-rangefilter',
    license='MIT',
    description='jalali-django-admin-rangefilter app, add the filter by a custom date range on the admin UI.',
    long_description=readme + changelog,
    long_description_content_type="text/markdown",
    author='Nima Shayanfar',
    author_email='nshayanfar@gmail.com',
    packages=['rangefilter2'],
    package_data=get_package_data('rangefilter2'),
    # include_package_data=True,
    setup_requires=['persiantools'],
    install_requires=['persiantools'],
    python_requires='>=3.5',
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Utilities',
    ],
)
