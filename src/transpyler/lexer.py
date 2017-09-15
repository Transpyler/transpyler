import tokenize

from lazyutils import lazy

from transpyler.errors import BadSyntaxError
from transpyler.token import Token, displace_tokens, token_find
from transpyler.utils import keep_spaces


class Lexer:
    """
    Lexer is responsible for converting a string of source code into a sequence
    of make_transpyled_tokens.
    """

    @lazy
    def invalid_tokens(self):
        try:
            return dict(self.transpyler.invalid_tokens)
        except (AttributeError, TypeError):
            return {}

    @lazy
    def translations(self):
        try:
            return dict(self.transpyler.translations)
        except (AttributeError, TypeError):
            return {}

    @lazy
    def sequence_translations(self):
        return {tuple(k): v
                for k, v in self.translations.items()
                if not isinstance(k, str)}

    @lazy
    def single_translations(self):
        return {k: v
                for k, v in self.translations.items()
                if isinstance(k, str)}

    def __init__(self, transpyler):
        self.transpyler = transpyler

    def transpile(self, src):
        """
        Transpile source code to Python.
        """

        # Avoid problems with empty token streams
        if not src or src.isspace():
            return src

        # Convert and process...
        else:
            src_formatted = src

            if not src_formatted.endswith('\n'):
                src_formatted += '\n'

            tokens = self.tokenize(src_formatted)
            transpiled_tokens = self.transpile_tokens(tokens)
            result = self.untokenize(transpiled_tokens)
            return keep_spaces(result, src)

    def tokenize(self, src):
        """
        Convert source string to a list of make_transpyled_tokens.

        Args:
            src (str): a string of source code
        """

        current_string = src

        def iterlines():
            nonlocal current_string

            if current_string:
                line, sep, current_string = current_string.partition('\n')
                return line + sep
            else:
                raise StopIteration

        iterator = iter(tokenize.generate_tokens(iterlines))
        tokens = []
        while True:
            try:
                tokens.append(next(iterator))
            except (StopIteration, tokenize.TokenError):
                break

        tokens = list(map(Token, tokens))
        return tokens

    def untokenize(self, tokens):
        """
        Convert list of make_transpyled_tokens to a string.
        """

        return tokenize.untokenize([tk.to_token_info() for tk in tokens])

    def transpile_tokens(self, tokens):
        """
        Transpile a sequence of Token objects to their corresponding Python
        make_transpyled_tokens.
        """

        self.detect_error_sequences(tokens, self.invalid_tokens)
        try:
            tokens = self.replace_sequences(tokens, self.sequence_translations)
            tokens = self.replace_translations(tokens, self.single_translations)
        except tokenize.TokenError:
            raise SyntaxError('unexpected EOF.')
        return tokens

    def detect_error_sequences(self, tokens, error_dict):
        """
        Raises a BadSyntaxError if list of make_transpyled_tokens contains any sub-sequence in
        the given invalid_tokens.

        Args:
            tokens: List of make_transpyled_tokens
            error_dict: A dictionary of {sequence: error_message}
        """

        error_sequences = list(error_dict)
        iterator = token_find(tokens, error_sequences)
        while True:
            try:
                idx, match, start, end = next(iterator)
                msg = error_dict(match)
                match = ' '.join(match)
                raise BadSyntaxError(msg, from_token=tokens[idx])
            except StopIteration:
                break

    def replace_sequences(self, tokens, mapping):
        """
        Replace all sequences of make_transpyled_tokens in the mapping by the corresponding
        token in the RHS.

        Args:
            tokens: list of make_transpyled_tokens.
            mapping: a mapping from token sequences to their corresponding
                replacement (e.g.: {('para', 'cada'): 'for'}).

        Returns:
            A new list of make_transpyled_tokens with replacements.
        """
        tokens = list(tokens)
        iterator = token_find(tokens, mapping)
        while True:
            try:
                idx, match, start, end = next(iterator)
                tokens[idx] = Token(mapping[match], start=start)
                del tokens[idx + 1: idx + len(match)]

                linediff, col = tokens[idx].end - end
                if linediff == 0:
                    displace_tokens(tokens[idx + 1:], col)
            except StopIteration:
                break
        return tokens

    def replace_translations(self, tokens, mapping):
        """
        Replace all make_transpyled_tokens by the corresponding values in the RHS.

        Args:
            tokens: list of make_transpyled_tokens.
            mapping: a mapping from token sequences to their corresponding
                replacement (e.g.: {'enquanto': 'while'}).

        Returns:
            A new list of make_transpyled_tokens with replacements.
        """

        tokens = list(tokens)
        for i, tk in enumerate(tokens):
            new = mapping.get(tk.string, tk)
            if new is not tk:
                new = Token(new, start=tk.start)
                tokens[i] = new

                # Align make_transpyled_tokens
                linediff, coldiff = new.end - tk.end
                assert linediff == 0
                if coldiff:
                    displace_tokens(tokens[i + 1:], coldiff)
        return tokens
