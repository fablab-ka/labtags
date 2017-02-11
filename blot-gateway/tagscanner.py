import threading, time
from bluepy import btle

from tag import Tag
from utils import list_contains
from messages import DiscoverTagMessage

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
                print("[TagScanner] Device not connectable", d.addr)
                continue

            print("[TagScanner] Tag found '%s' '%s' '%s'" % (d.addr, d.addrType, d.rssi))
            print(d.getScanData())

            name = d.getValueText(9)
            result.append(Tag(d.addr, d.addrType, name))

        return result


class ScanLoopThread(threading.Thread):

    def __init__(self, messageQueue, queueLock):
        threading.Thread.__init__(self)

        self.messageQueue = messageQueue
        self.queueLock = queueLock
        self.scanner = TagScanner()
        self.tagCache = []
        self.rediscoverTimeout = 5

    def pruneTagCache(self):
        now = time.time()
        for tag in self.tagCache[:]:
            if (now - tag.discovered) > self.rediscoverTimeout:
                self.tagCache.remove(tag)

    def discoverTags(self):
        tags = self.scanner.scan()

        for tag in tags:
            if not list_contains(self.tagCache, lambda t: t.mac == tag.mac):
                print("[ScanThread] discovered Tag " + tag.mac)

                self.tagCache.append(tag)

                self.queueLock.acquire()
                self.messageQueue.put(DiscoverTagMessage(tag))
                self.queueLock.release()

    def run(self):
        print("[ScanThread] scan loop start")

        while True:
            self.pruneTagCache()

            self.discoverTags()

            time.sleep(0.1)

        print("[ScanThread] scan loop shutdown")
