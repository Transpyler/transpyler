from ..transpyler import get_transpyler


# Executes using the global default transpyler instance
if __name__ == '__main__':
    transpyler = get_transpyler()
    transpyler.start_console('jupyter')
