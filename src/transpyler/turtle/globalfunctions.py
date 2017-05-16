import operator as op

from transpyler.math import math_namespace


class GlobalFunctions:
    """
    Functions that affect the global state.
    """

    inbox = property(op.attrgetter('state_class.inbox'))
    outbox = property(op.attrgetter('state_class.outbox'))
    timeout = 1.0

    @classmethod
    def global_namespace(cls, math_functions=True, lang=None):
        """
        Return a namespace dictionary.
        """

        functions = cls(lang=lang)
        return functions.namespace(math_functions=math_functions)

    def __init__(self, lang=None):
        self.lang = lang

    def clear(self):
        """
        Clear all lines and drawings.
        """

        self.send(['clear'])

    def reset(self):
        """
        Clear and reset turtle position and drawing state.
        """

        self.send(['reset'])

    def namespace(self, math_functions):
        """
        Return a namespace dictionary with the global functions.
        """

        ns = {
            'clear': self.clear,
            'reset': self.reset,
        }
        if math_functions:
            ns.update(math_namespace(self.lang))
        return ns

    def send(self, msg):
        """
        Send message requesting execution of a global function.
        """

        raise NotImplementedError