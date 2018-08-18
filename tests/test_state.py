import pytest

from transpyler.turtle.state import TurtleState

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

"""
    Function not implemented draw_line

def test_move(turtle_state):
    turtle_state.pos == (0, 0)
    turtle_state.move(100)
    assert turtle_state.pos == (100, 0)
"""



        