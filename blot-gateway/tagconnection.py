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
        self.isDead = False
        self.peripheral = None

    def triggerBeep(self):
        print(ANSI_GREEN + "[TagConnectionThread] triggerBeep" + ANSI_OFF)

        if self.isDead:
            print(ANSI_GREEN + "[TagConnectionThread] Error! Connection already dead" + ANSI_OFF)
            return

        success = False
        for service in self.peripheral.services:
            if service.uuid == UUID(6146):
                print(ANSI_GREEN + "[TagConnectionThread] found the Immediate Alert Service" + ANSI_OFF)

                characteristics = service.getCharacteristics()
                for characteristic in characteristics:
                    if characteristic.uuid == UUID(10758):
                        print(ANSI_GREEN + "[TagConnectionThread] found the Alert Level Characteristic" + ANSI_OFF)
                        characteristic.write(1)
                        success = True
                        continue
                continue

        if not success:
            print(ANSI_GREEN + "[TagConnectionThread] failed to trigger beep, was unable to find service or characteristic" + ANSI_OFF)

    def run(self):
        print(ANSI_GREEN + "[TagConnectionThread] connection loop start, connecting to: {}".format(self.mac) + ANSI_OFF)

        self.peripheral = btle.Peripheral(self.mac, btle.ADDR_TYPE_PUBLIC)

        print(ANSI_GREEN + "[TagConnectionThread] Tag '{}' connected successfully".format(self.mac) + ANSI_OFF)

        try:
            while True:
                if self.peripheral.waitForNotifications(self.notificationTimeout):
                    print(ANSI_GREEN + "[TagConnectionThread] received notification from '" + self.mac + "'" + ANSI_OFF)

                    self.queueLock.acquire()
                    self.messageQueue.put(TagNotificationMessage(self.mac, "press"))
                    self.queueLock.release()
                    #self._getResp(['ntfy','ind'], timeout)

                time.sleep(0.1)
        except btle.BTLEException as e:
            self.isDead = True

            if e.code == btle.BTLEException.DISCONNECTED:
                self.queueLock.acquire()
                self.messageQueue.put(TagDisconnectedMessage(self.mac))
                self.queueLock.release()

                print(ANSI_GREEN + "[TagConnectionThread] Device '" + self.mac + "' was disconnected." + ANSI_OFF)
            else:
                print(ANSI_GREEN + "[TagConnectionThread] Error!" + str(e.message) + ANSI_OFF)
                raise e
        finally:
            self.peripheral.disconnect()

        print(ANSI_GREEN + "[TagConnectionThread] connection loop shutdown" + ANSI_OFF)
        self.isDead = True
