import threading, time, binascii
from bluepy import btle
from messages import TagConnectedMessage, TagDisconnectedMessage, TagNotificationMessage
#from messages import *
from utils import ANSI_GREEN, ANSI_WHITE, ANSI_OFF
from bluepy.btle import UUID, Peripheral, DefaultDelegate, AssignedNumbers

#import time
#https://smidgeonpigeon.wordpress.com/2015/07/21/raspberry-pi-2-ble-ti-sensor-tag/
import sensortag

#class BeSensorTag(Peripheral):
#    def __init__(self,addr):
#        Peripheral.__init__(self,addr)
#        svcs = self.discoverServices()
#        self.disconnect()
#        if _TI_UUID(0xAA70) in svcs:
#            return 1
#        else:
#            return 0
               
                
class TagConnectionThread(threading.Thread):

    def __init__(self, messageQueue, tag):
        threading.Thread.__init__(self)

        #btle.Debugging = True
        self.messageQueue = messageQueue
        self.tag = tag
        #self.name2 = name
        self.notificationTimeout = 1
        self.isDead = False
        self.peripheral = None
        self.beepWasTriggered = False

    def triggerBeep(self):
        print(ANSI_GREEN + "[TagConnectionThread] triggerBeep" + ANSI_OFF)

        if self.isDead:
            print(ANSI_GREEN + "[TagConnectionThread] Error! Connection already dead" + ANSI_OFF)
            return

        self.beepWasTriggered = True

    def setBeepCharacteristicValue(self, val):
        print(ANSI_GREEN + "[TagConnectionThread] setBeepCharacteristicValue '" + str(val) + "'" + ANSI_OFF)

        if self.isDead:
            print(ANSI_GREEN + "[TagConnectionThread] Error! Connection already dead" + ANSI_OFF)
            return
        if not self.peripheral:
            print(ANSI_GREEN + "[TagConnectionThread] Peripheral not yet initialized. Triggering beep later" + ANSI_OFF)
            return

        if val:
            self.peripheral._writeCmd("wr B 01\n")
        else:
            self.peripheral._writeCmd("wr B 00\n")
        response = self.peripheral._getResp('wr')
        print(ANSI_GREEN + "[TagConnectionThread] Characteristic success (" + str(response) + ")" + ANSI_OFF)
        return

        # success = False
        # for service in self.peripheral.services:
        #     if service.uuid == btle.UUID(6146):
        #         print(ANSI_GREEN + "[TagConnectionThread] found the Immediate Alert Service" + ANSI_OFF)
        #
        #         characteristics = service.getCharacteristics()
        #         for characteristic in characteristics:
        #             if characteristic.uuid == btle.UUID(10758):
        #                 print(ANSI_GREEN + "[TagConnectionThread] found the Alert Level Characteristic" + ANSI_OFF)
        #                 if val:
        #                     characteristic.write(binascii.unhexlify("00"))
        #                     print(ANSI_GREEN + "[TagConnectionThread] enabled Alert" + ANSI_OFF)
        #                 else:
        #                     characteristic.write(binascii.unhexlify("01"))
        #                     print(ANSI_GREEN + "[TagConnectionThread] disabled Alert" + ANSI_OFF)
        #                 success = True
        #                 continue
        #         continue
        #
        # if not success:
        #     print(ANSI_GREEN + "[TagConnectionThread] failed to trigger beep, was unable to find service or characteristic" + ANSI_OFF)

    def run(self):
        print(ANSI_GREEN + "[TagConnectionThread] connection loop start, connecting to: {}".format(self.tag.mac) + ANSI_OFF)

        
        #self.peripheral.__init__(self,self.mac)
        #svcs = self.peripheral.discoverServices()
        #if _TI_UUID(0xAA70) in svcs:
        if self.mac == 'b0:b4:48:b8:7f:84' or self.mac == 'b0:b4:48:b8:43:86':
            #senstag = 1
            print(ANSI_WHITE + "------------ SensorTag {} -------------".format(self.mac) + ANSI_OFF)
            self.peripheral = sensortag.SensorTag(self.mac)
            self.peripheral.IRtemperature.enable()
            self.peripheral.humidity.enable()
            self.peripheral.barometer.enable()
            self.peripheral.accelerometer.enable()
            self.peripheral.magnetometer.enable()
            self.peripheral.gyroscope.enable()
            self.peripheral.keypress.enable()
            self.peripheral.lightmeter.enable()
        else:
            print(ANSI_WHITE + "------------ iTag {} -------------".format(self.mac) + ANSI_OFF)
            self.peripheral = btle.Peripheral(self.tag.mac, btle.ADDR_TYPE_PUBLIC)
        

        print(ANSI_GREEN + "[TagConnectionThread] Tag '{}' connected successfully".format(self.tag.mac) + ANSI_OFF)

        self.queueLock.acquire()
        self.messageQueue.put(TagConnectedMessage(self.tag.mac))
        self.queueLock.release()

        try:
            while True:

                if self.beepWasTriggered:
                    self.beepWasTriggered = False

                    self.setBeepCharacteristicValue(True)
                    time.sleep(1)
                    self.setBeepCharacteristicValue(False)

                if self.peripheral.waitForNotifications(self.notificationTimeout):
                    print(ANSI_GREEN + "[TagConnectionThread] received notification from '" + self.tag.mac + "'" + ANSI_OFF)

                    self.messageQueue.put(TagNotificationMessage(self.tag, "press"))

                if self.tag.mac == 'b0:b4:48:b8:7f:84' or self.tag.mac == 'b0:b4:48:b8:43:86':
                    print("Temp: ", self.peripheral.IRtemperature.read(), ' C')
                    print("Humidity: ", self.peripheral.humidity.read(),  ' Hrel')
                    print("Barometer: ", self.peripheral.barometer.read())
                    print("Accelerometer: ", self.peripheral.accelerometer.read())
                    print("Magnetometer: ", self.peripheral.magnetometer.read() , " uT")
                    print("Gyroscope: ", self.peripheral.gyroscope.read())
                    print("Light: ", self.peripheral.lightmeter.read())
                    time.sleep(5.0)
                else:
                    time.sleep(0.1)
        except btle.BTLEException as e:
            self.isDead = True

            if e.code == btle.BTLEException.DISCONNECTED:
                self.messageQueue.put(TagDisconnectedMessage(self.tag))

                print(ANSI_GREEN + "[TagConnectionThread] Device '" + self.tag.mac + "' was disconnected." + ANSI_OFF)
            else:
                print(ANSI_GREEN + "[TagConnectionThread] Error!" + str(e.message) + ANSI_OFF)
                raise e
        finally:
            self.peripheral.disconnect()

        print(ANSI_GREEN + "[TagConnectionThread] connection loop shutdown" + ANSI_OFF)
        self.isDead = True
