import operator as op
from functools import wraps as _wraps

from transpyler.math import Vec as _Vec

COLORS = dict(
    preto='black', branco='white', vermelho='red', verde='green', azul='blue',
    amarelo='yellow',
)


def vecargsmethod(func):
    """
    Decorates a function of a vec object to accept the following signatures:

        func(vec, **kwds)
        func(x, y, **kwds)

    A Vec object is always passed to the given implementation.
    """

    @_wraps(func)
    def decorated(self, x, y=None, **kwds):
        if y is None:
            try:
                x, y = x
            except ValueError:
                raise ValueError('expected 2 elements, got %s' % len(x))

            return func(self, _Vec(x, y), **kwds)
        else:
            return func(self, _Vec(x, y), **kwds)

    return decorated


def alias(*args):
    """
    Set a list of function aliases for TurtleFunction methods.

    The aliases are automatically included in the resulting global_namespace.
    """

    def decorator(func):
        func.alias_list = args
        return func

    return decorator


def object_ctrl(getter, setter=None):
    def fget(self):
        return getattr(self.object, getter)()

    if setter is not None:
        def fset(self, value):
            getattr(self.object, setter)(value)

        return property(fget, fset)
    else:
        return property(fget)


def webcolor(color, source='pt_BR'):
    """
    Convert a color string back to a normalized english webcolor name.
    """

    color = color.lower().replace(' ', '')
    return COLORS.get(color, color)


def getsetter(name):
    """
    Return a property object that assigns that uses a (get*, set*) pair of
    methods.
    """

    getter = op.methodcaller('get' + name)
    setter = lambda x, v: setattr(x, 'set' + name, v)
    return property(getter, setter)


def turtle_property(getter, setter=None):
    """
    A property that uses getter/setters at .turtle.<getter> and .turtle.<setter>
    """

    fgetter = op.attrgetter('turtle.' + getter)
    fsetter = op.attrgetter('turtle.' + (setter or getter))

    def fget(x):
        return fgetter(x)()

    def fset(x, v):
        fsetter(x)(v)

    return property(fget, fset)


def ipc_property(name, unwrap=lambda x: x, wrap=lambda x: x):
    """
    A property that redirects requests to the getvalue/setvalue
    functions.
    """

    def fget(self):
        return unwrap(self.getvalue(name))

    def fset(self, value):
        self.setvalue(name, wrap(value))

    return property(fget, fset)
