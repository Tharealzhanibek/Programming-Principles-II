a = int(input())
nums = list(map(int, input().split()))

count = 0
for i in range(a):
    if nums[i] > 0:
        count += 1

print(count)