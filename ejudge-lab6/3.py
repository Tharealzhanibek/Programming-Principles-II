def words(p):
    return f"{p[0]}:{p[1]}"

a = int(input())
text = input().split()

print(*map(words, enumerate(text)))