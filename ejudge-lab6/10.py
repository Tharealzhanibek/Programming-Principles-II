n = int(input())
numbers = list(map(int, input().split()))

result = sum(map(bool, numbers))

print(result)