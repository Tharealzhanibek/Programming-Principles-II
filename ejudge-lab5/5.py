import re

txt = input()

pattern = r"^[a-zA-Z].*[0-9]$"

res = re.match(pattern, txt)

if res:
    print("Yes")
else:    
    print("No")