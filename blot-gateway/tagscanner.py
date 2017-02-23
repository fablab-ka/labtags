import threading, time, traceback
from bluepy import btle

from tag import Tag
from messages import DiscoverTagMessage, GWStartupMessage, GWShutdownMessage
from utils import ANSI_RED, ANSI_OFF

class TagScanner:
    def __init__(self):
        #btle.Debugging = True
        self.timeout = 4
        self.hci = 0
        self.scanner = btle.Scanner(self.hci)

    def scan(self):
        result = []

        devices = self.scanner.scan(self.timeout)

        self.scanner.clear()

        for d in devices:
            if not d.connectable:
                print(ANSI_RED + "[TagScanner] Device not connectable", d.addr + ANSI_OFF )
                continue

            #print(ANSI_RED + "[TagScanner] Tag found '%s' '%s' '%s'" % (d.addr, d.addrType, d.rssi) + ANSI_OFF)
            #print(ANSI_RED + "[TagScanner] " + str(d.getScanData()) + ANSI_OFF)

            name = d.getValueText(9)
            result.append(Tag(d.addr, d.addrType, name, d.rssi,-1))

        return result


class ScanLoopThread(threading.Thread):

    def __init__(self, messageQueue, tagCache):
        threading.Thread.__init__(self)

        self.messageQueue = messageQueue
        self.tagCache = tagCache
        self.scanner = TagScanner()
        self.rediscoverTimeout = 5

    def pruneTagCache(self):
        now = time.time()
        for tag in self.tagCache.getData():
            if (now - tag.discovered) > self.rediscoverTimeout:
                self.tagCache.remove(tag)

    def discoverTags(self):
        tags = self.scanner.scan()

        for tag in tags:
            if not self.tagCache.hasTagByMac(tag.mac):
                print(ANSI_RED + "[ScanThread] discovered Tag '" + str(tag.mac) + "' name: '" + str(tag.name) + "'" + ANSI_OFF)

                self.tagCache.append(tag)

                self.messageQueue.put(DiscoverTagMessage(tag))

    def run(self):
        print(ANSI_RED + "[ScanThread] scan loop start" + ANSI_OFF)
        #self.messageQueue.put(GWStartupMessage()) #todo
        while True:
            try:
                self.pruneTagCache()

                self.discoverTags()
            except:
                print(ANSI_RED + "[ScanThread] " + str(traceback.format_exc()) + ANSI_OFF)

            time.sleep(0.1)
        #self.messageQueue.put(GWShutdownMessage()) #todo
        print(ANSI_RED + "[ScanThread] scan loop shutdown" + ANSI_OFF) #Ralf: Diese Meldung kommt imo nie ! #todo
