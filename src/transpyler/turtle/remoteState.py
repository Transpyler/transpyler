from .turtleState import TurtleState
from .utils import getsetter, ipc_property
from ..math import vec, cos, sin, tan
from colortools import Color

class RemoteState(TurtleState):
    """
    An abstract state class that stores information remotely and pipes all
    requests to a `.send(msg)` method. Subclass must implement the .send()
    method accordingly.

    The message is an S-expression:

    ['get', id, attr]:
        Get an state attribute
    ['set', id, attr, value]:
        Set an state attribute to a given value
    ['step', id, length]:
        Steps forward for the given length.
    ['rotate', id, angle]:
        Rotates by the given angle.
    ['move', id, pos]:
        Moves turtle to the given position.

    The actual state info is stored on another thread or process.
    """

    pos = ipc_property('pos', vec, tuple)
    heading = ipc_property('heading')
    drawing = ipc_property('drawing')
    color = ipc_property('color', Color, tuple)
    fillcolor = ipc_property('fillcolor', Color, tuple)
    width = ipc_property('width')
    hidden = ipc_property('hidden')
    avatar = ipc_property('avatar')
    id = None

    def __init__(self, **kwargs):
        msg = self.send(['newturtle', kwargs])
        if msg[0] != 'newturtle':
            raise ValueError('invalid reply: %s' % msg)
        self.id = kwargs.pop('id', msg[1])
        if not self.id:
            raise ValueError('invalid remote id: %s' % self.id)

    def rotate(self, angle):
        self.send(['rotate', self.id, angle])

    def move(self, pos):
        self.send(['move', self.id, tuple(pos)])

    def step(self, step):
        self.send(['step', self.id, step])

    def getvalue(self, attr):
        return self.send(['get', self.id, attr])[2]

    def setvalue(self, attr, value):
        return self.send(['set', self.id, attr, value])

    def send(self, msg):
        """
        Implemented in the client process. Just sends messages through a
        connection.
        """
        raise NotImplementedError('must implement the .send(msg) method')
