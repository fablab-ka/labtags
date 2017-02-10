class Message:
    pass

class DiscoverTagMessage(Message):
    def __init__(self, tag):
        self.tag = tag
