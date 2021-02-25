import random


class IPv4:
    ip = bytearray(b'\x89\x89\x89\x88')  # 137.137.137.136

    def mutate(self):
        self.ip[random.randint(0, 3)] ^= random.randint(0, 255)

    def get(self):
        return self.ip


class Cidr(IPv4):
    prefix = 31  # 137.137.137.136/31

    def mutate(self):
        r = random.randint(0, 10) % 3
        if r == 0:
            self.ip[random.randint(0, int(self.prefix / 8))] ^= random.randint(0, 255)
        elif r == 1:
            self.ip = bytearray(b'\x89\x89\x89\x88')
        else: # r = 2
            self.prefix = random.randint(0, 31)
        print(self.prefix, self.ip)
        # fix it up
        if self.prefix <= 8:
            self.ip[1:] = b'\x00\x00\x00'
            self.ip[0] &= ((1 << (self.prefix + 1)) - 1) << (8 - self.prefix)
        elif self.prefix <= 16:
            self.ip[2:] = b'\x00\x00'
            p = self.prefix - 8
            self.ip[1] &= ((1 << (p + 1)) - 1) << (8 - p)
        elif self.prefix <= 24:
            self.ip[3:] = b'\x00'
            p = self.prefix - 16
            self.ip[2] &= ((1 << (p + 1)) - 1) << (8 - p)
        else:
            p = self.prefix - 24
            self.ip[3] &= ((1 << (p + 1)) - 1) << (8 - p)

    def get(self):
        return self.ip, self.prefix
