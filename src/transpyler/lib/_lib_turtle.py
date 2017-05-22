from transpyler.turtle.turtle import Turtle

TRANSLATIONS = {}
_mainturtle = None


def _from_turtle(method: callable):
    from functools import wraps

    name = method.__name__

    @wraps(method)
    def func(*args, **kwargs):
        turtle = mainturtle()
        return getattr(turtle, name)(*args, **kwargs)

    return func


def mainturtle():
    """
    Returns the main turtle object.
    """

    global _mainturtle
    if _mainturtle is None:
        _mainturtle = Turtle()
    return _mainturtle


getpos = _from_turtle(Turtle.getpos)
setpos = _from_turtle(Turtle.setpos)
getheading = _from_turtle(Turtle.getheading)
setheading = _from_turtle(Turtle.setheading)
getwidth = _from_turtle(Turtle.getwidth)
setwidth = _from_turtle(Turtle.setwidth)
getcolor = _from_turtle(Turtle.getcolor)
setcolor = _from_turtle(Turtle.setcolor)
getfillcolor = _from_turtle(Turtle.getfillcolor)
setfillcolor = _from_turtle(Turtle.setfillcolor)
getavatar = _from_turtle(Turtle.getavatar)
setavatar = _from_turtle(Turtle.setavatar)
penup = _from_turtle(Turtle.penup)
pendown = _from_turtle(Turtle.pendown)
isdown = _from_turtle(Turtle.isdown)
isvisible = _from_turtle(Turtle.isvisible)
ishidden = _from_turtle(Turtle.ishidden)
hide = _from_turtle(Turtle.hide)
show = _from_turtle(Turtle.show)
clear = _from_turtle(Turtle.clear)
reset = _from_turtle(Turtle.reset)
goto = _from_turtle(Turtle.goto)
jump = _from_turtle(Turtle.jump)
forward = _from_turtle(Turtle.forward)
backward = _from_turtle(Turtle.backward)
left = _from_turtle(Turtle.left)
right = _from_turtle(Turtle.right)
