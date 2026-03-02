def cycle(lst, n):
    for i in range(n):
        for item in lst:
            yield item


elem = input().split()
n = int(input())

for value in cycle(elem, n):
    print(value, end=' ')