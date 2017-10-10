from multiprocessing import Queue

from colortools import Color

from .utils import getsetter, ipc_property
from ..math import vec, cos, sin, tan


class TurtleState:
    """
    An object that stores the turtle state. Users interact with Turtle
    instances that manipulates a state object. The state can be local and
    apply changes immediately or it can be remote and echo to a state stored
    in a different process/machine/thread.
    """

    valid_avatars = ['default']

    @property
    def heading_direction(self):
        return vec(self._cos(self.heading), self._sin(self.heading))

    def __init__(self, pos=None, heading=0.0, drawing=True,
                 color='black', fillcolor='black', width=1, hidden=False,
                 avatar=None, group=None, id=None):
        self.pos = self.startpos = self._vec(pos or (0, 0))
        self.heading = self.startheading = heading
        self.drawing = self.startdrawing = drawing
        self.color = color
        self.fillcolor = fillcolor
        self.width = width
        self.hidden = hidden
        self.avatar = self.valid_avatars[0] if avatar is None else avatar
        self.lines = []
        self.group = group
        self.id = id

    def validate_avatar(self, avatar):
        """
        Raises a ValueError if avatar is not a valid avatar name.
        """
        if avatar is not None and avatar not in self.valid_avatars:
            raise ValueError('invalid avatar name: %s')

    def rotate(self, angle):
        """
        Rotate cursor heading in the counter clockwise direction.
        """
        self.heading += angle

    def move(self, pos):
        """
        Move turtle possibly drawing a line.
        """
        oldpos = self.pos
        self.pos = pos
        if self.drawing:
            self.draw_line(oldpos, pos)

    def step(self, step):
        """
        Move forwards (or backwards if step is negative).
        """
        self.move(self.pos + self.heading_direction * step)

    def clear(self):
        """
        Remove all drawn lines.
        """
        self.lines.clear()

    def reset(self):
        """
        Reset turtle to initial state.
        """

        self.clear()
        self.pos = self.startpos
        self.heading = self.startheading
        self.drawing = self.startdrawing

    def draw_line(self, v1, v2):
        """
        Draws line from v1 to v2.
        """
        raise NotImplementedError

    def register(self, group):
        """
        Register on a group.
        """
        self.group = group

    def recv(self):
        """
        Receives messages from a connection.
        """
        raise NotImplementedError

    def handle(self, msg):
        """
        Handle message and redirect to the proper method.
        """

        action, id, *args = msg
        if id != self.id:
            raise ValueError('invalid turtle id (%s)' % msg)

        if action == 'get':
            return ['get', id, getattr(self, args[0])]
        elif action == 'set':
            setattr(self, *args)
            return ['set', id, args[0]]
        elif action == 'rotate':
            self.rotate(args[0])
            return ['rotate', id]
        elif action == 'move':
            self.move(args[0])
            return ['move', id]
        elif action == 'step':
            self.step(args[0])
            return ['step', id]
        else:
            raise ValueError('invalid action: %r' % action)

    # Mathematical functions. We define them here so they can be overridable in
    # subclasses.
    _cos = staticmethod(cos)
    _sin = staticmethod(sin)
    _tan = staticmethod(tan)
    _vec = staticmethod(vec)
