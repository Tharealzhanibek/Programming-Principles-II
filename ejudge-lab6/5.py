text = input()
vowel = True

for x in text:
    if x == 'i' or x == 'e' or x == 'a' or x == 'u' or x == 'o' or x == 'I' or x == 'E' or x == 'A' or x == 'U' or x == 'O':
        vowel = True
        break
    else:
        vowel = False

if vowel:
    print('Yes')
else:
    print('No')