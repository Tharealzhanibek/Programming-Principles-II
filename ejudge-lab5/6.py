import re

arr = list(map(str, input().split()))

pattern = r"\S+[@]\S+[.]\S+"

res = False

for el in arr:
    res = re.search(pattern, el)

    if res:
        print(el)
        break

if not res:
    print("No email")