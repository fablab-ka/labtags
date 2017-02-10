import requests

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
