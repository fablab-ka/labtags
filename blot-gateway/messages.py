import time

COMMAND_CONNECT_TAG = "CONNECT_TAG"
COMMAND_BEEP_TAG = "BEEP_TAG"

#ralf: s&tag_mac=%s zu ClientMessage verschoben
class Message:
    def __init__(self):
        self.queryTemplate = "?action=%s&gateway_mac=%s&gateway_ip=%s&time=%d"

    def toUrlQuery(self):
        return ""

#ralf: added
class GWShutdownMessage(Message):
    def __init__(self):
        Message.__init__(self)
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "GW_SHUTDOWN",
            gateway_mac,
            gateway_ip,
            self.time
        )

#ralf: added
class GWStartupMessage(Message):
    def __init__(self):
        Message.__init__(self)
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "GW_STARTUP",
            gateway_mac,
            gateway_ip,
            self.time
        )

class ClientMessage(Message):
    def __init__(self, tag):
        Message.__init__(self)
        self.queryTemplate += "&tag_mac=%s&tag_name=%s&tag_rssi=%s&tag_battlvl=%s"


class DiscoverTagMessage(ClientMessage):
    def __init__(self, tag):
        ClientMessage.__init__(self, tag)

        self.tag = tag
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_DISCOVERED",
            gateway_mac,
            gateway_ip,
            self.time,
            self.tag.mac,
            self.tag.name,
            self.tag.rssi,
            self.tag.battlvl
        )

class TagConnectedMessage(ClientMessage):
    def __init__(self, tag):
        ClientMessage.__init__(self, tag)

        self.tag = tag
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_CONNECTED",
            gateway_mac,
            gateway_ip,
            self.time,
            self.tag.mac,
            self.tag.name,
            self.tag.rssi,
            self.tag.battlvl
        )

class TagDisconnectedMessage(ClientMessage):
    def __init__(self, tag):
        ClientMessage.__init__(self, tag)

        self.tag = tag
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_DISCONNECTED",
            gateway_mac,
            gateway_ip,
            self.time,
            self.tag.mac,
            self.tag.name,
            self.tag.rssi,
            self.tag.battlvl
        )

#ralf: added
class TagUpdateMessage(ClientMessage):
    def __init__(self, tag):
        ClientMessage.__init__(self, tag)

        self.tag = tag
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_UPDATE",
            gateway_mac,
            gateway_ip,
            self.time,
            self.tag.mac,
            self.tag.name,
            self.tag.rssi, #send new value to DB
            self.tag.battlvl #send new value to DB
        )

class TagNotificationMessage(ClientMessage):
    def __init__(self, tag, type):
        ClientMessage.__init__(self, tag)

        self.queryTemplate += "&notification_type=%s"

        self.tag = tag
        self.type = type
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "TAG_NOTIFICATION",
            gateway_mac,
            gateway_ip,
            self.time,
            self.tag.mac,
            self.tag.name,
            self.tag.rssi,
            self.tag.battlvl,
            self.type
        )

class SensorTagMessage(ClientMessage):
    def __init__(self, tag):
        ClientMessage.__init__(self, tag)

        self.tag = tag
        self.time = time.time()

    def toUrlQuery(self, gateway_mac, gateway_ip):
        return self.queryTemplate % (
            "SENSOR_TAG_UPDATE",
            gateway_mac,
            gateway_ip,
            self.time,
            self.tag.mac,
            self.tag.name,
            self.tag.rssi,
            self.tag.battlvl
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
