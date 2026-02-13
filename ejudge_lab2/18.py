n = int(input())
f = {}
for i in range(1, n + 1):
    s = input().strip()
    if s not in f:
        f[s] = i

for s in sorted(f):
    print(s, f[s])