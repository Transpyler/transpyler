import time as _time

_b_alias = lambda x, **kwargs: x
_example = lambda x, doc: x

# -----------------------------------------------------------------------------
# Time control
sleep = _time.sleep
exit = exit

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
integer = _b_alias(int)
real = _b_alias(float)
complex = _b_alias(complex)
boolean = _b_alias(bool)
binary = _b_alias(bin)
octal = _b_alias(oct)
hexadecimal = _b_alias(hex)
character = _b_alias(chr)

# -----------------------------------------------------------------------------
# Sequence operations
enumeration = _b_alias(
    lambda x, start=0: list(enumerate(x, start=0)),
    example= \
        """
        >>> music = ['uni', 'duni', 'te']
        >>> enumeration(música))
        [(0, 'uni'), (1, 'duni'), (2, 'te')]
        """
)

length = _b_alias(
    len,
    example= \
        """
        >>> L = [1, 2, 3, 4]
        >>> length(L)
        4
        """
)
enumerate = _b_alias(lambda x: list(enumerate))

inverted = _b_alias(
    lambda x: list(reversed(x)),
    example= \
        """
        >>> música = ['uni', 'duni', 'te']
        >>> listar_invertido(música)
        ['te', 'duni', 'uni']
        """
)

sorted = _b_alias(
    sorted,
    example= \
        """
        >>> sorted([5, 2, 3, 1, 4])
        [1, 2, 3, 4, 5]
        """,
)

# -----------------------------------------------------------------------------
# Builtin types
Dictionary = _b_alias(
    dict,
    aliases=('dictionary'),
    example= \
        """
        >>> dictionary([(0, 'zero'), (1, 'um'), (2, 'dois')])
        {0: 'zero', 1: 'um', 2: 'dois'}
        """,
)

Tuple = _b_alias(
    tuple,
    example= \
        """
        >>> tupla([1, 2, 3])
        (1, 2, 3)
        """,
)

List = _b_alias(
    list,
)

String = _b_alias(
    str,
    aliases=('string',),
    example= \
        """
        >>> string(42)
        '42'
        """
)

# -----------------------------------------------------------------------------
# Other functions
type = _b_alias(type)
help = _b_alias(help)

# Singleton objects
verdadeiro = Verdadeiro = True
falso = Falso = False
nulo = Nulo = None
