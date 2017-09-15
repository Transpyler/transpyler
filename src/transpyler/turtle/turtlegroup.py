import collections

from .utils import vecargsmethod
from ..math import Vec


class TurtleGroup(collections.MutableSequence):
    """
    A synchronized group of turtles.

    Functions are broadcasted to all turtles belonging to the group.
    """

    _state_class = None
    __slots__ = ('_data',)

    def __init__(self):
        self._data = []

    def __repr__(self):
        return 'TurtleGroup(%r)' % self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, i):
        return self._data[i]

    def __delitem__(self, i):
        return self._data.__delitem__(i)

    def __setitem__(self, i, v):
        return self._data.__setitem__(i, v)

    def insert(self, i, v):
        return self.insert(i, v)

    @vecargsmethod
    def setpos(self, value):
        pos = Vec(*value)
        for t in self:
            t.setpos(pos)

    def setheading(self, value):
        for t in self:
            t.setheading(value)

    def setwidth(self, value):
        for t in self:
            t.setwidth(value)

    def setcolor(self, value):
        for t in self:
            t.setcolor(value)

    def setfillcolor(self, value):
        for t in self:
            t.setfillcolor(value)

    def setavatar(self, value):
        for t in self:
            t.setavatar(value)

    def penup(self):
        """
        Raises the turtle pen so it stops drawing.

        Aliases: penup | pu
        """
        for t in self:
            t.penup()

    def pendown(self):
        """
        Lower the turtle pen so it can draw in the screen.

        Aliases: pendown | pd
        """
        for t in self:
            t.pendown()

    def isdown(self):
        """
        Return True if all turtles are drawing.
        """
        return all(t.isdown() for t in self)

    def isvisible(self):
        """
        Return True if all turtles are visible.
        """
        return all(t.isvisible() for t in self)

    def arehidden(self):
        """
        Return True if all turtles are not visible.
        """
        return all(t.ishidden() for t in self)

    def hide(self):
        """
        Hide all turtles.
        """
        for t in self:
            t.hide()

    def show(self):
        """
        Shows all hidden turtle.
        """
        for t in self:
            t.show()

    @vecargsmethod
    def goto(self, pos):
        """
        Goes to the given position.

        If the pen is down, it draws a line.
        """
        for t in self:
            t.goto(pos)

    @vecargsmethod
    def jump(self, pos):
        """
        Relative movement by the desired position. It *never* draw as line even
        if the pen is down.
        """
        for t in self:
            t.jump(pos)

    def forward(self, step):
        """
        Move the turtle forward by the given step size (in pixels).

        Aliases: forward | fd
        """
        for t in self:
            t.forward(step)

    def backward(self, step):
        """
        Move the turtle backward by the given step size (in pixels).

        Aliases: backward | back | bk
        """
        for t in self:
            t.backward(step)

    def left(self, angle):
        """
        Rotate the turtle counter-clockwise by the given angle.

        Aliases: left | lt

        Negative angles produces clockwise rotation.
        """
        for t in self:
            t.left(angle)

    def right(self, angle):
        """
        Rotate the turtle clockwise by the given angle.

        Aliases: right | rt

        Negative angles produces counter-clockwise rotation. Return final
        heading.
        """
        for t in self:
            t.right(angle)

    def clear(self):
        """
        Clear all drawings made by turtles.
        """
        for t in self:
            t.clear()

    def reset(self):
        """
        Clear all drawings and reset turtles to initial position.
        """
        for t in self:
            t.reset()

    # Aliases
    fd = forward
    bk = back = backward
    lt = left
    rt = right
    pu = penup
    pd = pendown
