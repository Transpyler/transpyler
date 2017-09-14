import os

from PyQt5 import QtGui
from PyQt5 import QtSvg

from .utils import qtproperty, from_qvector, to_qvector, from_qcolor, to_qcolor
from .. import TurtleState, MailboxState, IpcStateGroup, Turtle as BaseTurtle

dir_path = os.path.dirname(os.path.dirname(__file__))
svg_path = os.path.join(dir_path, 'data', 'turtleart.svg')
svg_renderer = QtSvg.QSvgRenderer(svg_path)


class QGraphicsItemState(TurtleState):
    """
    A server turtle that redirects operations to a QGraphicsSvgItem.

    This turtle lives on the server part of the application.
    """

    valid_avatars = ['tuga']
    pos = qtproperty('graphics_item.pos', from_qvector, to_qvector)
    heading = qtproperty('graphics_item.rotation')
    width = qtproperty('pen.width')
    color = qtproperty('pen.color', from_qcolor, to_qcolor)
    fillcolor = qtproperty('brush.color', from_qcolor, to_qcolor)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('width', 2)
        avatar = kwargs.setdefault('avatar', 'tuga')
        self.size = kwargs.pop('size', 45)
        self.validate_avatar(avatar)
        self.graphics_item = cursor = QtSvg.QGraphicsSvgItem()

        # Loads from turtleart.svg
        cursor.setSharedRenderer(svg_renderer)
        cursor.setElementId(avatar)

        # Define local transforms
        rect = cursor.sceneBoundingRect()
        curr_width, curr_height = rect.width(), rect.height()
        cursor.setTransform(QtGui.QTransform(
            1.00, 0.00,
            0.00, 1.00,
            -curr_width / 2, -curr_height / 2)
        )
        cursor.setTransformOriginPoint(0.5 * curr_width, 0.5 * curr_height)
        cursor.setScale(self.size / curr_width)
        cursor.setZValue(1.0)
        self.pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        self.brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        super().__init__(*args, **kwargs)

    def draw_line(self, v1, v2):
        a, b = v1
        c, d = v2
        line = self.group.scene.addLine(a, b, c, d, self.pen)
        self.lines.append(line)

    def clear(self):
        scene = self.group.scene
        lines = self.lines
        while lines:
            line = lines.pop()
            scene.removeItem(line)

    def register(self, group):
        super().register(group)
        group.scene.addItem(self.graphics_item)


class QGraphicsSceneGroup(IpcStateGroup):
    """
    A manager of turtle states.
    """

    state_class = QGraphicsItemState

    def __init__(self, scene, **kwargs):
        self.scene = scene
        super().__init__(**kwargs)


#
# This is the user-visible turtle class for the QtSceneGraph. IPC is done using
# two message queues. The client publishes messages in a queue that is consumed
# by the server and vice-versa.
#
class Turtle(BaseTurtle):
    """
    Creates a new Turtle.
    """
    _state_factory = MailboxState
