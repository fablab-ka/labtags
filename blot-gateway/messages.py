import time

COMMAND_CONNECT_TAG = "CONNECT_TAG"
COMMAND_BEEP_TAG = "BEEP_TAG"

class Message:
    def __init__(self):
        self.queryTemplate = "?action=%s&tag_mac=%s&gateway_mac=%s&gateway_ip=%s&time=%d"

    def toUrlQuery():
        return ""

class ClientMessage(Message):
    def __init__(self, tag):
        Message.__init__(self)

        self.queryTemplate += "&tag_name=%s&tag_rssi=%s"

class DiscoverTagMessage(ClientMessage):
    def __init__(self, tag):
        ClientMessage.__init__(self)

        self.tag = tag
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_DISCOVERED",
            self.tag.mac,
            gateway_mac,
            gateway_ip,
            self.time,
            self.tag.rssi,
            self.tag.name
        )

class TagDisconnectedMessage(ClientMessage):
    def __init__(self, tag):
        ClientMessage.__init__(self)

        self.tag = tag
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_DISCONNECTED",
            self.tag.mac,
            gateway_mac,
            gateway_ip,
            self.time,
            self.tag.rssi,
            self.tag.name
        )

class TagNotificationMessage(ClientMessage):
    def __init__(self, tag, type):
        ClientMessage.__init__(self)

        self.queryTemplate += "&notification_type=%s"

        self.tag = tag
        self.type = type
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_NOTIFICATION",
            self.tag.mac,
            gateway_mac,
            gateway_ip,
            self.time,
            self.tag.rssi,
            self.tag.name,
            self.type
        )

class ConnectToTagCommandMessage(Message):
    def __init__(self, mac):
        Message.__init__(self)
        self.mac = mac

    def toUrlQuery(self, gateway_mac, gateway_ip):
        raise "ERROR, CommandMessage can't be converted into url query"

class BeepTagCommandMessage(Message):
    def __init__(self, mac):
        Message.__init__(self)
        self.mac = mac

    def toUrlQuery(self, gateway_mac, gateway_ip):
        raise "ERROR, CommandMessage can't be converted into url query"
