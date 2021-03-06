from transpyler.utils import with_transpyler_attr, clear_argv


def start_jupyter(transpyler, gui=False):
    """
    Starts a Jupyter console for the given kernel.
    """

    from jupyter_client.kernelspec import NoSuchKernel
    from transpyler.jupyter.setup import setup_assets

    try:
        start_shell(transpyler, gui=gui)
    except NoSuchKernel:
        setup_assets(transpyler, user=True)
        setup_assets(transpyler, user=True)
        start_shell(transpyler, gui=gui)


def start_console_shell(transpyler):
    """
    Starts a cli-based shell.
    """

    from transpyler.jupyter.app import ZMQTerminalTranspylerApp
    from transpyler.jupyter.app import TranspylerKernelManager

    App = with_transpyler_attr(ZMQTerminalTranspylerApp, transpyler)
    Manager = with_transpyler_attr(TranspylerKernelManager, transpyler)

    clear_argv()
    App.launch_instance(
        kernel_manager=Manager,
        kernel_name=transpyler.name,
        transpyler=transpyler,
    )


def start_qt_shell(transpyler):
    """
    Starts a shell based on QtConsole.
    """

    # Starts qtconsole
    from transpyler.jupyter.app import ZMQTerminalTranspylerApp
    from transpyler.jupyter.app import TranspylerKernelManager

    App = with_transpyler_attr(ZMQTerminalTranspylerApp, transpyler)
    Manager = with_transpyler_attr(TranspylerKernelManager, transpyler)

    clear_argv()
    App.launch_instance(
        kernel_manager=Manager,
        kernel_name=transpyler.name,
        transpyler=transpyler,
    )


def start_shell(transpyler, gui=False):
    """
    Starts pytuga shell.
    """

    if gui:
        start_qt_shell(transpyler)
    else:
        start_console_shell(transpyler)


def start_notebook(transpyler):
    """
    Starts a jupyter notebook.
    """

    # Starts qtconsole
    from notebook.notebookapp import NotebookApp
    from transpyler.jupyter.app import TranspylerKernelManager
    import sys

    App = with_transpyler_attr(NotebookApp, transpyler)
    Manager = with_transpyler_attr(TranspylerKernelManager, transpyler)

    sys.argv[:] = ['notebook']
    App.launch_instance(
        kernel_manager=Manager,
        kernel_name=transpyler.name,
        transpyler=transpyler,
    )
