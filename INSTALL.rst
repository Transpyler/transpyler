=========================
Installation instructions
=========================

Transpyler can be installed using pip::

    $ python3 -m pip install transpyler

This command will fetch the archive and its dependencies from the internet and
install them. 

If you've downloaded the tarball, unpack it, and execute::

    $ python3 setup.py install --user

You might prefer to install it system-wide. In this case, skip the ``--user``
option and execute as superuser by prepending the command with ``sudo``.


Troubleshoot
------------

Windows users may find that these commands only work if typed from Python's
installation directory.

Some Linux distributions (e.g. Ubuntu) install Python without pip. Please
install it before using the package manager. If you don't have root privileges,
download the get-pip.py script at https://get-pip.org and execute it as
``python get-pip.py --user``.