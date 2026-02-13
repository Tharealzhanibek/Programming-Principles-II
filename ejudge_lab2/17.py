n = int(input())
count = 0
dict = {}

for i in range(n):
    el = input()
    if el in dict:
        dict[el] += 1
    else:
        dict[el] = 1

for keys in dict:
    if dict[keys] == 3:
        count += 1

print(count)