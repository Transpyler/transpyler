import tokenize
from functools import singledispatch
from token import OP, NAME, NUMBER
from tokenize import TokenInfo, EXACT_TOKEN_TYPES

TOKEN_TYPE_NAME = {tt: attr for (attr, tt) in vars(tokenize).items()
                   if attr.isupper() and isinstance(tt, int)}


class Token:
    """
    Mutable token object.
    """

    @classmethod
    def from_strings(cls, start, *strings):
        """
        Return a list of tokens that begins at the given starting point. The
        resulting token elements have consistent start/end positions.
        """

        tk_list = []
        start = token_position(start)
        is_fragile = False
        for string in strings:
            if is_fragile and string.isidentifier():
                start += (0, 1)
            tok = Token(string, start=start)
            start = tok.end
            is_fragile = string.isidentifier()
            tk_list.append(tok)
        return tk_list

    def __init__(self, data, type=None, start=None, end=None, line=None,
                 abstract=False):

        data, type, start, end, line = token_args(data, type, start, end, line)

        # Fix start and end positions
        start = token_position(start)
        if start is not None:
            if end is None:
                if '\n' not in data:
                    end = start + (0, len(data))
                else:
                    lineno = end.lineno + end.count('\n')
                    col = len(data.rpartition('\n')[-1])
                    end = token_position(lineno, col)
        end = token_position(end)

        # We are not using exact token types: the tokenizer converts many
        # tokens to OP that should be other values.
        if type is None:
            type = infer_type(data)

        # Error checks
        if not abstract and None in (start, end):
            msg = 'unable to define start/end of concrete token'
            raise ValueError(msg)
        if abstract and (start, end) != (None, None):
            msg = 'cannot define start/end positions of abstract token'
            raise ValueError(msg)

        # Save data
        self.string = data
        self.type = type
        self.start = start
        self.end = end
        self.line = line

    def __eq__(self, other):  # noqa: C901
        if isinstance(other, Token):
            if self.string is None or other.string is None:
                return self.type == other.type

            if self.string != other.string or self.type != other.type:
                return False

            for (x, y) in [(self.start, other.start),
                           (self.end, other.end),
                           (self.line, other.line)]:
                if x != y and None not in (x, y):
                    return False
            return True
        elif isinstance(other, (str, TokenInfo)):
            return self == Token(other)
        elif isinstance(other, (tuple, list)):
            if len(other) == 2:
                return self.string == other[0] and self.type == other[1]
            return self == Token(*other)
        else:
            return NotImplemented

    def __str__(self):
        return 'Token(%r, %s, %r, %r, %r)' % (
            self.string, TOKEN_TYPE_NAME[self.type],
            self.start, self.end, self.line)

    def __repr__(self):
        tname = TOKEN_TYPE_NAME[self.type]
        if self.string.isspace():
            return tname
        else:
            return '%s(%r)' % (tname, self.string)

    def __len__(self):
        return 5

    def __getitem__(self, idx):
        if idx == 0:
            return self.string
        elif idx == 1:
            return self.type
        elif idx == 2:
            return self.start
        elif idx == 3:
            return self.end
        elif idx == 4:
            return self.line
        elif -5 <= idx < 0:
            return self[5 + idx]
        else:
            raise IndexError(idx)

    def __iter__(self):
        yield from (self[i] for i in range(5))

    def to_token_info(self):
        """
        Convert to TokenInfo object used by Python's tokenizer.
        """

        return TokenInfo(
            self.type, self.string, self.start, self.end, self.line
        )

    def displace(self, cols):
        """
        Displace token in line by cols columns to the right.
        """

        self.start += (0, cols)
        if self.end.lineno == self.start.lineno:
            self.end += (0, cols)


#
# Represents a position in the source code
#
class TokenPosition(tuple):
    """
    Represent the start or end position of a token and accept some basic
    arithmetic operations
    """

    def __new__(cls, x, y=None):
        if y is None:
            x, y = x
        return tuple.__new__(cls, [x, y])

    def __init__(self, x, y=None):
        super().__init__()

    def __add__(self, other):
        x, y = self
        a, b = other
        return TokenPosition(x + a, y + b)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        x, y = self
        a, b = other
        return TokenPosition(x - a, y - b)

    def __rsub__(self, other):
        x, y = self
        a, b = other
        return TokenPosition(a - x, b - y)

    @property
    def lineno(self):
        return self[0]

    @property
    def col(self):
        return self[1]


#
# Normalize token input arguments
#
@singledispatch
def token_args(data, type, start, end, line):
    return data, type, start, end, line


@token_args.register(TokenInfo)
def _token_info(info, type, start, end, line):
    if not all(x is None for x in [type, start, end, line]):
        raise ValueError('cannot specify argument when starting with TokenInfo')
    type, data, start, end, line = info
    return data, type, start, end, line


@token_args.register(Token)
def _token(data, type, start, end, line):
    if not all(x is None for x in [type, start, end, line]):
        raise ValueError('cannot specify argument when starting with Token')
    return data


@token_args.register(int)
def _type_code(tt, type, start, end, line):
    type = tt
    data = None
    return data, type, start, end, line


def token_position(pos):
    return None if pos is None else TokenPosition(pos)


def infer_type(data):
    if data in EXACT_TOKEN_TYPES:
        return OP
    else:
        if data.isidentifier():
            return NAME
        elif data.isdigit():
            return NUMBER
        else:
            raise TypeError('could not recognize token: %r' % data)


#
# Transformations over a list of tokens
#
def displace_tokens(tokens, cols):
    """
    Displace all tokens in list which are in the same line as the the first
    token by the given number of columns
    """

    if not tokens or cols == 0:
        return
    lineno = tokens[0].start.lineno

    for token in tokens:
        if token.start.lineno == lineno:
            token.displace(cols)
        else:
            break


def insert_tokens_at(tokens, idx, new_tokens, end=None):
    """
    Insert new_tokens at tokens list at the given idx
    """

    if end is not None:
        linediff, col = new_tokens[-1].end - end
        if linediff == 0 and end.lineno == tokens[idx].start.lineno:
            displace_tokens(tokens[idx:], col)

    for tk in new_tokens:
        tokens.insert(idx, tk)
        idx += 1


def token_find(tokens, matches, start=0):
    """
    Iterate over list of tokens yielding (index, match, start, end) for
    each match in the token stream. The `matches` attribute must be a sequence
    of token sequences.
    """

    matches = list(matches)
    tk_matches = \
        [tuple(Token(tk, abstract=True) for tk in seq) for seq in matches]
    tk_matches = \
        [tuple((tk.string, tk.type) for tk in seq) for seq in tk_matches]
    tk_idx = start

    while tk_idx < len(tokens):
        for match_idx, tkmatch in enumerate(tk_matches):
            if tk_idx + len(tkmatch) > len(tokens):
                continue

            if all(tokens[tk_idx + k] == tk for (k, tk) in enumerate(tkmatch)):
                matchsize = len(tkmatch)

                # Yield value and try to receive commands from sender
                start = tokens[tk_idx].start
                end = tokens[tk_idx + matchsize - 1].end
                yield (tk_idx, matches[match_idx], start, end)
                tk_idx += 1
        tk_idx += 1
    return
