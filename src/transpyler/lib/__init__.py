"""
Input and output functions
==========================

Functions for user interaction. Either reads files or typed values, or
displays values on the screen.

.. autofunction:: show
.. autofunction:: alert
.. autofunction:: show_formatted
.. autofunction:: read_text
.. autofunction:: read_number
.. autofunction:: read_file
.. autofunction:: save_in_file
.. autofunction:: pause


String processing
=================

Text processing functions.


Other
=====

Other functions that do not fall in any specific category.


Mathematical functions
======================

"""

TRANSLATIONS = {
    'exiter.name': 'quit',
    'exiter.doc': 'Type quit() to leave.',
    'cls.name': 'cls',
    'cls.doc': 'Clear screen'
}

from ._lib_std import *
from ._lib_str import *
from ._lib_io import *
from ..math import *
