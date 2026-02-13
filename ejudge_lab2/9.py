n = int(input())
arr = list(map(int, input().split()))

mx = max(arr)
mn = min(arr)

for el in arr:
    if (el == mx):
        el = mn
    
    print(el, end=" ")