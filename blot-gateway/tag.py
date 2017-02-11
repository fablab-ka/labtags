import time

class Tag:
    def __init__(self, mac, addrType, name):
        self.mac = mac
        self.addrType = addrType
        self.name = name
        self.discovered = time.time()
