import os
import re

import click


#
# Utilities
#
@click.command()
def potfile():
    """
    Updates Transpyler lib main potfile.

    You probably have little use for this command unless you are a Transpyler
    developer.
    """
    from transpyler import lib
    from transpyler.translate import L10N_PATH
    from transpyler.utils import extract_namespace
    from transpyler.translate import extract_translations
    from transpyler.translate import create_pot_file
    from transpyler.turtle.namespace import TurtleNamespace

    path = os.path.join(L10N_PATH, 'transpyler.pot')
    click.echo('Updating transpyler.pot file at:\n    %s' % path)

    namespace = extract_namespace(lib)
    namespace.update(TurtleNamespace())
    translations = extract_translations(namespace)
    create_pot_file(translations, path)

    click.echo('\nCreated potfile with %s translations!' % len(translations))
    click.echo('Please review the translation files for specific languages.')
    for path in os.listdir(L10N_PATH):
        path = os.path.basename(path)
        if re.match(r'^[a-z][a-z](_[A-Z][A-Z])?\.po$', path):
            click.echo('    * ' + path)


@click.command()
@click.argument('lang')
@click.option('--auto/--no-auto', default=True,
              help='Do not prompt for translation.')
def autotranslate(lang, auto):
    """
    Fill translations in a PO file using google translate.
    """
    from transpyler.translate.google_translate import google_translate

    lang = lang.replace('-', '_')
    google_translate(lang, prompt=not auto, verbose=True)


#
# Group commands
#
@click.group()
def cli():
    "Entry point for several Transpyler cli commands"


cli.add_command(potfile)
cli.add_command(autotranslate)

if __name__ == '__main__':
    cli()
