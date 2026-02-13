n = int(input())
arr = list(map(int, input().split()))

arr.sort(reverse=True)

for el in arr:
    print(el, end=" ")