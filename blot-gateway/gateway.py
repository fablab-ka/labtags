#!/usr/bin/python

import sys, threading, time
from Queue import Queue
from utils import list_contains
from client import Client
from messages import DiscoverTagMessage
from tagconnection import TagConnectionThread
from tagscanner import ScanLoopThread
from httplistener import HttpListenerThread

class WorkerThread(threading.Thread):

    def __init__(self, messageQueue, queueLock, blotClient):
        threading.Thread.__init__(self)

        self.messageQueue = messageQueue
        self.queueLock = queueLock
        self.blotClient = blotClient
        self.tagConnections = []

    def pruneTagConnections(self):
        pass # todo

    def handleMessageQueue(self):
        self.queueLock.acquire()
        while not self.messageQueue.empty():
            message = self.messageQueue.get()

            if isinstance(message, DiscoverTagMessage):
                self.blotClient.sendMessage(message)
            elif isinstance(message, ConnectTagMessage):
                tagConnection = TagConnectionThread(self.messageQueue, self.queueLock, message.tag)
                self.tagConnections.append(tagConnection)
            else:
                print("[WorkerThread] Error: unknown message type " str(message))

    def run(self):
        print("[WorkerThread] Worker loop start")

        while True:
            self.pruneTagConnections()

            self.handleMessageQueue()

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
        WorkerThread(messageQueue, queueLock, blotClient),
        HttpListenerThread(messageQueue, queueLock, 8080)
    ]

    for thread in threads:
        thread.daemon = True
        thread.start()

    try:
        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        print '\n! Received keyboard interrupt, quitting threads.\n'

    print "Gateway Shutdown"
