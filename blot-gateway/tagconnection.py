import threading, time
from bluepy import btle
from messages import TagDisconnectedMessage, TagNotificationMessage
from utils import ANSI_GREEN, ANSI_OFF

class TagConnectionThread(threading.Thread):

    def __init__(self, messageQueue, queueLock, mac):
        threading.Thread.__init__(self)
        self.messageQueue = messageQueue
        self.queueLock = queueLock
        self.mac = mac
        self.notificationTimeout = 10

    def run(self):
        print(ANSI_GREEN + "[TagConnectionThread] connection loop start, connecting to: {}".format(self.mac) + ANSI_OFF)

        peripheral = btle.Peripheral(self.mac, btle.ADDR_TYPE_PUBLIC)

        try:
            while True:
                if peripheral.waitForNotifications(self.notificationTimeout):
                    self.queueLock.acquire()
                    self.messageQueue.put(TagNotificationMessage(self.mac, ""))
                    self.queueLock.release()
                    #self._getResp(['ntfy','ind'], timeout)
                    print(ANSI_GREEN + "[TagConnectionThread] received notification from '" + self.mac + "'" + ANSI_OFF)

                time.sleep(0.1)
        except btle.BTLEException as e:
            if e.code == btle.BTLEException.DISCONNECTED:
                self.queueLock.acquire()
                self.messageQueue.put(TagDisconnectedMessage(self.mac))
                self.queueLock.release()
                print(ANSI_GREEN + "[TagConnectionThread] Device '" + self.mac + "' was disconnected." + ANSI_OFF)
            else:
                raise e
        finally:
            peripheral.disconnect()

        print(ANSI_GREEN + "[TagConnectionThread] connection loop shutdown" + ANSI_OFF)
