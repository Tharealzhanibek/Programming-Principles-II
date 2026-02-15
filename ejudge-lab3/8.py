class Account:
    def __init__(self):
        self.x = ''
        self.y = ''

    def withdral(self):
        self.x, self.y = map(int, input().split())
        if self.x >= self.y:
            print(self.x - self.y)
        else:
            print("Insufficient Funds")
    
obj = Account()
obj.withdral()