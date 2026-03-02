def primes(n):
    for i in range(2, n + 1):
        pr = True
        for j in range(2, int(i ** 0.5) + 1):
            if i % j == 0:
                pr = False
                break
        if pr:
            yield i

n = int(input())

first = True
for num in primes(n):
    if not first:
        print(' ', end='')
    print(num, end='')
    first = False