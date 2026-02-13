n = int(input())
i = 0
while True:
    if (2**i > n):
        print("NO")
        break
    elif (2**i == n):
        print("YES")
        break
    else:
        i += 1