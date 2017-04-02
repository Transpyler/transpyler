# -*- coding: utf-8 -*-
#
# This file were created by Python Boilerplate. Use boilerplate to start simple
# usable and best-practices compliant Python projects.
#
# Learn more about it at: http://github.com/fabiommendes/python-boilerplate/
#

import os
import codecs
from setuptools import setup, find_packages

# Save version and author to __meta__.py
version = open('VERSION').read().strip()
dirname = os.path.dirname(__file__)
path = os.path.join(dirname, 'src', 'transpyler', '__meta__.py')
meta = '''# Automatically created. Please do not edit.
__version__ = '%s'
__author__ = 'F\\xe1bio Mac\\xeado Mendes'
''' % version
with open(path, 'w') as F:
    F.write(meta)

setup(
    # Basic info
    name='transpyler',
    version=version,
    author='Fábio Macêdo Mendes',
    author_email='fabiomacedomendes@gmail.com',
    url='',
    description='A framework for building internationalized Python-like languages.',
    long_description=codecs.open('README.rst', 'rb', 'utf8').read(),

    # Classifiers (see https://pypi.python.org/pypi?%3Aaction=list_classifiers)
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Transpyler :: Python',
        'Programming Transpyler :: Python :: 3',
        'Programming Transpyler :: Python :: 3.4',
        'Programming Transpyler :: Python :: 3.5',
        'Programming Transpyler :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
    ],

    # Packages and dependencies
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'lazyutils',
        'unidecode',
    ],
    extras_require={
        'dev': [
            'python-boilerplate[dev]',
        ],
        'google_translate': [
            'textblob',
        ],
        'jupyter': [
            'jupyter',
            'jupyter-console',
            'ipython',
        ],
    },

    # Other configurations
    zip_safe=False,
    platforms='any',
)