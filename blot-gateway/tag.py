import time

class Tag:
    def __init__(self, mac):
        self.mac = mac
        self.discovered = time.time()
