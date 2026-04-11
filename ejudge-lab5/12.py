import re

s = input()

twodigits = re.findall(r"\d{2,}", s)

print(" ".join(twodigits))