#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
import subprocess
from setuptools import setup

# We expect tox to set GITDIR
if 'GITDIR' in os.environ:
    # We're being run from our tox.ini
    git_version = subprocess.check_output(
        ['git', '-C', os.environ['GITDIR'], 'describe', '--dirty']).decode('utf-8').strip()
else:
    # Not run from tox.ini, just do our best
    git_version = "UNKNOWN"


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-avoidance',
    version=git_version,
    author='Johan Walles',
    author_email='johan.walles@gmail.com',
    maintainer='Johan Walles',
    maintainer_email='johan.walles@gmail.com',
    license='MIT',
    url='https://github.com/walles/pytest-avoidance',
    description='Makes pytest skip tests that don not need rerunning',
    long_description=read('README.rst'),
    py_modules=['pytest_avoidance'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*',
    install_requires=['pytest>=3.5.0', 'coverage==4.5.2'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'avoidance = pytest_avoidance',
        ],
    },
)
