n = int(input())
total = {}
for i in range(n):
    s, k = input().split()
    k = int(k)
    total[s] = total.get(s, 0) + k

for s in sorted(total):
    print(s, total[s])