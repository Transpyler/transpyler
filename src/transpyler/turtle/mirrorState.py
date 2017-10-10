from .remoteState import RemoteState
from .turtleState import TurtleState

class MirrorState(RemoteState):
    """
    A remote turtle that stores a copy of state in itself.

    This state is used by the QTurtle application in the kernel process.
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
