#!/usr/bin/python

import sys, threading, time, socket
from messagequeue import MessageQueue
from client import Client
from messages import * #GWStartupMessage, GWShutdownMessage
from tagconnection import TagConnectionThread
from tagscanner import ScanLoopThread
from utils import ANSI_CYAN, ANSI_OFF, list_contains, list_find
from uuid import getnode as get_mac
from tagcache import TagCache
from httplistener import HttpListener
from config import Config

class WorkerThread(threading.Thread):

    def __init__(self, messageQueue, blotClient, tagCache):
        threading.Thread.__init__(self)

        self.messageQueue = messageQueue
        self.blotClient = blotClient
        self.tagCache = tagCache
        self.tagConnections = []
        #self.threadsRunning = threadsRunning
        self.messageQueue.put(GWStartupMessage()) #todo

    def pruneTagConnections(self):
        for conn in self.tagConnections[:]:
            if conn.isDead:
                self.tagConnections.remove(conn)

    def handleConnectToTagMessage(self, message):
        if list_contains(self.tagConnections, lambda t: t.tag.mac == message.mac):
            print(ANSI_CYAN + "[WorkerThread] Connection to Tag '" + message.mac + "' already established" + ANSI_OFF)
            return

        tag = self.tagCache.findByMac(message.mac)
        if not tag:
            print(ANSI_CYAN + "[WorkerThread] no Tag with that mac found (" + str(message.mac) + ")" + ANSI_OFF)
            return

        tagConnection = TagConnectionThread(self.messageQueue, tag)
        self.tagConnections.append(tagConnection)

        print(ANSI_CYAN + "[WorkerThread] starting new tag connection thread" + ANSI_OFF)
        tagConnection.daemon = True
        tagConnection.start()
        print(ANSI_CYAN + "[WorkerThread] started new tag connection thread" + ANSI_OFF)

    def handleBeepTagMessage(self, message):
        conn = list_find(self.tagConnections, lambda t: t.tag.mac == message.mac)
        if conn:
            conn.triggerBeep()
        else:
            print(ANSI_CYAN + "[WorkerThread] Tag '" + message.mac + "' is not yet connected (no connection found)" + ANSI_OFF)

    def processMessage(self, message):
        if isinstance(message, ClientMessage):
            self.blotClient.sendMessage(message)
        elif isinstance(message, GWStartupMessage): #GW start
            self.blotClient.sendMessage(message)
        elif isinstance(message, GWShutdownMessage): #GW stop
            self.blotClient.sendMessage(message)
        elif isinstance(message, SensorTagMessage): #sensortag
            self.blotClient.sendMessage(message)
        elif isinstance(message, TagUpdateMessage): #tag update
            self.blotClient.sendMessage(message)
        elif isinstance(message, ConnectToTagCommandMessage):
            self.handleConnectToTagMessage(message)
        elif isinstance(message, BeepTagCommandMessage):
            self.handleBeepTagMessage(message)
        else:
            print(ANSI_CYAN + "[WorkerThread] Error: unknown message type " + str(message) + ANSI_OFF)


        #if isinstance(message, Message):
        #    self.blotClient.sendMessage(message)


    def processMessageQueue(self):
        while not self.messageQueue.empty():
            message = self.messageQueue.get()

            print(ANSI_CYAN + "[WorkerThread] processing message " + str(message) + ANSI_OFF)

            self.processMessage(message)

    def run(self):
        print(ANSI_CYAN + "[WorkerThread] Worker loop start" + ANSI_OFF)

        while True:
            #print(ANSI_CYAN + "[WorkerThread] .") # debu + ANSI_OFFg
            self.pruneTagConnections()
            self.processMessageQueue()
            time.sleep(0.3)
        print(ANSI_CYAN + "[WorkerThread] Worker loop shutdown" + ANSI_OFF) #ralf - nie gesehen

def createBlotClient(messageQueue):
    mac = get_mac()
    mac_str = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
    ip = socket.gethostbyname(socket.getfqdn())

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("gmail.com",80))
    ip = s.getsockname()[0]
    s.close()

    blotClient = Client(messageQueue, Config.ServerUrl, mac_str, ip)
    return blotClient

def runGateway():
    print("Starting BluetoothLowEnergy of Things (BLoT) Gateway  ")
    messageQueue = MessageQueue()

    blotClient = createBlotClient(messageQueue)
    tagCache = TagCache()

    #threadsRunning = True
    threads = [
        ScanLoopThread(messageQueue, tagCache),
        WorkerThread(messageQueue, blotClient, tagCache),
        HttpListener(messageQueue, tagCache)
    ]

    for thread in threads:
        thread.daemon = True #False
        thread.start()

    messageQueue.put(GWStartupMessage())

    try:
        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        #threadsRunning = False
        print '\n! Received keyboard interrupt, quitting threads.\n' #Ralf: wo werden die beendet ?

    messageQueue.put(GWShutdownMessage()) #todo
    print "Gateway Shutdown"

if __name__ == "__main__":
    runGateway()


#todo
# GW start / stop msg
# RSSI aktuell
# battery value update
# Thread daemon false und kontrolliert beenden
# msg fuer TI Sensor TAG daten an DB Server
# schoenere Loesung fuer IP adresse
# port 3333 belegt meldung
