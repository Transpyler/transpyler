from .tk import Turtle
from .turtle import global_namespace as _global_namespace


globals().update(_global_namespace(Turtle))
