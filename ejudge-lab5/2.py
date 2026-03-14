import re

txt = input()
substr = input()

res = re.search(substr, txt)

if res:
    print("Yes")
else:    
    print("No")