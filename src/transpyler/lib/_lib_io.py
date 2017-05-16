from ._lib_str import format_string as _format_string


def show(*args):
    """
    Shows the object or text provided on the screen.

    If called with multiple arguments, prints them in sequence, separating
    them with a white space.

    Examples:
        >>> show("Hello world!")
        Hello World!
    """

    print(*args)


def alert(*args):
    """
    Similar to the `show` function, but displays the resulting message in a
    dialog box.
    """

    _alert(*args)


def fshow(text, *args, **kwargs):
    """
    Displays a string after applying the provided formatting arguments.
    """

    show(_format_string(text, *args, **kwargs))


def read_text(message=''):
    """
    Prompts the user for a text entry.

    Examples:
        >>> name = read_text('Your name:')
        >>> show("Hello," + name)  # the user types "Maria"
        Hello Maria
    """

    if isinstance(message, str) and message:
        message = (message + ' ') if not message.endswith(' ') else message
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
    num = float(text.replace(',', '.'))
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


# These functions can be replaced/mocked by the Qt GUI and have a proper
# behavior in a graphical environment or in tests.
def _pause():
    """
    Press <return> to continue
    """
    read_text(_pause.__doc__.strip())


def _alert(*args):
    show(*args)


def _input(*args):
    return input(*args)


def _filechooser(do_open):
    """
    File name:
    """
    return read_text(_filechooser.__doc__.strip() + ' ')
