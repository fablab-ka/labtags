#!/usr/bin/python

import sys, threading, time
from Queue import Queue
from tagscanner import TagScanner
from utils import list_contains
from messages import DiscoverTagMessage
from client import Client


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
                print("[ScanThread] discovered Tag" + tag.mac)

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

class WorkerThread(threading.Thread):

    def __init__(self, messageQueue, queueLock, blotClient):
        threading.Thread.__init__(self)

        self.messageQueue = messageQueue
        self.queueLock = queueLock
        self.scanner = TagScanner()
        self.blotClient = blotClient

    def run(self):
        print("[WorkerThread] Worker loop start")

        while True:
            self.queueLock.acquire()
            while not self.messageQueue.empty():
                message = self.messageQueue.get()

                if isinstance(message, DiscoverTagMessage):
                    self.blotClient.sendMessage(message)
            self.queueLock.release()

            time.sleep(0.3)
        print("[WorkerThread] Worker loop shutdown")


if __name__ == "__main__":
    print("Starting BlOT Gateway")

    queueLock = threading.Lock()
    messageQueue = Queue()
    blotClient = Client('http://homeserver.spdns.org/blot.php', "b8:27:eb:0b:de:50", "192.168.1.88")

    threads = [
        ScanLoopThread(messageQueue, queueLock),
        WorkerThread(messageQueue, queueLock, blotClient)
    ]

    for thread in threads:
        thread.daemon = True
        thread.start()

    try:
        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        print '\n! Received keyboard interrupt, quitting threads.\n'

    print "Gateway Shutdown"
