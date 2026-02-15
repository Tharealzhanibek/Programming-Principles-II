class Circle:
    def __init__(self, x):
        self.x = x

    def radius(self):
        res = self.x**2 * 3.14159
        return res

a = int(input())
obj = Circle(a)
area = obj.radius()
print(f"{area:.2f}")