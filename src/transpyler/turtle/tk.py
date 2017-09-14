from .utils import turtle_property
from .namespace import TurtleNamespace
from . import Turtle as BaseTurtle, PropertyState


class TkTurtleState(PropertyState):
    """
    A turtle state class for Python's builtin turtle module.
    """

    valid_avatars = [
        'classic', 'arrow', 'turtle', 'circle', 'square', 'triangle'
    ]

    pos = _pos = turtle_property('pos', 'setpos')
    heading = _heading = turtle_property('heading', 'setheading')
    color = _color = turtle_property('color')
    fillcolor = _fillcolor = turtle_property('fillcolor')
    width = _width = turtle_property('width')
    avatar = _avatar = turtle_property('shape')

    def getdrawing(self):
        return self.turtle.isdown()

    def setdrawing(self, value):
        self.turtle.pd() if value else self.turtle.pu()

    def gethidden(self):
        return self.turtle.isvisible()

    def sethidden(self, value):
        self.turtle.hideturtle() if value else self.turtle.showturtle()

    def __init__(self, *args, **kwargs):
        from turtle import Turtle

        self.turtle = Turtle()
        super().__init__(*args, **kwargs)

    def step(self, step):
        self.turtle.fd(step)

    def rotate(self, angle):
        self.turtle.lt(angle)

    def move(self, pos):
        self.turtle.goto(*pos)


# The tk turtle class
class Turtle(BaseTurtle):
    """
    Represents a turtle.
    """

    _state_factory = TkTurtleState


def make_turtle_namespace():
    """
    Returns a dictionary with the namespace of turtle functions.
    """

    return dict(TurtleNamespace(Turtle))


def start_console(transpyler=None):
    """
    Starts a console with turtle functions based on the Tk module.
    """

    from transpyler.console import start_console
    start_console(make_turtle_namespace(), transpyler=transpyler)


# We load a global namespace if called with the python -m flag.
if __name__ == '__main__':
    start_console()
