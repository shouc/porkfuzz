import random


class Interface:
    def mutate(self):
        pass

    def get(self):
        pass


class Integer(Interface):
    i = 0

    def mutate(self):
        self.i = random.randint(0, 1000)

    def get(self):
        return self.i
