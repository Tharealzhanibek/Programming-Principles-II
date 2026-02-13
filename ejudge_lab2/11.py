a = list(map(int, input().split()))
b = list(map(int, input().split()))

l, r = a[1]-1, a[2]

b[l:r] = b[l:r][::-1]

print(*b)