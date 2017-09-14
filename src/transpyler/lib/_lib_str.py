def concatenate(*args):
    """
    Convert argument to string and concatenate.

    If only one argument is passed, assumes it is a sequence.

    Examples:
        >>> concatenate('x = ', 2)
        'x = 2'
        >>> concatenate([1, 2, 3, 4])
        '1234'
    """

    return join('', *args)


def join(separator, *args):
    """
    Similar to concatenate(), but takes an extra separator as first argument
    argument.

    Examples:
        >>> join(', ', 1, 2, 3)
        '1, 2, 3'
    """

    if not args:
        return ''

    if len(args) == 1:
        args = args[0]

    return str(separator).join(map(str, args))


def format_string(string, *args, **kwargs):
    """
    Format text inserting parameters in the wildcard positions.

    There are two different syntax for string formatting. The first is based
    on C and uses symbols such as %s, %f, %d to delimit insertion points.

    >>> format_string('%i != %.2f', 42, 43)
    '42 != 43.00'

    The second uses curly braces.

    >>> format_string('{0} != {1}', 42, 43)
    '42 != 43'
    """

    try:
        return string % args
    except TypeError:
        return string.format(*args, **kwargs)
