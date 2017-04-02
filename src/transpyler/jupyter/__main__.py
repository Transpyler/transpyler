from transpyler.jupyter import start_shell
from ..transpyler import get_default_transpyler


# Executes using the global default transpyler instance
if __name__ == '__main__':
    transpyler = get_default_transpyler()
    start_shell(transpyler)