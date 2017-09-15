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
    echo = print \
        if verbose or prompt else lambda *args, **kwargs: None

    def showline():
        return print('\n' + '-' * 40) \
            if verbose or prompt else lambda: None

    def ask():
        return input('\nTranslate? [Y/n]').lower() in ('y', '') \
            if prompt else lambda: True

    # Prepare
    google_lang = lang.replace('_', '-')
    popath = os.path.join(L10N_PATH, lang + '.po')
    if os.path.exists(popath):
        echo('Loading file: %r' % popath, '\n\n')
        pofile = polib.pofile(popath)
    else:
        echo('Creating file: %r' % popath, '\n\n')
        with open(popath, 'w', encoding='utf-8') as F:
            F.write(PO_HEADER % lang.replace('-', '_'))

            potpath = os.path.join(L10N_PATH, 'transpyler.pot')
            with open(potpath, encoding='utf8') as Fpot:
                save = False
                for line in Fpot.readlines():
                    if save:
                        F.write(line)
                    elif line.isspace():
                        save = True

        pofile = polib.pofile(popath)

    # Translator functions
    def gtranslate(x):
        if not x:
            return ''
        try:
            result = '%s' % Blob(x).translate('en', google_lang)
        except NotTranslated:
            result = x

        if x[0].isupper():
            return result
        else:
            return result[0].lower() + result[1:]

    def translate(text, id):
        map = {
            'doc': translate_doc,
            'name': translate_name,
            'args': translate_args,
        }
        return map.get(id, gtranslate)(text)

    def translate_doc(text):
        sections = []
        for section in split_docstring(text):
            translated = gtranslate(section)
            sections.append(translated)
        return '\n\n'.join(map(lambda x: '%s' % x, sections))

    def translate_name(name):
        translated = gtranslate(name.replace('_', ' '))
        if name.islower():
            translated = translated.lower()
        elif name[0].islower():
            translated = translated[0].lower() + translated[1:]
        return translated.replace(' ', '_').replace('-', '_')

    def translate_args(text):
        return ', '.join(map(translate_name, text.split(',')))

    # Mainloop: handle all missing translations and pass them to google
    # translate
    for entry in pofile:
        if entry.msgstr:
            continue

        echo('\n'.join('#. ' + line for line in entry.comment.splitlines()))
        echo(entry.msgid)
        if ask():
            id = entry.comment.rpartition('.')[-1]
            entry.msgstr = translate(entry.msgid, id)
            entry.flags.append('fuzzy')

            # Show message
            showline()
            echo('\nTRANSLATION\n')
            echo(entry.msgstr)
            showline()

            # Save
            pofile.save()
