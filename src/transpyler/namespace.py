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

def make_turtle_namespace(backend, lang):
    """
    Return a dictionary with all turtle-related functions.
    """

    if backend == 'tk':
        from transpyler.turtle.tk import make_turtle_namespace

        ns = make_turtle_namespace()

    elif backend == 'qt':
        from transpyler.turtle.qt import make_turtle_namespace

        ns = make_turtle_namespace()

    else:
        raise ValueError('invalid backend: %r' % backend)

    if lang:
        translated = translate_namespace(ns, lang)
        ns.update(translated)
    
    return ns 