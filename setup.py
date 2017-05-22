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


# Reuse dependencies list
dependencies = {
    'google_translate': ['textblob'],
    'jupyter': ['jupyter', 'jupyter-console', 'ipython'],
    'dev': ['python-boilerplate[dev]']
}
dependencies['dev'] += dependencies['google_translate'] + dependencies['jupyter']


setup(
    # Basic info
    name='transpyler',
    version=version,
    author='Fábio Macêdo Mendes',
    author_email='fabiomacedomendes@gmail.com',
    url='',
    description='A framework for building localized Python-like languages.',
    long_description=codecs.open('README.rst', 'rb', 'utf8').read(),

    # Classifiers (see https://pypi.python.org/pypi?%3Aaction=list_classifiers)
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
    ],

    # Package data
    package_data={
        'transpyler.jupyter': [
            'assets/*.*',
        ],
        'transpyler.turtle': [
            'data/*.*',
        ],
        'transpyler.l10n': [
            '*.po',
            '*.mo',
            '*.pot',
        ],
    },

    # Packages and dependencies
    package_dir={'': 'src'},
    packages=find_packages('src'),
    install_requires=[
        'lazyutils',
        'unidecode',
        'polib',
        'colortools',
        'click',
    ],
    extras_require={
        'dev': dependencies['dev'],
        'google_translate': dependencies['google_translate'],
        'jupypter': dependencies['jupyter'],
    },

    # Other configurations
    zip_safe=False,
    platforms='any',
)