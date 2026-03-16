def square(x):
    return x * x

a = int(input())
numbers = list(map(int, input().split()))

print(sum(map(square, numbers)))