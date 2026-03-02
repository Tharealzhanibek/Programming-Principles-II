def even(n):
    for i in range(0, n + 1, 2):
        yield i

n = int(input())

gen = even(n)

first = True
for num in gen:
    if not first:
        print(',', end='')
    print(num, end='')
    first = False