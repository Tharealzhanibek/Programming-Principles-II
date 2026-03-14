import re

s = input()
d = input()

splitting = re.split(d, s)

print(",".join(splitting))