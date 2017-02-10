import time

class Tag:
    def __init__(self, mac, addrType):
        self.mac = mac
        self.addrType = addrType
        self.discovered = time.time()
