from collections import deque
from multiprocessing import Queue

from PyQt5 import QtWidgets, QtCore

from .state import QGraphicsSceneGroup


class TurtleScene(QtWidgets.QGraphicsScene):
    """
    The TurtleScene defines the scene in which geometric objects resides.

    It controls the Turtle object and how it draws in the screen.
    """

    clearScreenSignal = QtCore.pyqtSignal()
    restartScreenSignal = QtCore.pyqtSignal()

    def __init__(self, parent=None, fps=30, inbox=None, outbox=None):
        super().__init__(parent)
        self._fps = fps
        self._interval = 1 / fps
        self.startTimer(1000 / fps)

        # Connect signals to slots
        self.clearScreenSignal.connect(self.clearScreen)
        self.restartScreenSignal.connect(self.restartScreen)

        # Creates mail boxes
        self._inbox = inbox = Queue() if inbox is None else inbox
        self._outbox = outbox = Queue() if outbox is None else outbox

        # Init
        self._turtles = QGraphicsSceneGroup(self, inbox=inbox, outbox=outbox)
        self._tasks = deque()
        assert self._turtles.inbox is self._inbox
        assert self._turtles.outbox is self._outbox

    def clearTurtles(self):
        self._turtles.clear()

    #
    # Events and signals
    #
    def clearScreen(self):
        state = self.fullTurtleState()
        self.clear()
        self.setFullTurtleState(state)

    def restartScreen(self):
        self.clear()

    #
    # Task control and communication
    #
    def ping(self, receive=False):
        """
        Handles a ping message.
        """
        self._turtles.ping(receive=receive)

    def timerEvent(self, timer):
        """
        Scheduled to be executed at some given framerate.

        It process all queued animation _tasks.
        """

        inbox = self._inbox
        turtles = self._turtles
        while not inbox.empty():
            turtles.recv()

    #
    # Turtle control
    #
    def newTurtle(self, *, default=False, **kwds):
        """
        Adds new turtle to the scene and return it.
        """

        turtle = self._turtles.new_turtle(**kwds)
        self.addItem(turtle.graphic_item)
        if default:
            self.setTurtle(turtle)
        return turtle

    def turtle(self):
        """
        Return the active turtle.
        """
        return self._turtle

    def setTurtle(self, turtle):
        """
        Configures the active Turtle object.
        """
        self._turtle = turtle

    #
    # Turtle visibility
    #
    def isActiveTurtleVisible(self):
        return not self.isActiveTurtleHidden()

    def isActiveTurtleHidden(self):
        if self._turtle is None:
            return True
        return self._turtle.hidden

    def hideActiveTurtle(self):
        if self._turtle is not None:
            self._turtle.hide()

    def showActiveTurtle(self):
        if self._turtle is None:
            raise ValueError('no turtle defined')
        self._turtle.show()

    #
    # Communication with the client. The client sends messages with turtle
    # commands. The scene graph updates the turtle state and return a response.
    #
    def receive(self, msg):
        # TODO: handle this properly. Turtle should send messages that asks
        # for certain turtle movements and draws the corresponding geometric
        # figures
        pass
