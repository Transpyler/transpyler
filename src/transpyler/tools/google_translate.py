import inspect
import warnings


try:
    from textblob import TextBlob
except (ImportError, ValueError):
    warnings.warn('could not initialize TextBlob. You should check if your '
                  'nltk installation has all necessary data.')
    textblob = None


def translate_functions(seq, to_lang, from_lang='en'):
    """
    Use Google Translate to translate names, parameters and docstrings for
    the given list of functions.
    """

    return [translate_function(func, to_lang, from_lang='en') for func in seq]


def translate_function(function, to_lang, from_lang='en'):
    """
    Translate a single function using Google Translate. The resulting source
    code just calls the original function and assumes it lives in the global
    get_namespace.
    """

    name = TextBlob(function.__name__)
    args = get_args(function)
    docs = TextBlob(function.__doc__)
    lines = []

    # Format arguments declaration
    args_decl = []
    for (arg_name, default) in args:
        if default is None:
            args_decl.append(arg_name)
        else:
            args_decl.append('%s=%s' % (arg_name, default))
    args_decl = ', '.join(args_decl)

    # Translate function name and make declaration.
    translated_name = str(name.translate(from_lang, to_lang))
    translated_name = translated_name[0].lower() + translated_name[1:]
    lines.append('def %s(%s):' % (translated_name, args_decl))

    # Translate docstring, indent and add it to lines
    translated_docs = docs.translate(from_lang, to_lang)
    lines.append('    """')
    for line in str(translated_docs).splitlines():
        lines.append('    ' + line)
    lines.append('    """')

    # Call original function
    args_call = []
    has_stararg = False
    for arg_name, default in args:
        if has_stararg and not arg_name.startswith('*'):
            args_call.append('%s=%s' % (arg_name, arg_name))
        else:
            args_call.append(arg_name)
            if arg_name.startswith('*'):
                has_stararg = True
    args_call = ', '.join(args_call)
    lines.append('    return %s(%s)' % (name, args_call))

    # Render source code
    return '\n'.join(lines)


def get_args(function):
    """
    Return a list of named arguments (name, default) tuples. If it has no
    default, return (name, None). Variational positional and keyword arguments
    are also returned, as ('*args', None) and ('**kwargs, None).
    """

    try:
        spec = inspect.getfullargspec(function)
        return get_args_from_spec(spec)
    except TypeError:
        return get_args_from_docstring(function)


def get_args_from_spec(spec):
    args = []

    # Save default args
    diff = len(spec.args) - len(spec.defaults)
    defaults = (None,) * diff + spec.defaults
    defaults = [x if x is None else repr(x) for x in defaults]
    args.extend(zip(spec.args, defaults))

    # Add varags
    if spec.varargs:
        args.append(('*%s' % spec.varargs, None))
    elif spec.kwonlyargs:
        args.append('*', None)

    # Add keyword only
    if spec.kwonlyargs:
        defaults = [repr(spec.kwonlydefaults[k]) for k in spec.kwonlyargs]
        args.extend(zip(spec.kwonlyargs, defaults))

    # Add varkw
    if spec.varkw:
        args.append(('**%s' % spec.varkw, None))
    return args


def get_args_from_docstring(function):
    signature = function.__doc__.partition('\n')[0]
    name = function.__name__
    if not signature.startswith(name):
        raise TypeError('could not determine signature of builtin.')
    signature = signature.partition('(')[2].partition(')')[0]
    signature = signature.replace('[', '').replace(']', '')
    return [(x.strip(), None) for x in signature.split(',')]
