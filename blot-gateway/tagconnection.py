import threading
from bluepy import btle

class TagConnectionThread(threading.Thread):

    def __init__(self, messageQueue, queueLock, mac):
        threading.Thread.__init__(self)
        self.messageQueue
        self.queueLock
        self.mac = mac

    def run(self):
        print("[TagConnectionThread] connection loop start")

        print("[TagConnectionThread] Connecting to: {}, address type: {}".format(self.tag.mac, self.tag.addrType))

        peripheral = btle.Peripheral(self.mac, btle.ADDR_TYPE_PUBLIC)

        try:
            while True:

                time.sleep(0.1)
        finally:
            peripheral.disconnect()

        print("[TagConnectionThread] connection loop shutdown")
