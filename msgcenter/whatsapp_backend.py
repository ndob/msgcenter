from backend import Backend

class WhatsAppBackend(Backend):
    def __init__(self, name, phone, password):
        self.name = name
        self.phone = phone
        self.password = password
        self.channels = []

    def start(self, incoming, outgoing):
        self.incoming = incoming
        self.outgoing = outgoing

    def join(self, channel):
        self.channels.append(channel)
