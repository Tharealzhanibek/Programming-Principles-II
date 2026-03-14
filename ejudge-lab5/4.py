import re

txt = input()

arr = re.findall(r"\d", txt)

for el in arr:
    print(el, end=" ")