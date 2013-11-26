#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='song_comparison',
    version='0.1.0',
    description='This toolbox allows audio file conversion, audio feature extraction, distance calculation and graph visualization',
    long_description=readme + '\n\n' + history,
    author='Jonathan',
    author_email='j.wermelinger@gmx.ch',
    url='https://github.com/jw1123/song_comparison',
    packages=[
        'song_comparison',
    ],
    package_dir={'song_comparison': 'song_comparison'},
    include_package_data=True,
    install_requires=[
    ],
    license="BSD",
    zip_safe=False,
    keywords='song_comparison',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    test_suite='tests',
)