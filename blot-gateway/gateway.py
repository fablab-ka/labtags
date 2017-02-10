#!/usr/bin/python

import sys, threading, time, requests
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
        self.currentTagList = []

    def run(self):
        print("[ScanThread] scan loop start")

        while True:
            tags = self.scanner.scan()

            for tag in tags:
                if not list_contains(self.currentTagList, lambda t: t.mac == tag.mac):
                    print("[ScanThread] discovered Tag", tag.mac)
                    self.currentTagList.append(tag)

                    self.queueLock.acquire()
                    self.messageQueue.put(DiscoverTagMessage(tag))
                    self.queueLock.release()

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
                message = q.get()

                if isinstance(message, DiscoverTagMessage):
                    self.blotClient.sendMessage(message)
            self.queueLock.release()

            time.sleep(300)
        print("[WorkerThread] Worker loop shutdown")


if __name__ == "__main__":
    print("Starting BlOT Gateway")

    queueLock = threading.Lock()
    messageQueue = Queue()
    blotClient = Client('http://homeserver.spdns.org/biot.php')

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
