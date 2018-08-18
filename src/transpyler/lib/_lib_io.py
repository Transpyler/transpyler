import builtins as _builtins

from ._lib_str import format_string as _format_string
from ..translate import gettext as _


def print(*args, **kwargs):
    """
    Prints the object or text provided on the screen.

    If called with multiple arguments, prints them in sequence, separating
    them with a white space.

    Examples:
        >>> print("Hello world!")
        Hello World!
    """

    _print(*args, **kwargs)


def alert(*args, **kwargs):
    """
    Similar to the `show` function, but displays the resulting message in a
    dialog box.
    """

    _alert(*args, **kwargs)


def print_formatted(text, *args, **kwargs):
    """
    Displays a string after applying the provided formatting arguments.
    """

    print(_format_string(text, *args, **kwargs))


def read_text(message=''):
    """
    Prompts the user for a text entry.

    Examples:
        >>> name = read_text('Your name:')
        >>> show("Hello," + name)  # the user types "Maria"
        Hello Maria
    """

    message = str(message or _('Input:'))
    message = (message + ' ') if message[-1] not in ' \n\t\r' else message
    return _input(message)


def read_number(message=''):
    """
    Prompts the user for a numeric entry.

    Examples:
        >>> x = read_number('A number:')  # user types 2...
        >>> x + 40
        42
    """

    text = read_text(message)
    while True:
        try:
            num = float(text.replace(',', '.'))
        except ValueError:
            _print(_('Invalid number: {text}').format(text=text))
            return read_number(message)
        else:
            return int(num) if int(num) == num else num


def read_file(file=None):
    """
    Reads the content from a text file and returns it as string.

    Examples:
        >>> data = read_file("foo.txt")
    """

    if file is None:
        file = _filechooser(True)
    return open(file).read()


def save_in_file(text, file=None):
    """
    Saves the text content to the indicated file, deleting any previous content.

    WARNING! If the given file exists, this function will overwrite your
    content without asking!

    Examples:
        >>> save_in_file(data, "foo.txt")
    """

    if file is None:
        file = _filechooser(False)

    with open(file) as F:
        F.write(str(text))


def pause():
    """
    Stops execution until the user presses the <return> key.
    """
    _pause()


# These functions can be replaced/mocked and have a proper behavior in a
# graphical environment or in tests.
_print = _builtins.print


def _pause():
    """
    Press <return> to continue
    """
    read_text(_pause.__doc__.strip())


def _alert(*args):
    print(*args)


def _input(*args):
    return input(*args)


def _filechooser(do_open):
    """
    File name:
    """
    return read_text(_filechooser.__doc__.strip() + ' ')
