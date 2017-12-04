import pytest
import warnings
from transpyler.turtle.turtleState import TurtleState

@pytest.fixture
def turtle_state():
    trans = TurtleState()
    return trans

def test_init(turtle_state):
    assert isinstance(turtle_state, TurtleState)
    assert turtle_state.pos == (0,0)
    assert turtle_state.heading == 0.0
    assert turtle_state.drawing == True
    assert turtle_state.color == 'black'
    assert turtle_state.fillcolor == 'black'
    assert turtle_state.width == 1
    assert turtle_state.hidden == False
    assert turtle_state.avatar == 'default'
    assert turtle_state.group == None
    assert turtle_state.id == None

def test_heading_direction(turtle_state):
    assert turtle_state.heading_direction == (1, 0)
    # Turtle starting angle: 0 degrees

def test_validate_avatar(turtle_state):
    assert turtle_state.validate_avatar('default') == None
    try:
        turtle_state.validate_avatar('')
        assert False
    except ValueError:
        assert True

def test_rotate(turtle_state):
    turtle_state.heading == 0.0
    turtle_state.rotate(1.0)
    assert turtle_state.heading == 1.0

def test_move(turtle_state):
    try:
        turtle_state.move(100)
        assert False
    except NotImplementedError:
        assert True

def test_step(turtle_state):
    try:
        turtle_state.step(100)
        assert False
    except NotImplementedError:
        assert True

def test_clear(turtle_state):
    turtle_state.lines = [1]
    turtle_state.lines.clear()
    assert turtle_state.lines == []

def test_reset(turtle_state):
    turtle_state.lines = [1]
    turtle_state.pos = (100)
    turtle_state.heading = (1.1)
    turtle_state.drawing = False
    turtle_state.reset()
    assert turtle_state.lines == []
    assert turtle_state.pos == (0,0)
    assert turtle_state.drawing == True

def test_draw_line(turtle_state):
    try:
        turtle_state.draw_line(1,1)
        assert False
    except NotImplementedError:
        assert True

def test_register(turtle_state):
    turtle_state.register("pytuga")
    assert turtle_state.group == "pytuga"
    
def test_recv(turtle_state):
    try:
        turtle_state.recv()
        assert False
    except NotImplementedError:
        assert True
