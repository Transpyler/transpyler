from colortools import Color
from lazyutils import lazy

from .utils import vecargsmethod
from ..math import Vec


class Turtle:
    """
    Creates a new Turtle.
    """

    _state_factory = None

    @lazy
    def _state(self):
        if self._state_factory is None:
            raise RuntimeError('Turtle does not define an _state_factory '
                               'attribute')
        return self._state_factory(**self._args)

    def __init__(self, pos=None, heading=0.0, *, drawing=True,
                 color='black', fillcolor='black', width=2, hidden=False):
        self._args = dict(
            pos=pos, heading=heading, drawing=drawing, color=color,
            fillcolor=fillcolor, width=width, hidden=hidden
        )
        self.forward(1)


    def __repr__(self):
        return 'Turtle(%r)' % self.getavatar()

    def getpos(self):
        """
        Return a vector (x, y) with turtle's position (in pixels).
        """
        return self._state.pos

    @vecargsmethod
    def setpos(self, value):
        """
        Modifies turtle's position (in pixels)

        User can pass the x, y coordinates of the new position or a tuple of
        (x, y) values. This method never draws a line.
        """
        self._state.pos = Vec(*value)

    def getheading(self):
        """
        Return current heading of the turtle (in degrees).
        """
        return self._state.heading

    def setheading(self, value):
        """
        Sets turtle's heading (in degrees).
        """
        self._state.heading = value

    def getwidth(self):
        """
        Return the pen width (in pixels):
        """
        return self._state.width

    def setwidth(self, value):
        """
        Modifies the pen width (in pixels)
        """
        self._state.width = value

    def getcolor(self):
        """
        Return a tuple of (R, G, B) with the current pen color.
        """
        return Color(self._state.color)

    def setcolor(self, value):
        """
        Modifies the pen color.

        Color can be specified as an (R, G, B) tuple or as a hex string or by
        name.
        """
        self._state.color = value

    def getfillcolor(self):
        """
        Return a tuple of (R, G, B) with the current fill color.
        """
        return Color(self._state.fillcolor)

    def setfillcolor(self, value):
        """
        Modifies the fill color.

        Color can be specified as an (R, G, B) tuple or as a hex string or by
        name.
        """
        self._state.fillcolor = value

    def getavatar(self):
        """
        Return a string with the name of the current avatar.
        """
        return self._state.avatar

    def setavatar(self, value):
        """
        Modifies the turtle avatar.
        """
        self._state.avatar = value

    def penup(self):
        """
        Raises the turtle pen so it stops drawing.

        Aliases: penup | pu
        """
        self._state.drawing = False

    def pendown(self):
        """
        Lower the turtle pen so it can draw in the screen.

        Aliases: pendown | pd
        """
        self._state.drawing = True

    def isdown(self):
        """
        Return True if the pen is down or False otherwise.
        """
        return self._state.drawing

    def isvisible(self):
        """
        Return True if the turtle is visible.
        """
        return not self._state.hidden

    def ishidden(self):
        """
        Return True if the turtle is not visible.
        """
        return self._state.hidden

    def hide(self):
        """
        Hide turtle.
        """
        self._state.hidden = True

    def show(self):
        """
        Shows a hidden turtle.
        """
        self._state.hidden = False

    def clear(self):
        """
        Clear all drawings made by turtle.
        """
        self._state.clear()

    def reset(self):
        """
        Clear all drawings and reset turtle to initial position.
        """
        self._state.reset()

    @vecargsmethod
    def goto(self, pos):
        """
        Goes to the given position.

        If the pen is down, it draws a line.
        """
        self._state.goto(pos)

    @vecargsmethod
    def jump(self, pos):
        """
        Relative movement by the desired position. It *never* draw as line even
        if the pen is down.
        """
        self._state.pos = pos + self._state.pos

    def forward(self, step):
        """
        Move the turtle forward by the given step size (in pixels).

        Aliases: forward | fd
        """
        self._state.step(step)

    def backward(self, step):
        """
        Move the turtle backward by the given step size (in pixels).

        Aliases: backward | back | bk
        """
        self.forward(-step)

    def left(self, angle):
        """
        Rotate the turtle counter-clockwise by the given angle.

        Aliases: left | lt

        Negative angles produces clockwise rotation.
        """
        self._state.rotate(angle)

    def right(self, angle):
        """
        Rotate the turtle clockwise by the given angle.

        Aliases: right | rt

        Negative angles produces counter-clockwise rotation. Return final
        heading.
        """
        self.left(-angle)

    # Aliases
    fd = forward
    bk = back = backward
    lt = left
    rt = right
    pu = penup
    pd = pendown

    # Attribute-based access to state
    pos = property(getpos, setpos)
    heading = property(getheading, setheading)
    width = property(getwidth, setwidth)
    color = property(getcolor, setcolor)
    fillcolor = property(getfillcolor, setfillcolor)
    drawing = property(isdown, lambda _, v: _.pendown() if v else _.penup())
    hidden = property(ishidden, lambda _, v: _.hide() if v else _.show())
