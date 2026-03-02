def fibonacci(n):
    a, b = 0, 1
    for i in range(n):
        yield a
        a, b = b, a + b

n = int(input())

first = True
for num in fibonacci(n):
    if not first:
        print(',', end='')
    print(num, end='')
    first = False