from PyQt5 import QtWidgets, QtGui, QtCore

from .scene import TurtleScene

_LABEL_FONT = QtGui.QFont('Helvetica', 8)
_LABEL_FONT.setStyleStrategy(QtGui.QFont.NoAntialias)
_LABEL_PADDING = 2


class TurtleView(QtWidgets.QGraphicsView):
    """
    A TurtleView is a widget that can be inserted anywhere in the GUI and is
    responsible to render and display a TurtleScene.

    By default, the TurtleView applies a transforms that inverts the
    y-coordinate so that it point upwards instead of downwards (as is the
    default in many computer graphics applications). This transform also invert
    the direction of rotations: positive rotations are counter-clockwise and
    negative rotations are clockwise.
    """

    def __init__(self, scene=None):
        if scene is None:
            scene = TurtleScene()
        self._scene = scene
        super().__init__(scene)
        transform = QtGui.QTransform(
            1, 0,
            0, -1,  # Revert y, so it uses the standard axis convention in maths
            0, 0
        )
        self.setTransform(transform)
        self._zoomfactor = 1.2

        # This will crash if I put it in the module namespace, probably
        # because the QApplication instance does not exist yet
        _LABEL_HEIGHT = QtGui.QFontMetrics(
            _LABEL_FONT).height() + 2 * _LABEL_PADDING

        w = self._posLabel = QtWidgets.QLabel(self)
        # http://stackoverflow.com/questions/7928519/how-to-make-the-qlabel-background-semi-transparent
        # Fourth parameter in color tuple is alpha: 0-transparent; 255-opaque
        w.setStyleSheet('color: rgba(0, 0, 0, 196); '
                        'background-color: rgba(0, 0, 0, 0);'
                        'padding: %d' % _LABEL_PADDING)
        w.setAlignment(QtCore.Qt.AlignRight)
        w.setFont(_LABEL_FONT)
        w.setGeometry(0, 0, 100, _LABEL_HEIGHT)
        self._updatePosLabelText((0, 0))
        self._updatePosLabelPosition()

    def zoomIn(self):  # noqa: N802
        """
        Increase the zoom.
        """
        self.scale(self._zoomfactor, self._zoomfactor)

    def zoomOut(self):  # noqa: N802
        self.scale(1 / self._zoomfactor, 1 / self._zoomfactor)

    def notifyPosChanged(self, turtle, pos):  # noqa: N802
        if turtle is self._scene.mainTurtle():
            self._updatePosLabelText(pos)

    def resizeEvent(self, event):  # noqa: N802
        self._updatePosLabelPosition()
        super().resizeEvent(event)

    def _updatePosLabelPosition(self):  # noqa: N802
        size = self.viewport().size()
        w = self._posLabel
        margin = 3
        w.move(size.width() - w.width() - margin,
               size.height() - w.height() - margin)

    def _updatePosLabelText(self, pos):  # noqa: N802
        s = "x=%s, y=%s" % (round(pos[0]), round(pos[1]))
        self._posLabel.setText(s)

    def saveImage(self, fname):  # noqa: N802
        """
        Saves current viewport as a png file of the given fname.
        """

        rect = self.viewport()
        rgb = QtGui.QImage.Format_RGB32
        image = QtGui.QImage(rect.width(), rect.height(), rgb)
        image.fill(QtGui.QColor(255, 255, 255))
        painter = QtGui.QPainter(image)
        self.render(painter)
        if not image.save(fname):
            raise ValueError('could not save image %s' % fname)
        del painter
