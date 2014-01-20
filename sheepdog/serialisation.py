# Sheepdog
# Copyright 2013 Adam Greig
#
# Released under the MIT license. See LICENSE file for details.

"""
Sheepdog's serialisation functions, for turning Python bits into
HTTP safe strings.

Functions are serialised by getting their code objects and dumping them with
marshal and encoding the bytes using base64.

Arguments are pickled since that should work for any standard arguments.
"""

import types
import base64
import pickle
import marshal

def serialise_function(f):
    """Turn a Python function (unbound, no closures, etc) into a base64 byte
       string (a bytes object).
    """
    if hasattr(f, "__code__"):
        fcode = f.__code__
    else:
        fcode = f.func_code
    fcodebin = marshal.dumps(fcode)
    return base64.b64encode(fcodebin)

def deserialise_function(f, namespace=None):
    """Turn a base64 bytestring back into a Python function, with *namespace*
       for its globals. Returns the function.
    """
    if not namespace:
        namespace = globals()
    else:
        namespace = namespace.copy()
    if "__builtins__" not in namespace:
        namespace["__builtins__"] = __builtins__
    fcodebin = base64.b64decode(f)
    fcode = marshal.loads(fcodebin)
    return types.FunctionType(fcode, namespace)

def serialise_pickle(args):
    """Serialise *args* using pickle and base64, returning the b64 bytestring.
    """
    return base64.b64encode(pickle.dumps(args))

def deserialise_pickle(args):
    """Deserialise *args* using base64 and pickle, returning the Python object.
    """
    return pickle.loads(base64.b64decode(args))

serialise_arg = serialise_pickle
deserialise_arg = deserialise_pickle

def serialise_args(args):
    """Serialise each item in *args* using serialise_pickle, returning a list
       of serialised items.
    """
    return [serialise_pickle(x) for x in args]

def deserialise_args(args):
    """Deserialise each item in *args* using deserialise_pickle, returning a
       list of the original objects.
    """
    return [deserialise_pickle(x) for x in args]

def serialise_namespace(ns):
    """Serialise a dict *ns* so that any functions in it are first converted to
       base64 strings, then pickle and base64 encode the result.
    """
    ns = ns.copy()
    serialised_keys = []
    for key in ns:
        if type(ns[key]) == types.FunctionType:
            ns[key] = serialise_function(ns[key])
            serialised_keys.append(key)
    ns["__serialised_keys"] = serialised_keys
    return serialise_pickle(ns)

def deserialise_namespace(ns):
    """Deserialise a base64 bytestring *ns*, deserialising any serialised
       functions inside it too, finally returning the original dictionary.
    """
    ns = deserialise_pickle(ns)
    if "__serialised_keys" in ns:
        for key in ns["__serialised_keys"]:
            ns[key] = deserialise_function(ns[key], ns)
    del ns["__serialised_keys"]
    return ns
