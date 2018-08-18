import tokenize

from transpyler.token import Token, TokenPosition


class TestToken:
    def test_create_token(self):
        tk = Token('(', start=(0, 0))
        assert tk.string == '('
        assert tk.type == tokenize.OP  # Python do not createLPAR tokens.
        assert tk.start == (0, 0)
        assert tk.end == (0, 1)
        assert tk.line == None
        assert tk == Token(tk)

    def test_creat_special_tokens(self):
        assert Token('name', start=(0, 0)).type == tokenize.NAME
        assert Token('42', start=(0, 0)).type == tokenize.NUMBER
        assert Token('*', start=(0, 0)).type == tokenize.OP

    def test_token_repr(self):
        tk = Token('tok', start=(0, 0))
        assert repr(tk) == "NAME('tok')"
        assert str(tk) == "Token('tok', NAME, (0, 0), (0, 3), None)"

    def test_token_as_sequence(self):
        tk = Token('tok', start=(0, 0))
        assert len(tk) == 5
        assert list(tk) == ['tok', tokenize.NAME, (0, 0), (0, 3), None]

    def test_create_list_of_tokens(self):
        tk1, tk2, tk3 = Token.from_strings((1, 1), 'x', '=', '42')

        assert tk1.string == 'x'
        assert tk2.string == '='
        assert tk3.string == '42'

        assert tk1.start == (1, 1)
        assert tk2.start == (1, 2)
        assert tk3.start == (1, 3)


class TestTokenPosition:
    def test_token_pos_arithmetic(self):
        pos = TokenPosition(2, 1)
        assert pos.lineno == 2
        assert pos.col == 1
        assert pos == (2, 1)
        assert pos + (1, 1) == (3, 2)
        assert [1, 1] + pos == (3, 2)
        assert pos - (1, 1) == (1, 0)
        assert [3, 2] - pos == (1, 1)
