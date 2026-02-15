class StringHandler:
    def __init__(self):
        self.word = ""
    def inpt(self):
        self.word = input()
    
    def outpt(self):
        print(self.word.upper())

inst = StringHandler()
inst.inpt()
inst.outpt()