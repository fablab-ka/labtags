import threading, time, binascii, traceback
from bluepy import btle
from messages import TagConnectedMessage, TagDisconnectedMessage, TagNotificationMessage, TagUpdateMessage
#from messages import *
from utils import ANSI_GREEN, ANSI_WHITE, ANSI_OFF
from bluepy.btle import UUID, Peripheral, DefaultDelegate, AssignedNumbers


#https://smidgeonpigeon.wordpress.com/2015/07/21/raspberry-pi-2-ble-ti-sensor-tag/
import sensortag


class TagConnectionThread(threading.Thread):

    def __init__(self, messageQueue, tag):
        threading.Thread.__init__(self)

        #btle.Debugging = True
        self.messageQueue = messageQueue
        self.tag = tag
        self.notificationTimeout = 1
        self.isDead = False
        self.peripheral = None
        self.beepWasTriggered = False
        #battlvl=-1

    def triggerBeep(self):
        print(ANSI_GREEN + "[TagConnectionThread] triggerBeep '" + self.tag.mac + "'" + ANSI_OFF)

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

    def getBatteryLevelValue(self):
        print(ANSI_GREEN + "[TagConnectionThread] getBatteryLevelValue " + ANSI_OFF)

        if self.isDead:
            print(ANSI_GREEN + "[TagConnectionThread] Error! Connection already dead" + ANSI_OFF)
            return
        if not self.peripheral:
            print(ANSI_GREEN + "[TagConnectionThread] Peripheral not yet initialized. Triggering beep later" + ANSI_OFF)
            return

        #battery
        battlvl=-1
        for service in self.peripheral.services:
            if service.uuid == btle.UUID(0x180F):
                print(ANSI_GREEN + "[TagConnectionThread] found the Battery Service" + ANSI_OFF)
        
                characteristics = service.getCharacteristics()
                for ch in characteristics:
                    if ch.uuid == btle.UUID(0x2A19):
                        if (ch.supportsRead()):
                            try:
                                battlvl = ord(ch.read());
                                print(ANSI_GREEN + "    ->" + str(battlvl) + "%" + ANSI_OFF)
                            except BTLEException as e:
                                battlvl = -1
                                print("    ->", e)
                        continue
                continue
        return battlvl

    def run(self):
        try:
            print(ANSI_GREEN + "[TagConnectionThread] connection loop start, connecting to: {}".format(self.tag.mac) + ANSI_OFF)
            senstag = 0
            if self.tag.name == 'CC2650 SensorTag':
                senstag = 1
                print(ANSI_GREEN + "[TagConnectionThread] it's a SensorTag '{}' <-------------".format(self.tag.mac) + ANSI_OFF)
                self.peripheral = sensortag.SensorTag(self.tag.mac)
                self.peripheral.IRtemperature.enable()
                self.peripheral.humidity.enable()
                self.peripheral.barometer.enable()
                self.peripheral.accelerometer.enable()
                self.peripheral.magnetometer.enable()
                self.peripheral.gyroscope.enable()
                self.peripheral.keypress.enable()
                self.peripheral.lightmeter.enable()
            else:
                print(ANSI_GREEN + "[TagConnectionThread] it's a iTag '{}' <-------------".format(self.tag.mac) + ANSI_OFF)
                self.peripheral = btle.Peripheral(self.tag.mac, btle.ADDR_TYPE_PUBLIC)
                self.tag.battlvl = self.getBatteryLevelValue()


            print(ANSI_GREEN + "[TagConnectionThread] Tag '{}' connected successfully".format(self.tag.mac) + ANSI_OFF)

            self.messageQueue.put(TagConnectedMessage(self.tag))



            while True:
                #battery update
                battlvl = self.getBatteryLevelValue()
                if battlvl != self.tag.battlvl:
                    print(ANSI_GREEN + "    ->" + str(battlvl) + "% (old:" + str(self.tag.battlvl) + "%" + ANSI_OFF)
                    self.tag.battlvl = battlvl;
                    self.messageQueue.put(TagUpdateMessage(self.tag))
                    
                if self.beepWasTriggered:
                    self.beepWasTriggered = False

                    self.setBeepCharacteristicValue(True)
                    time.sleep(1)
                    self.setBeepCharacteristicValue(False)

                if self.peripheral.waitForNotifications(self.notificationTimeout):
                    print(ANSI_GREEN + "[TagConnectionThread] received notification from '" + self.tag.mac + "'" + ANSI_OFF)

                    self.messageQueue.put(TagNotificationMessage(self.tag, "press"))

                if senstag == 1:
                    print("Temp: ", self.peripheral.IRtemperature.read(), ' C')
                    print("Humidity: ", self.peripheral.humidity.read(),  ' Hrel')
                    print("Barometer: ", self.peripheral.barometer.read())
                    print("Accelerometer: ", self.peripheral.accelerometer.read())
                    print("Magnetometer: ", self.peripheral.magnetometer.read() , " uT")
                    print("Gyroscope: ", self.peripheral.gyroscope.read())
                    print("Light: ", self.peripheral.lightmeter.read())
                    
                    self.messageQueue.put(TagNotificationMessage(self.tag, 
                    "sensorTag&temperature=" + str(self.peripheral.IRtemperature.read()) +
                    "&humidity=" + str(self.peripheral.humidity.read()) +
                    "&barometer=" + str(self.peripheral.barometer.read()) +
                    "&accelerometer=" + str(self.peripheral.accelerometer.read()) +
                    "&magnetometer=" + str(self.peripheral.magnetometer.read()) +
                    "&gyroscope=" + str(self.peripheral.gyroscope.read()) +
                    "&lightmeter=" + str(self.peripheral.lightmeter.read())
                    ))
                    
                    time.sleep(10.0)
                else:
                    time.sleep(1.0)

        except btle.BTLEException as e:
            if e.code == btle.BTLEException.DISCONNECTED:
                print(ANSI_GREEN + "[TagConnectionThread] Device '" + self.tag.mac + "' was disconnected." + ANSI_OFF)
            else:
                print(ANSI_GREEN + "[TagConnectionThread] Error!" + str(e.message) + ANSI_OFF)
                raise e
        except:
            print(ANSI_GREEN + "[TagConnectionThread] " + str(traceback.format_exc()) + ANSI_OFF)
        finally:
            self.isDead = True

            if self.peripheral:
                self.peripheral.disconnect()

            self.tag.rssi=-100
            self.messageQueue.put(TagDisconnectedMessage(self.tag))

            print(ANSI_GREEN + "[TagConnectionThread] connection loop shutdown" + ANSI_OFF)
