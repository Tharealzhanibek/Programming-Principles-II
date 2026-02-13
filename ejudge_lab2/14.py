a=int(input())
num=list(map(int, input().split()))

freq = {}
for x in num:
    freq[x] = freq.get(x,0) + 1
mostfreq = max(freq, key=freq.get)
if freq[mostfreq] == 1:
    print(min(num))
else:
    print(mostfreq)