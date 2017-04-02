import json
import os
import tempfile
from contextlib import contextmanager

from transpyler.utils import full_class_name


class LanguageInfo:
    def __init__(self, transpyler):
        self.transpyler = transpyler

    def get_argv(self):
        """
        Return the list of arguments to be passed to initialize the kernel.
        """
        return [
            "python3", "-m", "transpyler.jupyter.kernel",
            "-f", "{connection_file}",
            "--type", full_class_name(type(self.transpyler)),
        ]

    def get_pygments_lexer(self):
        return 'ipython3'

    def get_kernel_spec(self):
        """
        Return the kernel spec as a JSON-like data.
        """

        transpyler = self.transpyler
        return {
            "argv": self.get_argv(),
            "display_name": transpyler.display_name,
            "language": transpyler.name,
            "codemirror_mode": transpyler.codemirror_mode,
            "language_info": {
                "name": transpyler.display_name,
                "codemirror_mode": {
                    "name": transpyler.codemirror_mode,
                },
                "mimetype": transpyler.mimetype,
                "pygments_lexer": self.get_pygments_lexer(),
            },
            "help_links": [
                {
                    "text": "Documentação do Pytuguês",
                    "link": "http://pytuga.readthedocs.io/pt/latest/"
                },
                {
                    "text": "Github",
                    "link": "http://github.com/transpyler/transpyler/"
                }
            ]
        }

    def get_assets(self):
        """
        Register a list of all assets available for the given kernel.
        """

        basedir = os.path.dirname(__file__)
        assets_dir = os.path.join(basedir, 'jupyter', 'assets')
        filenames = os.listdir(assets_dir)
        return [os.path.join(assets_dir, name) for name in filenames]

    @contextmanager
    def prepare_assets(self):
        """
        Creates a temporary directory with all assets.
        """

        temp = tempfile.mkdtemp()
        try:
            for asset in self.get_assets():
                name = os.path.split(asset)[-1]
                with open(asset, 'rb') as input:
                    with open(os.path.join(temp, name), 'wb') as output:
                        output.write(input.read())
            with open(os.path.join(temp, 'kernel.json'), 'w') as F:
                dump = json.dumps(self.get_kernel_spec(), indent=2)
                F.write(dump)
            yield temp
        finally:
            for file in os.listdir(temp):
                os.unlink(os.path.join(temp, file))
            os.rmdir(temp)