n = int(input())
words = input().split()

print(max(words, key=len))