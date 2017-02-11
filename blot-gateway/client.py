import requests
from messages import ConnectToTagCommandMessage, COMMAND_CONNECT_TAG, COMMAND_BEEP_TAG
from utils import ANSI_YELLOW, ANSI_OFF

class Client:
    def __init__(self, messageQueue, queueLock, serverUrl, gateway_mac, gateway_ip):
        self.messageQueue = messageQueue
        self.queueLock = queueLock
        self.serverUrl = serverUrl
        self.gateway_mac = gateway_mac
        self.gateway_ip = gateway_ip

    def handleConnectResponse(self, commandMessage):
        print(ANSI_YELLOW + "[Client] Received Connect Command for Tag '" + str(commandMessage["tag_mac"]) + "'" + ANSI_OFF)

        if not isinstance(commandMessage["tag_mac"], basestring):
            print(ANSI_YELLOW + "[Client] invalid message format expected string for mac, got '" + str(commandMessage["tag_mac"]) + "'" + ANSI_OFF)
            return

        self.queueLock.acquire()
        self.messageQueue.put(ConnectToTagCommandMessage(commandMessage["tag_mac"]))
        self.queueLock.release()

    def handleBeepResponse(self, commandMessage):
        print(ANSI_YELLOW + "[Client] Received Beep Command for Tag '" + str(commandMessage["tag_mac"]) + "'" + ANSI_OFF)

        if not isinstance(commandMessage["tag_mac"], basestring):
            print(ANSI_YELLOW + "[Client] invalid message format expected string for mac, got '" + str(commandMessage["tag_mac"]) + "'" + ANSI_OFF)
            return

        #self.queueLock.acquire()
        #self.messageQueue.put(BeepTagCommandMessage(commandMessage["tag_mac"]))
        #self.queueLock.release()


    def handleResponse(self, result):
        if not isinstance(result, list):
            result = [result]

        for commandMessage in result:
            if commandMessage and commandMessage.has_key("command"):
                if not isinstance(commandMessage["command"], basestring):
                    print(ANSI_YELLOW + "[Client] invalid message format '" + str(commandMessage["command"]) + "'" + ANSI_OFF)
                    continue

                if commandMessage["command"] == COMMAND_CONNECT_TAG:
                    self.handleConnectResponse(commandMessage)
                elif commandMessage["command"] == COMMAND_BEEP_TAG:
                    self.handleBeepResponse(commandMessage)
                else:
                    print(ANSI_YELLOW + "[Client] unknown result command '" + commandMessage["command"] + "'" + ANSI_OFF)

    def sendMessage(self, message):
        print(ANSI_YELLOW + "[Client] sendMessage" + str(message) + ANSI_OFF)

        url = self.serverUrl +  message.toUrlQuery(self.gateway_mac, self.gateway_ip)
        print(ANSI_YELLOW + "[Client] GET " + url + ANSI_OFF)
        res = requests.get(url)
        print(ANSI_YELLOW + "[Client] Response: %s '%s'" % (res.status_code, res.text) + ANSI_OFF)

        if res.text == "OK":
            print(ANSI_YELLOW + "[Client] No Command response" + ANSI_OFF)
        else:
            self.handleResponse(res.json())
