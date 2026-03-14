import re

s = input()

uppercases = re.findall(r"\d{2,}", s)

print(" ".join(uppercases))