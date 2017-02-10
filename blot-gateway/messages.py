import time

COMMAND_CONNECT_TAG = "CONNECT_TAG"

class Message:
    def __init__(self):
        self.queryTemplate = "?action=%s&tag_mac=%s&gateway_mac=%s&gateway_ip=%s&time=%d"

    def toUrlQuery():
        return ""

class DiscoverTagMessage(Message):
    def __init__(self, tag):
        Message.__init__(self)

        self.tag = tag
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_DISCOVERED",
            self.tag.mac,
            gateway_mac,
            gateway_ip,
            self.time
        )

class ConnectToTagCommandMessage(Message):
    def __init__(self, mac):
        Message.__init__(self)
        self.mac = mac

    def toUrlQuery(self, gateway_mac, gateway_ip):
        raise "ERROR, CommandMessage can't be converted into url query"
