.. image:: https://travis-ci.org/Transpyler/transpyler.svg?branch=master
    :target: https://travis-ci.org/Transpyler/transpyler

.. image:: https://codecov.io/gh/Transpyler/transpyler/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/Transpyler/transpyler

.. image:: https://ci.appveyor.com/api/projects/status/it45pshyqi76irbx?svg=true
    :target: https://ci.appveyor.com/project/fabiommendes/transpyler


Transpyler is an infrastructure to create simple localized versions of
Python. It was originally created as part of the Pytuguês language (Python
in Portuguese), but it is now abstracted to handle any translation. The
goal of such specialized languages is to provide a more friendly environment to
newcomers that are not fluent in English, children and adults alike.

Creating support for a new language is very simple. Say we want to create a
Py-Klingon to help us dominate the galaxy. Fortunately, Klingon structure is
not very different from English and we can go a long way just by translating
tokens. In transpyler it looks like this:

.. code-block:: python

    from transpyler import Transpyler

    # Let us define Py-Klingon
    klingon = Transpyler(
        name='Py-Klingon',
        translations={
            # Warning: computer-based translation!
            'meH': 'for',
            'chugh': 'if',
            'latlh': 'else',
            'Qap': 'def',
            'nobHa': 'return',
            # ... you get the idea ;-)
        })


    # Now execute some Klingon number crunching
    klingon.exec('''
    Qap fib(x):
        chugh x < 0:
            nobHa 1
        latlh:
            nobHa fib(x - 1) + fib(x - 2)
    ''', globals())

    print(fib(10))  # It creates a Python function!


Since the main goal is educational, transpyler-enabled languages automatically
supports a series of nice educational tools inherited from the original Pytuguês
runtume:

* Support for Jupyter/IPython: we can easily create a Jupyter kernel from a
  Transpyler instance. This enables nice consoles and notebooks which
  can be really handy in teaching a new programming language.
* QCode support and syntax highlight: QCode is a Qt-based widget for coding
  editing.
* Pygments plugin: Pygments is a source code highlighter commonly used to generate
  nice coloured HTML for source code.
* QTurtle application: QTurtle is similar to Python's own turtle module rewritten
  in Qt. This is great for teaching kids, and all transpyled languages support
  it for free :)


How does it work?
-----------------

Transpilation is the act of translating code from one programming language to
another (as opposed to compilation, which translate source code to machine
code). A **transpylation** is even simpler: it translate a Python-like language
back to Python (and sometimes execute it directly). This task is not very
difficult since both languages are similar and we can reuse lots of Python's
own machinery to analyze and modify its own source code.

Transpyler acts exclusively at the token level: it modifies the stream of tokens
from the original translated language to a new stream of tokens that must then
generate a grammatically valid python program. Indeed, we do not even implement
our own tokenizer and use Python's own ``tokenize`` module to handle this part
for us.

Transpyler works by making several passes over the list of tokens. The first
pass simply performs direct translations such as those shown in the Py-Klingon
example above. A second pass makes maps groups of tokens into a single Python
token (eg.: we could make a "for each" command that is translated to "for").

Subsequent passes may look for specific patterns of tokens and perform more
complex translations. Pytuguês, for instance, implements a "repeat" command.
In English it would be something like this:


.. code-block:: transpyler

    repeat 4 times:
        forward(100)
        left(90)

This is transpiled to Python as:

.. ignore-next-block
.. code-block:: python

    for ___ in range(4):
        forward(100)
        left(90)

It is possible to make arbitrary modifications to the list of tokens which in
principle could allow arbitrary syntactic constructs. Notice that tokens still
come from the Python tokenizer and hence there are certain hard lexical
constraints on (including indentation as block delimiter semantics which in
Python is implemented at the tokenizer level rather than in the grammar).

Transpyler do not implement source code maps because they are not needed by
Pytuguês and we don't think that simple localized Pythons would require
it. That said, new grammatical constructs should keep line numbers unaltered.

Remember: transpyler is using your regular vanilla Python interpreter and putting
a small layer of token translation on top of it. We make a few dirty hacks in the
Python runtime, but it does not requires any specially flavored interpreter
and additional compilation is unnecessary.


And the standard lib?
---------------------

I'm glad you asked :). This is by far the most laborious part of doing a decent
Python translation. Transpyler offers a few helpful tools, but most of the work
is the inevitable task of translating the names and docstrings of each function
you want to support into a their localized counterparts.

As a convenience tool, you can list the functions you want to translate and
we offer a tool that uses Google Translate to create a boilerplate for your
standard lib functions. Google Translate is a wonderful tool, but we all know
how bad it can get for serious translations. Always keep that in mind.

Here is a list of all projects using Transpyler.

* Pytuguês: the original Python to portuguese.
* Pykor: Korean version.
* Pytuñol: non-serious translation to Portuñol. It is a minimal project and can
be used as a template for new translations.


How about the builtin types?
----------------------------

Python builtins poses a challenge. They cannot be monkey-patched at Python level,
but we need to modify them. In Py-Klingon, we want the "teH" constant (True) to
be represented as "teH" rather than "True". We also want method names for
lists, strings, etc to be fully translated.

Transpyler messes with these types at C level using ctypes. The techniques are
very similar to those implemented in a module called ``forbiddenfruit``,
which recommends never to use itself unless you want to do something dangerous or
silly :)

In the language introduced by ``forbiddenfruit``, modifying a method to a builtin
type is called making a curse. We provide a tools to curse Python's builtins easily
and effectively.


A superset of Python?
---------------------

Transpyler languages are usually supersets of Python itself. In Pytuguês, for
instance, most Python code is also a valid Pytuguês code. This makes languages
easier to implement since we don't have to blacklist the original Python
keywords, but it also creates a path for going from a educational Pythonesque
languages to vanilla Python used in real world applications.

The fact that we don't make any effort to hide the Python internals and Python
original syntax is not a bug, its a feature!
