from transpyler.utils import with_transpyler_attr


def run_jupyter(transpyler, gui=False):
    """
    Starts a Jupyter console for the given kernel.
    """

    from jupyter_client.kernelspec import NoSuchKernel
    from transpyler.jupyter.setup import setup_assets

    try:
        start_shell(transpyler, gui=gui)
    except NoSuchKernel:
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

    App.launch_instance(
        kernel_manager=Manager,
        kernel_name=transpyler.name,
        transpyler=transpyler,
    )


def start_qt_shell(transpyler):
    """
    Starts a shell based on QtConsole.
    """

    from transpyler.jupyter.app import ZMQTerminalTranspylerApp
    from transpyler.jupyter.app import TranspylerKernelManager

    App = with_transpyler_attr(ZMQTerminalTranspylerApp, transpyler)
    Manager = with_transpyler_attr(TranspylerKernelManager, transpyler)

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
