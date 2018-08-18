from transpyler.turtle.namespace import TurtleNamespace


class TestTurtleNamespace:
    def test_namespace_acts_like_a_dict(self):
        ns = TurtleNamespace()
        assert hasattr(ns, 'items')
        assert 'forward' in ns
        assert set(ns) == {
            'Turtle', 'back', 'backward', 'bk', 'fd', 'forward',
            'getavatar', 'getcolor', 'getfillcolor', 'getheading', 'getpos',
            'getwidth', 'goto', 'hide', 'isdown', 'ishidden', 'isvisible',
            'jump', 'left', 'lt', 'mainturtle', 'pd', 'pendown', 'penup', 'pu',
            'reset', 'right', 'rt', 'setavatar', 'setcolor', 'setfillcolor',
            'setheading', 'setpos', 'setwidth', 'show', 'setspeed', 'getspeed',
            'clean',
        }
