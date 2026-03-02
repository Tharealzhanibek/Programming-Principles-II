def div(n):
    for i in range(0, n + 1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

n = int(input())

first = True
for num in div(n):
    if not first:
        print(' ', end='')
    print(num, end='')
    first = False