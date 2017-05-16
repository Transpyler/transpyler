from transpyler.jupyter import start_shell
from ..transpyler import simple_transpyler


# Executes using the global default transpyler instance
if __name__ == '__main__':
    start_shell(simple_transpyler)
