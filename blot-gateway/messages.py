import time

class Message:
    def __init__(self):
        self.queryTemplate = "?action={}&tag_mac={}&gateway_mac={}&gateway_ip={}&time={}"

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
