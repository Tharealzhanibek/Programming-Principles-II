n = int(input())
numbers = map(int, input().split())

if all(x >= 0 for x in numbers):
    print("Yes")
else:
    print("No")