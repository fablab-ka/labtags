import threading

from utils import list_contains

class TagCache:
    def __init__(self):
        self.data = []
        self.threadLock = threading.Lock()

    def append(self, tag):
        self.threadLock.acquire()
        self.data.append(tag)
        self.threadLock.release()

    def remove(self, tag):
        self.threadLock.acquire()
        self.data.remove(tag)
        self.threadLock.release()

    def hasTagByMac(self, mac):
        self.threadLock.acquire()
        result = list_contains(self.data, lambda t: t.mac == mac)
        self.threadLock.release()
        
        return result

    def findByMac(self, mac):
        result = None

        self.threadLock.acquire()
        for tag in self.data:
            if tag.mac == mac:
                result = tag
                break
        self.threadLock.release()

        return result
