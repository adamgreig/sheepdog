"""
Bog standard Sheepdog example script.

Defines a simple function, a short list of arguments to run it with,
then submits it to a GridEngine cluster and waits for the results.
"""

import sheepdog

def f(a, b):
    return a + b

args = [(1, 1), (1, 2), (2, 2)]

print("Running f(a,b) for arguments:")
print(args)

config = {
    "host": "fear",
}

results = sheepdog.map(f, args, config)

print("\nReceived results:")
print(results)
