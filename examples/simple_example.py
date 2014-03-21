# Bog standard Sheepdog example script
import sheepdog

def f(a, b):
    return a + b

args = [(1, 1), (1, 2), (2, 2)]

print("Running f(a,b) for arguments:")
print(args)

config = {
    "host": "fear",
}

results = sheepdog.map_sync(f, args, config)

print("\nReceived results:")
print(results)
