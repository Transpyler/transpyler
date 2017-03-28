import code
import sys
import traceback

from lazyutils import lazy


class TranspylerConsole(code.InteractiveConsole):
    """
    Very simple console for Transpyled languages.
    """

    language_class = None

    @lazy
    def language(self):
        return self.language_class()

    def __init__(self, locals=None, filename='<console>', language=None):
        if language is not None:
            self.language = language
        locals = locals if locals is not None else {}
        locals.update(self.language.get_builtins_namespace())
        super().__init__(locals, filename)

    def runsource(self, source, filename="<input>", symbol="single"):
        try:
            source = self.language.transpile(source)
            if source.endswith('\n'):
                source = source[:-1]
            code = self.compile(source, filename, symbol)
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            print(source)
            self.showsyntaxerror(filename)
            return False

        if code is None:
            # Case 2
            return True

        # Case 3
        self.runcode(code)
        return False

    def runcode(self, code):
        if isinstance(code, str):
            code = self.language.transpile(code)
        super().runcode(code)

    def showsyntaxerror(self, filename=None):
        type, value, tb = sys.exc_info()
        sys.last_type = type
        sys.last_value = value
        sys.last_traceback = tb

        if filename and type is SyntaxError:
            # Work hard to stuff the correct filename in the exception
            try:
                msg, (dummy_filename, lineno, offset, dummy_line) = value.args
            except ValueError:
                # Not the format we expect; leave it alone
                pass
            else:
                # Stuff in the right filename and line
                print(self.buffer, lineno)
                line = dummy_line
                value = SyntaxError(msg, (filename, lineno, offset, line))
                sys.last_value = value
        if sys.excepthook is sys.__excepthook__:
            lines = traceback.format_exception_only(type, value)
            self.write(''.join(lines))
        else:
            # If someone has set sys.excepthook, we let that take precedence
            # over self.write
            sys.excepthook(type, value, tb)

    def interact(self, banner=None, exitmsg=None):
        """
        Starts the console mainloop.
        """

        self.language.init()
        super().interact(banner, exitmsg)


def run_console(language=None, banner=None):
    """
    Run the main console.
    """

    console = TranspylerConsole(language=language)
    try:
        import readline
    except ImportError:
        pass
    if banner is None:
        banner = language.get_console_banner()
    console.interact(banner)


if __name__ == '__main__':
    run_console()
