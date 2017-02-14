import time

COMMAND_CONNECT_TAG = "CONNECT_TAG"
COMMAND_BEEP_TAG = "BEEP_TAG"

class Message:
    def __init__(self):
        self.queryTemplate = "?action=%s&tag_mac=%s&gateway_mac=%s&gateway_ip=%s&time=%d"

    def toUrlQuery():
        return ""

class DiscoverTagMessage(Message):
    def __init__(self, tag):
        Message.__init__(self)

        self.queryTemplate += "&tag_name=%s"
        self.tag = tag
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_DISCOVERED",
            self.tag.mac,
            gateway_mac,
            gateway_ip,
            self.time,
            self.tag.name
        )

class TagConnectedMessage(Message):
    def __init__(self, mac):
        Message.__init__(self)

        self.mac = mac
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_CONNECTED",
            self.mac,
            gateway_mac,
            gateway_ip,
            self.time
        )

class TagDisconnectedMessage(Message):
    def __init__(self, mac):
        Message.__init__(self)

        self.mac = mac
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_DISCONNECTED",
            self.mac,
            gateway_mac,
            gateway_ip,
            self.time
        )

class TagNotificationMessage(Message):
    def __init__(self, mac, type):
        Message.__init__(self)

        self.queryTemplate += "&notification_type=%s"

        self.mac = mac
        self.type = type
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_NOTIFICATION",
            self.mac,
            gateway_mac,
            gateway_ip,
            self.time,
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
