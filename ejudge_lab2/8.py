n = int(input())
i = 0

while True:
    if (2**i <= n):
        print(2**i, end=" ")
        i += 1
    elif(2**i > n):
        break
        