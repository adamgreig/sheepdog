"""
Sheepdog example demonstrating what happens when errors occur.

Our simple function raises an error for one of the arguments, and we'll see
that it gives us a None in the results and we can fetch more error details too.
"""

import sheepdog

def f(a, b):
    if a == 2:
        raise ValueError("a cannot be 2!!!")
    return a + b

args = [(1, 1), (1, 2), (2, 2)]

print("Running f(a,b) for arguments:")
print(args)

config = {
    "host": "fear",
}

request_id = sheepdog.map_async(f, args, config)

results = sheepdog.get_results(request_id, './sheepdog.sqlite', verbose=True)
results = [r[1] for r in results]
print("\nReceived results:")
print(results)

errors = sheepdog.get_errors(request_id, './sheepdog.sqlite')

print("\nReceived errors:")
for error in errors:
    print("Argument: {}".format(error[0]))
    print("Error: =====================================")
    print(error[1])
    print("============================================")
