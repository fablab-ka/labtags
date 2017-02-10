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
        print("scan loop start")

        while True:
            tags = self.scanner.scan()

            for tag in tags:
                if not list_contains(self.currentTagList, lambda t: t.mac == tag.mac):
                    currentTagList.append(tag)

                    self.queueLock.acquire()
                    self.messageQueue.put(DiscoverTagMessage(tag))
                    self.queueLock.release()

        print("scan loop shutdown")

class WorkerThread(threading.Thread):

    def __init__(self, messageQueue, queueLock, blotClient):
        threading.Thread.__init__(self)
        
        self.messageQueue = messageQueue
        self.queueLock = queueLock
        self.scanner = TagScanner()
        self.blotClient = blotClient

    def run(self):
        print("worker loop start")

        while True:
            while not self.messageQueue.empty():
                self.queueLock.acquire()
                message = q.get()
                self.queueLock.release()

                if isinstance(message, DiscoverTagMessage):
                    self.blotClient.sendMessage(message)

            time.sleep(300)
        print("worker loop shutdown")


if __name__ == "__main__":
    print("Starting BlOT Gateway")

    queueLock = threading.Lock()
    messageQueue = Queue()
    blotClient = Client('http://google.com/') # todo

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
