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
        self.reactor.add_global_handler("unavailresource", self.on_resource_unavailable)

        while 1:
            if self.incoming.poll():
                info = self.incoming.recv()
                self._incoming_msg(info["to"], info["msg"].pretty_print())
            
            self.reactor.process_once()
            time.sleep(0.2)

    def join(self, channel):
        self.channels.append(channel)

    def _connect(self):
        logger.debug("IrcBackend: connecting to " + self.name)
        try:
            self.server = self.reactor.server()
            self.server.connect(self.server_address, self.port, self.nickname)
        except irc.client.ServerConnectionError:
            logger.error("IrcBackend: error connecting to " + self.name)
            time.sleep(5)
            self._connect()

    def _join_channel(self, connection, channel):
        if irc.client.is_channel(channel):
            logger.debug("IrcBackend: joining to " + channel + "@" + self.name)
            connection.join(channel)

    def on_connect(self, connection, event):
        logger.debug("IrcBackend: connected to " + self.name)
        for channel in self.channels:
            self._join_channel(connection, channel)

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
        self._outgoing_msg(msg)

    def on_resource_unavailable(self, connection, event):
        logger.debug("IrcBackend: resource unavailable")
        if len(event.arguments) > 0 and irc.client.is_channel(event.arguments[0]):
            self._join_channel(connection, event.arguments[0])

    def _outgoing_msg(self, msg):
        self.outgoing.put(msg)

    def _incoming_msg(self, channel, message):
        self.server.privmsg(channel, unicode(message))
