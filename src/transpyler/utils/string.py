import re

SPACE_RE = re.compile('^[ ]*')
HEADING_SPACE = re.compile(r'^\s*')
ENDING_SPACE = re.compile(r'\s*$')


def humanize_name(name):
    """
    Convert a variable or class name to a version that a human can understand.

    Examples:
        >>> humanize_name('SomeName')
        'Some Name'
    """

    name = name.replace('_', ' ')
    letters = []
    for c in name:
        if c.isupper() and letters and letters[-1] != '_':
            letters.append('_' + c)
        else:
            letters.append(c)
    return ''.join(letters)


def unhumanize_name(name):
    """
    Revert the actions of humanize_name.
    """

    pieces = name.split()
    while len(pieces) > 1:
        if pieces[1][0].isupper():
            pieces[0] += pieces.pop(1)
        else:
            pieces[0] += '_' + pieces.pop(1)
    return pieces[0]


def keep_spaces(result, src):
    """
    Keep the same number of heading and trailing whitespace in result as
    compared to src.

    Example:
        >>> keep_spaces(' foo', 'bar\n\n')
        'foo\n\n'
    """

    if not src:
        return result.strip()

    # Find head and tail
    head = tail = ''
    if src[0].isspace():
        head = HEADING_SPACE.search(src).group()
    if src[-1].isspace():
        tail = ENDING_SPACE.search(src).group()
    return head + result.strip() + tail


def normalize_docstring(doc):
    """
    Normalize docstring.
    """

    doc = doc.strip().replace('\n\t', '\n    ')
    if not doc:
        return doc

    lines = doc.splitlines()
    indents = [SPACE_RE.match(line).span()[1] for line in lines]
    zipped = list(zip(indents, lines))

    if indents[0] == 0:
        zipped = zipped[1:]
    ind = min(zipped, default=(0, ''), key=lambda x: (x[0] if x[1] else 80))[0]

    for i, line in enumerate(lines):
        if i == 0 and indents[0] == 0:
            continue
        lines[i] = '' if not line.strip() else line[ind:]

    return '\n'.join(lines)
