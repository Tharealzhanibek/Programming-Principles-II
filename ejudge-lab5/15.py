import re

text = input()

def callable(match):
    digit = match.group()
    return digit * 2

result = re.sub(r'\d', callable, text)

print(result)