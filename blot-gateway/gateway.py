#!/usr/bin/python

import sys, threading, time
from Queue import Queue
from client import Client
from messages import DiscoverTagMessage, ConnectToTagCommandMessage
from tagconnection import TagConnectionThread
from tagscanner import ScanLoopThread

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
        hasElements = self.messageQueue.empty()
        self.queueLock.release()

        while not hasElements:
            self.queueLock.acquire()
            message = self.messageQueue.get()
            self.queueLock.release()

            print("[WorkerThread] processing message " + str(message))

            if isinstance(message, DiscoverTagMessage):
                self.blotClient.sendMessage(message)
            elif isinstance(message, ConnectToTagCommandMessage):
                print("[WorkerThread] connect to tag command is being processed")
                tagConnection = TagConnectionThread(self.messageQueue, self.queueLock, message.mac)
                self.tagConnections.append(tagConnection)

                print("[WorkerThread] starting new tag connection thread")
                tagConnection.daemon = True
                tagConnection.start()
                print("[WorkerThread] started new tag connection thread")
            else:
                print("[WorkerThread] Error: unknown message type " + str(message))


    def run(self):
        print("[WorkerThread] Worker loop start")

        while True:
            self.pruneTagConnections()

            self.handleMessageQueue()

            time.sleep(0.3)
        print("[WorkerThread] Worker loop shutdown")


if __name__ == "__main__":
    print("Starting BlOT Gateway")

    queueLock = threading.Lock()
    messageQueue = Queue()
    blotClient = Client(messageQueue, queueLock, 'http://homeserver.spdns.org/blot.php', "b8:27:eb:0b:de:50", "192.168.1.88")

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
