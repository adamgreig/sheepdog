"""
Example Sheepdog script with numpy.

We'll import and make global numpy inside our Sheepdog function,
and then any other function can also use it.
"""

import sheepdog

def f(a, b):
    import numpy as np
    global np
    return g(a, b)

def g(a, b):
    return np.mean(np.array((a, b)))

args = [(1, 1), (1, 2), (2, 2)]

print("Running f(a,b) for arguments:")
print(args)

config = {
    "host": "fear",
}

namespace = {"g": g}

results = sheepdog.map(f, args, config, namespace)

print("\nReceived results:")
print(results)
