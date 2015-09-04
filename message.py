class Message(object):
    def __init__(self, backend, channel, nickname, text):
        self.backend = backend
        self.channel = channel
        self.nickname = nickname
        self.text = text

    def pretty_print(self):
        return "[" + self.nickname + "@" + self.channel + "-" + self.backend + "] " + self.text

class MessageSink(object):
    def __init__(self, backend, channel):
        self.backend = backend
        self.channel = channel
