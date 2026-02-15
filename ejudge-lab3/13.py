nums = list(map(int, input().split()))

primes = list(filter(
    lambda n: n > 1 and all(n % i != 0 for i in range(2, int(n**0.5) + 1)),
    nums
))

if primes:
    print(*primes)
else:
    print("No primes")