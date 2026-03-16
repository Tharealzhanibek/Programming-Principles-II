def even(x):
    cnt = 0
    if x % 2 == 0:
        cnt += 1
    return cnt
        
a = int(input())
numbers = list(map(int, input().split()))

print(sum(map(even, numbers)))