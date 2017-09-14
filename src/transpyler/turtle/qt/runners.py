import sys
from multiprocessing import Process, Queue

from PyQt5 import QtWidgets

from .scene import TurtleScene
from .. import MailboxState


def start_qt_scene_app_subprocess():
    """
    Starts a remote sub-process that initializes a TurtleScene widget and Qt's
    mainloop.
    """

    inbox = MailboxState.inbox = Queue()
    outbox = MailboxState.outbox = Queue()
    process = Process(target=start_qt_scene_app,
                      kwargs=dict(outbox=outbox, inbox=inbox, ping=True),
                      name='turtle-server')
    process.daemon = True
    process.start()

    # Send a ping message to the out process
    outbox.put(['ping'])
    msg = inbox.get(timeout=2.0)
    if msg != ['ping']:
        raise RuntimeError('wrong response from server: %s' % (msg,))

    return process


def start_qt_scene_app(inbox=None, outbox=None, ping=False):
    """
    Starts a simple QtApp with a TurtleScene widget.

    Args:
        inbox/outbox:
            Inbox/Outbox queues used for IPC.
    """
    from .view import TurtleView

    app = QtWidgets.QApplication(sys.argv)
    scene = TurtleScene(inbox=inbox, outbox=outbox)
    window = TurtleView(scene)
    window.setWindowTitle('Turtle')
    window.setMinimumWidth(800)
    window.setMinimumHeight(600)
    if ping:
        scene.ping(receive=True)
    window.show()
    sys.exit(app.exec_())


def start_console():
    """
    Starts a console with the Qt interface.
    """

    raise NotImplementedError('Qt interface does not support console app yet!')
