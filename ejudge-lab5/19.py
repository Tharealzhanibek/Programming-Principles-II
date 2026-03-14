import re

text = input()

pattern = re.compile(r"\b\w+\b")

words = pattern.findall(text)

print(len(words))