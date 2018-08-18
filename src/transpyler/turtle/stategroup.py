import collections
from multiprocessing import Queue

from .state import TurtleState


class StateGroup(collections.MutableSequence):
    """
    Manage and coordinate a group of turtle states.

    It presents itself as a list of turtles.
    """

    state_class = TurtleState

    def __init__(self):
        self._index = 0
        self._turtles = []

    def __setitem__(self, idx, value):
        if not isinstance(value, self.state_class):
            raise TypeError(type(value))
        value.register(self)
        self._turtles.__setitem__(idx, value)

    def __len__(self):
        return len(self._turtles)

    def __iter__(self):
        return iter(self._turtles)

    def __getitem__(self, idx):
        return self._turtles[idx]

    def __delitem__(self, idx):
        return self._turtles.__delitem__[idx]

    def getturtle(self, id):
        """
        Gets turtle by id.
        """
        for turtle in self:
            if turtle.id == id:
                return turtle
        raise ValueError('invalid turtle id: %s' % id)

    def insert(self, idx, value):
        self._turtles.insert(idx, None)
        try:
            self[idx] = value
        except Exception:
            self.remove(None)

    def new_turtle(self, **kwargs):
        """
        Creates a new turtle state passing the given parameters.

        Return the turtle state object.
        """

        self._index += 1
        turtle = self.state_class(**kwargs)
        turtle.id = self._index
        self.append(turtle)
        return turtle

    def clean(self):
        """
        Clear all drawings, but maintains turtles in their respective states.
        """
        for turtle in self:
            turtle.clean()

    def reset(self):
        """
        Clear all drawings, and reset turtle state.
        """
        for turtle in self:
            turtle.reset()


class IpcStateGroup(StateGroup):
    """
    A state handle that receives messages from a client using a inbox/outbox
    communication model.
    """

    inbox_factory = outbox_factory = Queue
    timeout = 1.0
    inbox = outbox = None

    def __init__(self, inbox=None, outbox=None, **kwargs):
        self.inbox = inbox or self.inbox_factory()
        self.outbox = outbox or self.outbox_factory()
        super().__init__(**kwargs)

    def ping(self, receive=False):
        """
        Handles a ping message.
        """

        if receive:
            msg = self.inbox.get(timeout=self.timeout)
            if msg != ['ping']:
                raise ValueError('invalid ping message: %s' % msg)
            self.outbox.put(msg)
        else:
            self.outbox.put(['ping'])
            msg = self.inbox.get(timeout=self.timeout)
            if msg != ['ping']:
                raise ValueError('invalid ping message: %s' % msg)

    def recv(self):
        """
        Reads message from the inbox and sends response.
        """

        msg = self.inbox.get(timeout=self.timeout)
        reply = self.handle(msg)
        self.outbox.put(reply)
        return reply

    def handle(self, msg):
        """
        Receive message and handle message.

        Dispatch to the corresponding turtle, if required.
        """

        action, *args = msg

        # Global actions
        if action == 'newturtle':
            kwargs = args[0]
            new = self.new_turtle(**kwargs)
            return ['newturtle', new.id]
        elif action == 'clear':
            self.clean()
            return ['clear']
        elif action == 'reset':
            self.reset()
            return ['reset']

        # Turtle actions
        elif action in ('get', 'set', 'move', 'step', 'rotate'):
            id = args[0]
            turtle = self.getturtle(id)
            return turtle.handle([action] + args)
        else:
            raise ValueError('invalid action: %r' % action)
