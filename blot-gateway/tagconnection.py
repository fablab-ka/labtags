import threading, time
from bluepy import btle
from messages import TagDisconnectedMessage, TagNotificationMessage

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
                    self.queueLock.acquire()
                    self.messageQueue.put(TagNotificationMessage(self.mac, ""))
                    self.queueLock.release()
                    #self._getResp(['ntfy','ind'], timeout)
                    print("[TagConnectionThread] received notification from '" + self.mac + "'")

                time.sleep(0.1)
        except btle.BTLEException as e:
            if e.code == btle.BTLEException.DISCONNECTED:
                self.queueLock.acquire()
                self.messageQueue.put(TagDisconnectedMessage(self.mac))
                self.queueLock.release()
                print("[TagConnectionThread] Device '" + self.mac + "' was disconnected.")
            else:
                raise e
        finally:
            peripheral.disconnect()

        print("[TagConnectionThread] connection loop shutdown")
