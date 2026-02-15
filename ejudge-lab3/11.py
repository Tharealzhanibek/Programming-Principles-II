class Para:
    def __init__(self, a1, b1, a2, b2):
        self.x = a1
        self.y = b1
        self.z = a2
        self.c = b2

    def Sum(self):
        print(f"Result: {self.x + self.z} {self.y + self.c}")


a, b, c, d = map(int, input().split())
obj = Para(a, b, c, d)
obj.Sum()