import re

txt = input()
res = re.match(r"Hello", txt)

if res:
    print("Yes")
else:    
    print("No")