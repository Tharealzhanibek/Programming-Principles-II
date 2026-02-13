a = int(input())
n = list(map(int, input().split()))
s = set()
for i in n:
    if i not in s:
        print("YES")
        s.add(i)
    else:
        print("NO")