from .translate.translate import translate_namespace

def make_global_namespace(lang):
    """
    Return a dictionary with the default global namespace for the
    transpyler runtime.
    """
    from transpyler import lib
    
    ns = extract_namespace(lib)

    # Load default translations from using the lang option
    if lang:
        translated = translate_namespace(ns, lang)
        ns.update(translated)

    return ns

def extract_namespace(mod):
    """
    Return a dictionary with module public variables.
    """

    return {
        name: getattr(mod, name) for name in dir(mod) 
        if not name.startswith('_')
    } 