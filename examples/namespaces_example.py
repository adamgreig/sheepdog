"""
Sheepdog example script demonstrating namespace usage.
"""

import sheepdog

def f(a, b):
    return const + g(a) + h(b)

def g(a):
    return a + 1

def h(b):
    return b ** 2

args = [(1, 1), (1, 2), (2, 2)]
namespace = {"g": g, "h": h, "const": 12}

print("Running f(a,b) for arguments:")
print(args)

config = {
    "host": "fear",
}

results = sheepdog.map(f, args, config, namespace)

print("\nReceived results:")
print(results)
