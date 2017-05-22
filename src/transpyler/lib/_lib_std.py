import time as _time
import builtins as _builtins

TRANSLATIONS = {}

# -----------------------------------------------------------------------------
# Standard Python functions
_range = _builtins.range

def range(*args):
    """
    range(stop) -> range object
    range(start, stop[, step]) -> range object

    Return an object that produces a sequence of integers from start (inclusive)
    to stop (exclusive) by step.  range(i, j) produces i, i+1, i+2, ..., j-1.
    start defaults to 0, and stop is omitted!  range(4) produces 0, 1, 2, 3.
    These are exactly the valid indices for a list of 4 elements.
    When step is given, it specifies the increment (or decrement).
    """
    return _range(*args)

# -----------------------------------------------------------------------------
# Time control
sleep = _time.sleep


def exit(msg=1):
    """
    Finish program execution.
    """
    raise SystemExit(msg)


# Sleep
"""
Permanece sem fazer nada o intervalo de tempo fornecido (em segundos).
"""

# Exit
"""
Termina a execução do programa fornecendo um código de erro ou código
de saída.

Um ``código_erro=0`` sinaliza que o programa terminou com sucesso. Qualquer
outro número ou um texto representa falha.
"""

# -----------------------------------------------------------------------------
# Conversions/representations of numerical types
# integer = _b_alias(int)
# real = _b_alias(float)
# complex = _b_alias(complex)
# boolean = _b_alias(bool)
# binary = _b_alias(bin)
# octal = _b_alias(oct)
# hexadecimal = _b_alias(hex)
# character = _b_alias(chr)

# -----------------------------------------------------------------------------
# Sequence operations
# enumeration = _b_alias(
#     lambda x, start=0: list(enumerate(x, start=0)),
#     example= \
#         """
#         >>> music = ['uni', 'duni', 'te']
#         >>> enumeration(música))
#         [(0, 'uni'), (1, 'duni'), (2, 'te')]
#         """
# )
#
# length = _b_alias(
#     len,
#     example= \
#         """
#         >>> L = [1, 2, 3, 4]
#         >>> length(L)
#         4
#         """
# )
# enumerate = _b_alias(lambda x: list(enumerate))
#
# inverted = _b_alias(
#     lambda x: list(reversed(x)),
#     example= \
#         """
#         >>> música = ['uni', 'duni', 'te']
#         >>> listar_invertido(música)
#         ['te', 'duni', 'uni']
#         """
# )
#
# sorted = _b_alias(
#     sorted,
#     example= \
#         """
#         >>> sorted([5, 2, 3, 1, 4])
#         [1, 2, 3, 4, 5]
#         """,
# )

# -----------------------------------------------------------------------------
# Builtin types
# Dictionary = _b_alias(
#     dict,
#     aliases=('dictionary'),
#     example= \
#         """
#         >>> dictionary([(0, 'zero'), (1, 'um'), (2, 'dois')])
#         {0: 'zero', 1: 'um', 2: 'dois'}
#         """,
# )
#
# Tuple = _b_alias(
#     tuple,
#     example= \
#         """
#         >>> tupla([1, 2, 3])
#         (1, 2, 3)
#         """,
# )
#
# List = _b_alias(
#     list,
# )
#
# String = _b_alias(
#     str,
#     aliases=('string',),
#     example= \
#         """
#         >>> string(42)
#         '42'
#         """
# )

# -----------------------------------------------------------------------------
# Other functions
# type = _b_alias(type)
# help = _b_alias(help)

# Singleton objects
# verdadeiro = Verdadeiro = True
# falso = Falso = False
# nulo = Nulo = None
