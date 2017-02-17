import threading
from Queue import Queue

class MessageQueue:
    def __init__(self):
        self.queue = Queue()
        self.threadLock = threading.Lock()

    def empty(self):
        self.threadLock.acquire()
        result = self.queue.empty()
        self.threadLock.release()
        return result

    def get(self):
        self.threadLock.acquire()
        result = self.queue.get()
        self.threadLock.release()
        return result

    def put(self, message):
        self.threadLock.acquire()
        self.queue.put(message)
        self.threadLock.release()
