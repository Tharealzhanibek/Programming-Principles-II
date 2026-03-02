g = 0

def outer(commands):
    n = 0
    
    def inner():
        nonlocal n
        global g
        for cmd, val in commands:
            if cmd == "global":
                g += val
            elif cmd == "nonlocal":
                n += val
            elif cmd == "local":
                x = 0
                x += val
        return n
    
    n = inner()
    return n

num = int(input())
commands = []
for i in range(num):
    s, v = input().split()
    commands.append((s, int(v)))

n_final = outer(commands)

print(f"{g} {n_final}")