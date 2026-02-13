n = int(input())
arr = list(map(int, input().split()))

max = 0
for i in range(1, n):
    if (arr[i] > arr[max]):
        max = i
print(arr[max])