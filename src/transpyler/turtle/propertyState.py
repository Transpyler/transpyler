from .turtleState import TurtleState
from .utils import getsetter

class PropertyState(TurtleState):
     """
     A Turtle state in which all attributes are properties that expose a
     getter/setter interface.

     This state class is used by the Tk implementation.
     """

     # Position
     getpos = lambda self: self._pos
     setpos = lambda self, v: setattr(self, '_pos', vec(*v))
     pos = getsetter('pos')

     # Heading
     getheading = lambda self: self._heading
     setheading = lambda self, v: setattr(self, '_heading', v)
     heading = getsetter('heading')

     # Drawing
     getdrawing = lambda self: self._drawing
     setdrawing = lambda self, v: setattr(self, '_drawing', v)
     drawing = getsetter('drawing')

     # Color
     getcolor = lambda self: self._color
     setcolor = lambda self, v: setattr(self, '_color', v)
     color = getsetter('color')

     # Fillcolor
     getfillcolor = lambda self: self._fillcolor
     setfillcolor = lambda self, v: setattr(self, '_fillcolor', v)
     fillcolor = getsetter('fillcolor')

     # Width
     getwidth = lambda self: self._width
     setwidth = lambda self, v: setattr(self, '_width', v)
     width = getsetter('width')

     # Hidden
     gethidden = lambda self: self._hidden
     sethidden = lambda self, v: setattr(self, '_hidden', v)
     hidden = getsetter('hidden')

     # Avatar
     getavatar = lambda self: self._avatar

     def setavatar(self, v):
         self.validate_avatar(v)
         self._avatar = v

     avatar = getsetter('avatar')
