import re

s = input()

uppercases = re.findall(r"[A-Z]", s)

print(len(uppercases))