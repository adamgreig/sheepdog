import sheepdog

def f(a, b):
    return a + g(b)

c = 3

def g(x):
    return x * c

args = [(1, 1), (1, 2), (2, 2)]

print("Running f(a,b) for arguments:")
print(args)
print()

config = {
    "host": "fear", "ssh_user": "ag611",
    "shell": "/users/ag611/.pyenv/versions/3.3.3/bin/python3"
}

namespace = {"g": g, "c": c}

results = sheepdog.map_sync(f, args, config, namespace)

print()
print("Received results:")
print(results)
