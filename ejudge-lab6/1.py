def power(n):
    return n*n

n = int(input())

arr = list(map(int, input().split()))

res = list(map(power, arr))

print(res)