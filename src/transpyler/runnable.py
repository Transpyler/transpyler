from .utils.utils import has_qt

def start_console(transpyler, console='auto', turtle='auto'):
    """
    Starts a regular python console with the current transpyler.

    Args:
        console:
            Can be one of 'jupyter', 'console', 'qtconsole', 'auto'. This
            chooses the default console application. The default behavior
            (auto) is to try jupyter and fallback to console if it is
            not available.
        turtle:
            Sets the turtle backend. It can be either 'qt', 'tk', 'none' or
            'auto'. The defaut strategy (auto) is to try the qt first and
            fallback to tk.
    """

    # Select the console application
    if console == 'auto':
        try:
            import IPython  # noqa: F401
        except ImportError:
            console = 'console'
        else:
            console = 'jupyter'

    if console == 'qtconsole':
        from .jupyter import start_jupyter
        start_jupyter(transpyler=transpyler, gui=True)

    elif console == 'jupyter':
        from .jupyter import start_jupyter
        start_jupyter(transpyler=transpyler, gui=False)

    elif console == 'console':
        from .console import start_console
        start_console(transpyler=transpyler)

def start_notebook(transpyler):
    """
    Starts a jupyter notebook with the current transpyler.
    """

    from .jupyter import start_notebook
    start_notebook(transpyler)

def start_qturtle(transpyler):
    """
    Starts a QTurtle application with the current transpyler.
    """

    if not has_qt():
        raise SystemExit('PyQt5 is necessary to run the turtle '
                         'application.')

    from qturtle.mainwindow import start_application
    start_application(transpyler)
