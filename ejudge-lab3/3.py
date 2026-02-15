s = input()

digits = {
    "ONE": "1",
    "TWO": "2",
    "THR": "3",
    "FOU": "4",
    "FIV": "5",
    "SIX": "6",
    "SEV": "7",
    "EIG": "8",
    "NIN": "9",
    "ZER": "0",
    
    "0": "ZER",
    "1": "ONE",
    "2": "TWO",
    "3": "THR",
    "4": "FOU",
    "5": "FIV",
    "6": "SIX",
    "7": "SEV",
    "8": "EIG",
    "9": "NIN"
}

fNum = ""
sNum = ""
operator = ""

tempDigit = ""
tempCnt = 0

isFirst = True

for c in s:
    if (c == '+'):
        operator = c
        isFirst = False
        continue
    elif (c == '-'):
        operator = c
        isFirst = False
        continue
    elif (c == '*'):
        operator = c
        isFirst = False
        continue
        
    tempDigit += c
    tempCnt += 1
        
    if (tempCnt == 3):
        if isFirst:
            fNum += digits[tempDigit]
            tempDigit = ""
            tempCnt = 0
        else:
            sNum += digits[tempDigit]
            tempDigit = ""
            tempCnt = 0
    
def perform(fNum, sNum, operator):
    a = int(fNum)
    b = int(sNum)
    
    int_res = 0
    if operator == '*':
        int_res = a * b
    if operator == '+':
        int_res =  a + b
    if operator == '-':
        int_res = a - b

    res = ""
    str_res = str(int_res)
    
    for c in str_res:
        res += digits[c]
    
    return res

print(perform(fNum, sNum, operator))