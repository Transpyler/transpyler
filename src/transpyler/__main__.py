import os

import click

import transpyler.utils.namespaces


#
# Utilities
#
@click.command()
def potfile():
    """
    Updates Transpyler lib main potfile.

    You probably has little use for this command unless you are a Transpyler
    developer.
    """
    import transpyler.utils.translate as mod

    click.echo('Updating transpyler.pot file...', nl=False)

    path = os.path.join(mod.I10N_PATH, 'transpyler.pot')
    names = transpyler.utils.namespaces.collect_mod_namespace()
    translations = mod.extract_translations(names)
    mod.create_pot_file(translations, path)

    click.echo(' Done!')


@click.command()
@click.argument('lang')
@click.option('--auto/--no-auto', default=True,
              help='Do not prompt for translation.')
def autotranslate(lang, auto):
    """
    Fill translations in a PO file using google translate.
    """
    from transpyler.utils.translate import google_translate

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
