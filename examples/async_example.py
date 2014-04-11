"""
Sheepdog example demonstrating how to submit a request asynchronously.
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

request_id = sheepdog.map_async(f, args, config)

print("Request has been submitted, now waiting for results...")

results = sheepdog.get_results(request_id, './sheepdog.sqlite', verbose=True)
results = [r[1] for r in results]

print("\nReceived results:")
print(results)
