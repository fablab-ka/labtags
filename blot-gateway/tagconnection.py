import threading
from bluepy import btle

class TagConnectionThread(threading.Thread):

    def __init__(self, messageQueue, queueLock, mac):
        threading.Thread.__init__(self)
        self.messageQueue = messageQueue
        self.queueLock = queueLock
        self.mac = mac
        self.notificationTimeout = 10

    def run(self):
        print("[TagConnectionThread] connection loop start, connecting to: {}".format(self.mac))

        peripheral = btle.Peripheral(self.mac, btle.ADDR_TYPE_PUBLIC)

        try:
            while True:
                if peripheral.waitForNotifications(self.notificationTimeout):
                    #self._getResp(['ntfy','ind'], timeout)
                    print("[TagConnectionThread] received notification")

                time.sleep(0.1)
        finally:
            peripheral.disconnect()

        print("[TagConnectionThread] connection loop shutdown")
