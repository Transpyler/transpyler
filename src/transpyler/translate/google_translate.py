import os

import polib
from textblob import TextBlob as Blob
from textblob.exceptions import NotTranslated

from .gettext import L10N_PATH, PO_HEADER
from ..utils.string import split_docstring


def google_translate(lang, verbose=True, prompt=True):
    """
    Fill translations for the given PO file using google translate.
    """

    # Utility functions
    echo = print if verbose or prompt else lambda *args, **kwargs: None
    ask = _ask(verbose, prompt)
    showline = _showline(verbose, prompt)

    # Prepare
    popath = os.path.join(L10N_PATH, lang + '.po')
    if os.path.exists(popath):
        echo('Loading file: %r' % popath, '\n\n')
    else:
        echo('Creating file: %r' % popath, '\n\n')
        potpath = os.path.join(L10N_PATH, 'transpyler.pot')
        save_po_file(potpath, popath, lang)
    pofile = polib.pofile(popath)

    translator = GoogleTranslator(lang)

    # Mainloop: handle all missing translations and pass them to google
    # translate
    for entry in pofile:
        if entry.msgstr:
            continue

        echo('\n'.join('#. ' + line for line in entry.comment.splitlines()))
        echo(entry.msgid)
        if ask():
            id = entry.comment.rpartition('.')[-1]
            entry.msgstr = translator(entry.msgid, id)
            entry.flags.append('fuzzy')

            # Show message
            showline()
            echo('\nTRANSLATION\n')
            echo(entry.msgstr)
            showline()

            # Save
            pofile.save()


def save_po_file(potpath, popath, lang):
    """
    Saves .po file using data from potfile and language.
    """

    with open(popath, 'w', encoding='utf-8') as F:
        F.write(PO_HEADER % lang.replace('-', '_'))

        with open(potpath, encoding='utf8') as Fpot:
            save = False
            for line in Fpot.readlines():
                if save:
                    F.write(line)
                elif line.isspace():
                    save = True


def _showline(verbose, prompt):
    return lambda: \
        print('\n' + '-' * 40) if verbose or prompt else lambda: None


def _ask(verbose, prompt):
    return lambda: (
        input('\nTranslate? [Y/n]').lower() in ('y', '')
        if prompt else lambda: True
    )


class GoogleTranslator:
    """
    A namespace with utility functions used to implement translations with
    google translate.
    """

    def __init__(self, lang):
        self.lang = lang
        self.google_lang = lang.replace('_', '-')

    def __call__(self, text, id):
        map = {
            'doc': self.translate_doc,
            'name': self.translate_name,
            'args': self.translate_args,
        }
        return map.get(id, self.google_translate)(text)

    def google_translate(self, x):
        if not x:
            return ''
        try:
            result = '%s' % Blob(x).translate('en', self.google_lang)
        except NotTranslated:
            result = x

        if x[0].isupper():
            return result
        else:
            return result[0].lower() + result[1:]

    def translate_doc(self, text):
        sections = []
        for section in split_docstring(text):
            translated = self.google_translate(section)
            sections.append(translated)
        return '\n\n'.join(map(lambda x: '%s' % x, sections))

    def translate_name(self, name):
        translated = self.google_translate(name.replace('_', ' '))
        if name.islower():
            translated = translated.lower()
        elif name[0].islower():
            translated = translated[0].lower() + translated[1:]
        return translated.replace(' ', '_').replace('-', '_')

    def translate_args(self, text):
        return ', '.join(map(self.translate_name, text.split(',')))
