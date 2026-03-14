import re

text = input()

match = re.search(r'Name:\s*(.+),\s*Age:\s*(.+)', text)

name = match.group(1)
age = match.group(2)
print(name, age)