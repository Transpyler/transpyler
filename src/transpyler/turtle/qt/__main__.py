from .turtle import Turtle, start_client as _start_client
from transpyler.turtle.globalfunctions import GlobalFunctions as _globals
from ..turtle import global_namespace as _global_namespace

#
# When called as a module with the -i flag, it populates the global_namespace with
# Turtle names and opens a Python interpreter in this global_namespace.
#
_process = _start_client()
globals().update(_global_namespace(Turtle))
globals().update(_globals.global_namespace())
fd(0)