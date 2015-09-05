from backend import Backend
from message import Message
from logger import logger
import irc.bot
import time

class IrcBackend(Backend):
    def __init__(self, name, server_address, port, nickname):
        irc.client.ServerConnection.buffer_class = irc.buffer.LenientDecodingLineBuffer
        self.reactor = irc.client.Reactor()
        self.channels = []
        self.name = name
        self.server_address = server_address
        self.port = port
        self.nickname = nickname

    def start(self, incoming, outgoing):
        self.incoming = incoming
        self.outgoing = outgoing

        self._connect()

        self.reactor.add_global_handler("welcome", self.on_connect)
        self.reactor.add_global_handler("disconnect", self.on_disconnect)
        self.reactor.add_global_handler("pubmsg", self.on_newmsg)

        while 1:
            if self.incoming.poll():
                info = self.incoming.recv()
                self.send_msg(info["to"], info["msg"].pretty_print())
            
            self.reactor.process_once()
            time.sleep(0.2)

    def _connect(self):
        logger.debug("IrcBackend: connecting to " + self.name)
        try:
            self.server = self.reactor.server()
            self.server.connect(self.server_address, self.port, self.nickname)
        except irc.client.ServerConnectionError:
            logger.error("IrcBackend: error connecting to " + self.name)
            time.sleep(5)
            self._connect()

    def on_connect(self, connection, event):
        logger.debug("IrcBackend: connected to " + self.name)

        for chan in self.channels:
            if irc.client.is_channel(chan):
                logger.debug("IrcBackend: joining to " + chan + "@" + self.name)
                connection.join(chan)

    def on_disconnect(self, connection, event):
        logger.debug("IrcBackend: disconnected from " + self.name + " and trying to reconnect")
        self._connect()
        pass

    def on_newmsg(self, channel, event):
        logger.debug("IrcBackend: new message on " + str(event.target) + " -> " + event.arguments[0])

        msg = Message(backend=self.name, 
            channel=event.target,
            nickname=event.source.split("!")[0],
            text=event.arguments[0])
        self.outgoing.put(msg)

    def join(self, channel):
        self.channels.append(channel)

    def send_msg(self, channel, message):
        self.server.privmsg(channel, unicode(message))
