import re

s = input()
p = re.escape(input())

print(len(re.findall(p, s)))