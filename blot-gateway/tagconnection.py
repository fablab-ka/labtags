from bluepy import btle

class TagConnectionThread(threading.Thread):

    def __init__(self, messageQueue, queueLock, tag):
        threading.Thread.__init__(self)
        self.messageQueue
        self.queueLock
        self.tag = tag

    def run(self):
        print("[TagConnectionThread] connection loop start")

        print("[TagConnectionThread] Connecting to: {}, address type: {}".format(self.tag.mac, self.tag.addrType))

        peripheral = btle.Peripheral(self.tag.mac, self.tag.addrType)

        try:
            while True:

                time.sleep(0.1)
        finally:
            peripheral.disconnect()

        print("[TagConnectionThread] connection loop shutdown")
