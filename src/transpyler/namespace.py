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


def recreate_namespace(transpyler):
    """
    Recompute the default namespace for the transpyler object.
    """
    ns = make_global_namespace(transpyler.lang)

    if transpyler.has_turtle_functions:
        if transpyler.turtle_backend is None:
            raise RuntimeError(
                '.turtle_backend of transpyler object must be set to '
                'either "tk" or "qt"'
            )
        turtle_ns = make_turtle_namespace(transpyler.turtle_backend, transpyler.lang)
        ns.update(turtle_ns)
    transpyler.namespace = ns
    return ns