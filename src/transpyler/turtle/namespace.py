from collections.abc import Mapping
from functools import wraps

from .turtle import Turtle


class TurtleNamespace(Mapping):
    """
    Define all global functions that should be used in the turtle namespace.

    It behaves as an immutable mapping.
    """

    def __init__(self, turtle_cls=Turtle):
        self.turtle_cls = turtle_cls
        self._data = {}
        self._mainturtle = None
        self._maingroup = None
        self._data.update(self._namespace())

    def __getitem__(self, item):
        return self._data[item]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def mainturtle(self):
        """
        Returns the main turtle object.
        """

        if self._mainturtle is None:
            self._mainturtle = self.turtle_cls()
        return self._mainturtle

    def _from_turtle(self, method: callable):
        name = method.__name__

        @wraps(method)
        def func(*args, **kwargs):
            turtle = self.mainturtle()
            return getattr(turtle, name)(*args, **kwargs)

        return func

    def _namespace(self):
        wrap = self._from_turtle
        cls = self.turtle_cls
        return dict(
            mainturtle=self.mainturtle,
            Turtle=self.turtle_cls,

            # Getters and setters
            getpos=wrap(cls.getpos),
            setpos=wrap(cls.setpos),
            getheading=wrap(cls.getheading),
            setheading=wrap(cls.setheading),
            getwidth=wrap(cls.getwidth),
            setwidth=wrap(cls.setwidth),
            getcolor=wrap(cls.getcolor),
            setcolor=wrap(cls.setcolor),
            getfillcolor=wrap(cls.getfillcolor),
            setfillcolor=wrap(cls.setfillcolor),
            getavatar=wrap(cls.getavatar),
            setavatar=wrap(cls.setavatar),

            # Visibility
            penup=wrap(cls.penup),
            pendown=wrap(cls.pendown),
            isdown=wrap(cls.isdown),
            isvisible=wrap(cls.isvisible),
            ishidden=wrap(cls.ishidden),
            hide=wrap(cls.hide),
            show=wrap(cls.show),
            clean=wrap(cls.clean),
            reset=wrap(cls.reset),

            # Movement
            goto=wrap(cls.goto),
            jump=wrap(cls.jump),
            forward=wrap(cls.forward),
            backward=wrap(cls.backward),
            left=wrap(cls.left),
            right=wrap(cls.right),
            setspeed=self.setspeed,
            getspeed=self.getspeed,

            # Aliases
            fd=wrap(cls.forward),
            bk=wrap(cls.backward),
            back=wrap(cls.backward),
            lt=wrap(cls.left),
            rt=wrap(cls.right),
            pu=wrap(cls.penup),
            pd=wrap(cls.pendown),
        )

    def getspeed(self):
        return 5

    def setspeed(self, value):
        pass
