class test:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def add(self):
        print(self.a + self.b)

    def addadd(self):
        self.add()

class trytry(test):
    def addaddadd(self):
        self.addadd()

tryclass = trytry(3, 7)
tryclass.addaddadd()
