from multiprocessing import Process, Queue

from transpyler.turtle.state import MailboxState
from ..turtle import Turtle

__all__ = ['turtle', 'start_server', 'start_client']


#
# This is the user-visible turtle class for the QtSceneGraph. IPC is done using
# two message queues. The client publishes messages in a queue that is consumed
# by the server and vice-versa.
#
Turtle._state_factory = MailboxState


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
