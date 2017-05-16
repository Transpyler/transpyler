from multiprocessing import Process, Queue
from time import sleep

from transpyler.turtle.state import MailboxState
from ..turtle import Turtle as _Turtle, global_namespace

__all__ = ['turtle', 'start_server', 'start_client', 'global_namespace']


#
# This is the user-visible turtle class for the QtSceneGraph. IPC is done using
# two message queues. The client publishes messages in a queue that is consumed
# by the server and vice-versa.
#
class Turtle(_Turtle):
    """
    Creates a new turtle.
    """

    __slots__ = ()
    _state_factory = MailboxState
    _sleep = sleep
    _sleep_duration = 0.001
    _timeout = 0.1

    def __init__(self, **kwargs):
        kwargs.setdefault('width', 2)
        super().__init__(**kwargs)


def start_server(inbox, outbox):
    """
    Starts a server that reads messages from an inbox and return the responses
    on an outbox.
    """

    from transpyler.turtle.qt.scene import start_qt_scene_app

    start_qt_scene_app(inbox=inbox, outbox=outbox, ping=True)


def start_client():
    """
    Starts a remote process that initializes a TurtleScene widget and Qt's
    mainloop.
    """

    inbox = MailboxState.inbox = Queue()
    outbox = MailboxState.outbox = Queue()
    process = Process(target=start_server,
                      args=(outbox, inbox),
                      name='turtle-server')
    process.daemon = True
    process.start()

    # Send a ping message to the out process
    outbox.put(['ping'])
    msg = inbox.get(timeout=2.0)
    if msg != ['ping']:
        raise RuntimeError('wrong response from server: %s' % (msg,))

    return process
