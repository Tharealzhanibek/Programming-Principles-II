import re

s = input()
p = input()

n = re.findall(p, s) 

print(len(n))