a = int(input())
nums = input().split()

tot = 0
for i in range(a):
    tot += int(nums[i])

print(tot)