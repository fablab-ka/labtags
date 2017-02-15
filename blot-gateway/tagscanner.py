import threading, time, sys
from bluepy import btle

from tag import Tag
from messages import DiscoverTagMessage
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
                print(ANSI_RED + "[TagScanner] Device not connectable", d.addr + ANSI_OFF)
                continue

            #print(ANSI_RED + "[TagScanner] Tag found '%s' '%s' '%s'" % (d.addr, d.addrType, d.rssi) + ANSI_OFF)
            #print(ANSI_RED + "[TagScanner] " + str(d.getScanData()) + ANSI_OFF)

            name = d.getValueText(9)
            result.append(Tag(d.addr, d.addrType, name))

        return result


class ScanLoopThread(threading.Thread):

    def __init__(self, messageQueue, queueLock, tagCache):
        threading.Thread.__init__(self)

        self.messageQueue = messageQueue
        self.queueLock = queueLock
        self.scanner = TagScanner()
        self.tagCache = tagCache
        self.rediscoverTimeout = 5

    def pruneTagCache(self):
        now = time.time()
        for tag in self.tagCache[:]:
            if (now - tag.discovered) > self.rediscoverTimeout:
                self.tagCache.remove(tag)

    def discoverTags(self):
        tags = self.scanner.scan()

        for tag in tags:
            if not self.tagCache.hasTagByMac(tag.mac):
                print(ANSI_RED + "[ScanThread] discovered Tag '" + str(tag.mac) + "' name: '" + str(tag.name) + "'" + ANSI_OFF)

                self.tagCache.append(tag)

                self.queueLock.acquire()
                self.messageQueue.put(DiscoverTagMessage(tag))
                self.queueLock.release()

    def run(self):
        print(ANSI_RED + "[ScanThread] scan loop start" + ANSI_OFF)

        while True:
            try:
                self.pruneTagCache()

                self.discoverTags()
            except:
                print(ANSI_RED + "[ScanThread] " + sys.exec_info()[0] + ANSI_OFF)

            time.sleep(0.1)

        print(ANSI_RED + "[ScanThread] scan loop shutdown" + ANSI_OFF)
