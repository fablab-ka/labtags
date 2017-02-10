import requests
from messages import ConnectToTagCommandMessage, COMMAND_CONNECT_TAG

class Client:
    def __init__(self, serverUrl, gateway_mac, gateway_ip):
        self.serverUrl = serverUrl
        self.gateway_mac = gateway_mac
        self.gateway_ip = gateway_ip

    def sendMessage(self, message):
        print("[Client] sendMessage", message)

        url = self.serverUrl +  message.toUrlQuery(self.gateway_mac, self.gateway_ip)
        print("[Client] GET " + url)
        res = requests.get(url)
        print("[Client] Response: %s '%s'" % (res.status_code, res.text))

        result = res.json()

        if not isinstance(result, list):
            result = [result]

        for commandMessage in result:
            if commandMessage and commandMessage.has_key("command"):
                if not isinstance(commandMessage["command"], string):
                    print("invalid message format")
                    continue

                if commandMessage["command"] == COMMAND_CONNECT_TAG:
                    print("[Client] Received Connect Command for Tag '" + commandMessage.tag_mac + "'")

                    self.queueLock.acquire()
                    self.messageQueue.put(ConnectToTagCommandMessage(commandMessage.tag_mac))
                    self.queueLock.release()
                else:
                    print("[Client] unknown result command '" + commandMessage["command"] + "'")
