#!/usr/bin/python

import sys, threading, time
from Queue import Queue
from client import Client
from messages import DiscoverTagMessage, ConnectToTagCommandMessage, TagDisconnectedMessage, TagNotificationMessage
from tagconnection import TagConnectionThread
from tagscanner import ScanLoopThread
from utils import ANSI_CYAN, ANSI_OFF, list_contains, list_find

class WorkerThread(threading.Thread):

    def __init__(self, messageQueue, queueLock, blotClient):
        threading.Thread.__init__(self)

        self.messageQueue = messageQueue
        self.queueLock = queueLock
        self.blotClient = blotClient
        self.tagConnections = []

    def pruneTagConnections(self):
        for conn in self.tagConnections[:]:
            if conn.isDead:
                self.tagConnections.remove(conn)

    def hasElements(self):
        self.queueLock.acquire()
        hasElements = self.messageQueue.empty()
        self.queueLock.release()
        return hasElements


    def handleMessageQueue(self):
        while not self.hasElements():
            self.queueLock.acquire()
            message = self.messageQueue.get()
            self.queueLock.release()

            print(ANSI_CYAN + "[WorkerThread] processing message " + str(message) + ANSI_OFF)

            if isinstance(message, DiscoverTagMessage) or isinstance(message, TagDisconnectedMessage) or isinstance(message, TagNotificationMessage):
                self.blotClient.sendMessage(message)
            elif isinstance(message, ConnectToTagCommandMessage):
                if list_contains(self.tagConnections, lambda t: t.mac == message.mac):
                    print(ANSI_CYAN + "[WorkerThread] Connection to Tag '" + message.mac + "' already established" + ANSI_OFF)
                    continue

                tagConnection = TagConnectionThread(self.messageQueue, self.queueLock, message.mac)
                self.tagConnections.append(tagConnection)

                print(ANSI_CYAN + "[WorkerThread] starting new tag connection thread" + ANSI_OFF)
                tagConnection.daemon = True
                tagConnection.start()
                print(ANSI_CYAN + "[WorkerThread] started new tag connection thread" + ANSI_OFF)
            elif isinstance(message, BeepTagCommandMessage):
                conn = list_find(self.tagConnections, lambda t: t.mac == message.mac)
                if conn:
                    conn.triggerBeep()
                else:
                    print(ANSI_CYAN + "[WorkerThread] Tag '" + message.mac + "' is not yet connected (no connection found)" + ANSI_OFF)
            else:
                print(ANSI_CYAN + "[WorkerThread] Error: unknown message type " + str(message) + ANSI_OFF)


    def run(self):
        print(ANSI_CYAN + "[WorkerThread] Worker loop start" + ANSI_OFF)

        while True:
            #print(ANSI_CYAN + "[WorkerThread] .") # debu + ANSI_OFFg

            self.pruneTagConnections()

            self.handleMessageQueue()

            time.sleep(0.3)
        print(ANSI_CYAN + "[WorkerThread] Worker loop shutdown" + ANSI_OFF)


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
