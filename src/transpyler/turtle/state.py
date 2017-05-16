from multiprocessing import Queue

from colortools import Color

from .utils import getsetter, ipc_property
from ..math import vec, cos, sin, tan


class TurtleState:
    """
    An object that stores the turtle state. Users interact with Turtle
    instances that manipulates a state object. The state can be local and
    apply changes immediately or it can be remote and echo to a state stored
    in a different process/machine.
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


class PropertyState(TurtleState):
    """
    A Turtle state in which all attributes are properties that expose a
    getter/setter interface.
    """

    # Position
    getpos = lambda x: x._pos
    setpos = lambda x, v: setattr(x, '_pos', vec(*v))
    pos = getsetter('pos')

    # Heading
    getheading = lambda x: x._heading
    setheading = lambda x, v: setattr(x, '_heading', v)
    heading = getsetter('heading')

    # Drawing
    getdrawing = lambda x: x._drawing
    setdrawing = lambda x, v: setattr(x, '_drawing', v)
    drawing = getsetter('drawing')

    # Color
    getcolor = lambda x: x._color
    setcolor = lambda x, v: setattr(x, '_color', v)
    color = getsetter('color')

    # Fillcolor
    getfillcolor = lambda x: x._fillcolor
    setfillcolor = lambda x, v: setattr(x, '_fillcolor', v)
    fillcolor = getsetter('fillcolor')

    # Width
    getwidth = lambda x: x._width
    setwidth = lambda x, v: setattr(x, '_width', v)
    width = getsetter('width')

    # Hidden
    gethidden = lambda x: x._hidden
    sethidden = lambda x, v: setattr(x, '_hidden', v)
    hidden = getsetter('hiden')

    # Avatar
    getavatar = lambda x: x._avatar
    setavatar = lambda x, v: x.validate_avatar(v) and setattr(x, '_avatar', v)
    avatar = getsetter('avatar')


class RemoteState(TurtleState):
    """
    A turtle that stores state remotely and pipes all requests to a
    `.send(msg)` method.

    The actual state info is stored on another thread/process.
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


class MailboxState(RemoteState):
    """
    A remote state that uses a multiprocessing.Queue to communicate between
    processes.

    The communication uses an inbox/outbox model. The client puts a message in
    the outbox and the server responds with a message in the outbox.
    """

    inbox_factory = lambda self: Queue()
    outbox_factory = lambda self: Queue()
    timeout = 1.0

    def __init__(self, **kwargs):
        # Initialize inbox
        try:
            self.inbox = kwargs['inbox']
        except KeyError:
            if not hasattr(self, 'inbox'):
                self.inbox = self.inbox_factory()

        # Initialize outbox
        try:
            self.outbox = kwargs['outbox']
        except KeyError:
            if not hasattr(self, 'outbox'):
                self.outbox = self.outbox_factory()

        super().__init__(**kwargs)

    def send(self, msg):
        self.put_message(msg)
        return self.get_message()

    def put_message(self, msg):
        """
        Put outgoing message on the outbox
        """
        self.outbox.put(msg)

    def get_message(self):
        """
        Get incoming message from the inbox.
        """
        return self.inbox.get(timeout=self.timeout)

    def draw_line(self, v1, v2):
        pass  # no-op: we broadcast and let the server handle it


class MirrorState(RemoteState):
    """
    A remote turtle that stores a copy of state in itself.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.local = TurtleState(**kwargs)
        self.local.draw_line = lambda v1, v2: None
        self.id = self.local.id

    def getvalue(self, attr):
        return getattr(self.local, attr)

    def setvalue(self, attr, value):
        setattr(self.local, attr, value)
        super().setvalue(attr, value)

    def rotate(self, angle):
        local = self.local
        local.rotate(angle)
        super().rotate(angle)
        self.setvalue('heading', local.heading)

    def move(self, pos):
        local = self.local
        local.move(pos)
        super().move(pos)
        self.setvalue('pos', local.pos)

    def step(self, step):
        local = self.local
        local.step(step)
        super().step(step)
        self.setvalue('pos', local.pos)

    def draw_line(self, v1, v2):
        pass