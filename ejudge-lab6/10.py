n = int(input())
numbers = list(map(int, input().split()))

# Count truthy (non-zero) numbers
result = sum(map(bool, numbers))

# Output
print(result)