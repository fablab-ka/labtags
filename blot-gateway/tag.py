import time

class Tag:
    def __init__(self, mac, addrType, name, rssi, battlvl):
        self.mac = mac
        self.addrType = addrType
        self.name = name
        self.rssi = rssi
        self.battlvl = battlvl
        self.discovered = time.time()
