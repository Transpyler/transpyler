import gettext as _gettext
import os

import polib

L10N_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'l10n')
LANGUAGE = None
GETTEXT_INSTANCE = None
PO_HEADER = """#
msgid ""
msgstr ""
"Project-Id-Version: \\n"
"Language: %s\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"

"""


def gettext(x):
    """
    Translates string using the default language.
    """
    if LANGUAGE is None:
        return x
    return GETTEXT_INSTANCE.gettext(x)


def set_language(lang):
    """
    Sets the global output language for the transpyler environment.
    """
    global LANGUAGE, GETTEXT_INSTANCE

    LANGUAGE = lang.replace('-', '_')
    GETTEXT_INSTANCE = gettext_for(LANGUAGE)


def gettext_for(lang):
    """
    Return a GNUTranslation class for the given language.

    Example:
        >>> trans = gettext_for('pt_BR')
        >>> _ = trans.gettext
        >>> _('hello world!')                                   # doctest: +SKIP
        'olá mundo!'
    """
    lang = lang.replace('-', '_')

    try:
        with open(os.path.join(L10N_PATH, lang + '.mo'), 'rb') as F:
            result = _gettext.GNUTranslations(F)
    except FileNotFoundError:
        result = _gettext.NullTranslations()
    return result


def create_pot_file(translations, path=None):
    """
    Save contents on a POT file from a dictionary of (id, string) translation
    pairs.

    It interprets the id as a comment in the POT file and the string is the
    msgid field. The msgstr field is always empty.
    """

    pot = polib.POFile()
    pot.metadata = {
        'Project-Id-Version': '1.0',
        'Report-Msgid-Bugs-To': 'fabiomacedomendes@gmail.com',
        'MIME-Version': '1.0',
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Transfer-Encoding': '8bit',
    }

    # We keep a dictionary from msgids's to comments in order to keep all
    # entries unique. Duplicate entries simply duplicate comments
    entries = {}
    for key, data in translations.items():
        entry = polib.POEntry(msgid=data, comment=key)
        if data in entries:
            entries[data].comment += '\n' + key
        else:
            entries[data] = entry
            pot.append(entry)
    if path:
        pot.save(path)
    return pot
