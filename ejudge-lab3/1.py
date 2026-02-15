s = input()

even = True
for c in s:
    el = int(c)
    if (el % 2 == 1):
        even = False
        
if even:
    print("Valid")
else:
    print("Not valid")