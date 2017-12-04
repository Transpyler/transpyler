"""
A turtle library with a client/server architecture.

The turtle client is responsible for issuing commands that are serialized and
sent to a turtle server. The server stores the state of the turtles and
can send messages the tell the client how to update its display.

In the simple case, both the server and the client run on the same machine and
"message passing" is a simple method call. The client and server can live on
different processes, different machines and can even be implemented in different
languages.

We have a few use cases:

* Implement turtle commands in a Jupyter architecture: the server runs in the
  kernel process and the client runs in the shell process.
* Jupyter notebooks: similar as above, but messages can be redirect to
  javascript to update a canvas object that display the different turtles.
* It should be possible to choose different frontend toolkits. Tk does not
  capture the main thread, but Qt does. We would like to support both
  archtectures.
* The "draw" messages can be stored and saved in a persistent structure. This
  can be used to generate output in static file formats or even to implement an
  online judge for turtle-based programs.


.. autoclass:: transpyler.turtle.Turtle
    :members:

.. autoclass:: transpyler.turtle.turtleState
    :members:
"""

from .turtle import Turtle
from .turtlegroup import TurtleGroup
from .namespace import TurtleNamespace
from .turtleState import TurtleState
from .stategroup import StateGroup, IpcStateGroup
from .propertyState import PropertyState
from .remoteState import RemoteState
from .mirrorState import MirrorState
from .mailboxState import MailboxState
