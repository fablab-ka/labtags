from tag import Tag
from bluepy import btle

class TagScanner:
    def __init__(self):
        #btle.Debugging
        self.timeout = 4
        self.hci = 0
        self.scanner = btle.Scanner(self.hci)

    def scan(self):
        result = []

        devices = self.scanner.scan(self.timeout)
        for d in devices:
            if not d.connectable:
                print("[TagScanner] Device not connectable", d.addr)
                continue

            #print("[TagScanner] DEBUG", dir(d))
            result.append(Tag(d.addr))

        return result
