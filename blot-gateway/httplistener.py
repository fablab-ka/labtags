import threading
from flask import Flask
from utils import ANSI_BLUE, ANSI_OFF
from config import Config
from messages import BeepTagCommandMessage

class HttpListener(threading.Thread):
    def __init__(self, messageQueue, tagCache):
        threading.Thread.__init__(self)

        self.messageQueue = messageQueue
        self.tagCache = tagCache
        self.app = Flask("Blot HTTP Listener")

    def handleRequest(self, mac):
        if not mac:
            return 'ERROR: no mac given'
        
        self.messageQueue.put(BeepTagCommandMessage(mac))
        return 'OK'

    def run(self):
        print(ANSI_BLUE + "[HttpListener] Starting on Port '" + str(Config.NotificationServiceUrl) + "'" + ANSI_OFF)

        self.handleRequest = self.app.route("/<mac>")(lambda mac: self.handleRequest(mac))
        self.app.run(port=Config.NotificationServiceUrl)

        print(ANSI_BLUE + "[HttpListener] Shutting down" + ANSI_OFF)
