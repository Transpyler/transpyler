import operator as op

import colortools
from PyQt5.QtCore import QPointF, QObject
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QGraphicsLineItem

from transpyler.math import Vec
from transpyler.turtle.utils import webcolor


def to_qcolor(value):
    """
    Convert a color, color tuple or color string to a QColor object.
    """
    if isinstance(value, str):
        value = webcolor(value)
    color = colortools.Color(value)
    return QColor(*color.rgba)


def from_qcolor(color):
    """
    Converts QColor to Color object.
    """
    return colortools.Color(*color.rgba())


def to_qvector(value):
    """
    Converts a vector-like object to QPointF.
    """
    return QPointF(*value)


def from_qvector(value):
    """
    Converts a QPointF to a Vec.
    """
    return Vec(value.x(), value.y())


class QLine(QGraphicsLineItem, QObject):
    """
    A line/QObject class.
    """

    def __init__(self, v0, v1, pen):
        x0, y0 = v0
        x1, y1 = v1
        super().__init__(x0, y0, x1, y1)
        self.setPen(pen)


def qtproperty(name, unwrap=lambda x: x, wrap=lambda x: x):
    """
    Expose a property of an attribute that respects Qt's get/setter
    conventions.

    If transform is defined, it is applied to the value passed to the setter
    method.

    Example::

        class MyObj:
            title = qtproperty('_widget.title')
    """

    prop, action = name.split('.')
    set_name = '%s.set%s' % (prop, action.title())
    getter = op.attrgetter(name)
    setter = op.attrgetter(set_name)
    return property(
        lambda x: unwrap(getter(x)()),
        lambda x, v: setter(x)(wrap(v)),
    )
