def kvadrat(n):
    pwr = 1
    for i in range(n + 1):
        yield pwr
        pwr *= 2

n = int(input())

first = True
for num in kvadrat(n):
    if not first:
        print(' ', end='')
    print(num, end='')
    first = False