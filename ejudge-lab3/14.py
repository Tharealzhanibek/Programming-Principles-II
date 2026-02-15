n = int(input())
arr = list(map(int, input().split()))
q = int(input())

operations = []

for _ in range(q):
    parts = input().split()
    if parts[0] == "add":
        x = int(parts[1])
        operations.append(lambda a, x=x: a + x)
    elif parts[0] == "multiply":
        x = int(parts[1])
        operations.append(lambda a, x=x: a * x)
    elif parts[0] == "power":
        x = int(parts[1])
        operations.append(lambda a, x=x: a ** x)
    elif parts[0] == "abs":
        operations.append(lambda a: abs(a))

for op in operations:
    arr = list(map(op, arr))

print(*arr)