import sheepdog

def f(a, b):
    return a + b

args = [(1, 1), (1, 2), (2, 2)]
print("Running f(a,b)=a+b for arguments:")
print(args)
print()

config = {
    "host": "fear", "ssh_user": "ag611",
    "shell": "/users/ag611/.pyenv/versions/3.3.3/bin/python3"
}

results = sheepdog.map_sync(f, args, config)
print()
print("Received results:")
print(results)
