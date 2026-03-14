import re

s = input()

pattern = r'\b\d{2}/\d{2}/\d{4}\b'

matches = re.findall(pattern, s)

print(len(matches))