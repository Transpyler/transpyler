from ..transpyler import SingletonTranspyler


# Executes using the global default transpyler instance
if __name__ == '__main__':
    transpyler = SingletonTranspyler.getInstance()
    transpyler.start_console('jupyter', 'tk')
