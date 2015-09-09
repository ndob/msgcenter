from backend import Backend
from message import Message
from logger import logger
from yowsup.common import YowConstants
from yowsup.layers import YowLayerEvent
from yowsup.layers.auth import AuthError
from yowsup.layers.network import YowNetworkLayer
from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.stacks import YowStack
from yowsup.stacks import YowStackBuilder
from threading import Thread
import time

class MsgCenterLayer(YowInterfaceLayer):
    PROP_OUTGOING = "com.github.ndob.msgcenter.whatsappbackend.incoming"
    EVENT_NEW_MSG = "com.github.ndob.msgcenter.whatsappbackend.new_message"

    def onEvent(self, layerEvent):
        if layerEvent.getName() == self.__class__.EVENT_NEW_MSG:
            self.incoming_msg(layerEvent.getArg("to"), layerEvent.getArg("text"))
            return True

    @ProtocolEntityCallback("message")
    def on_message(self, messageProtocolEntity):
        if messageProtocolEntity.getType() == "text":
            self.on_text_message(messageProtocolEntity)
        else:
            logger.warning("WhatsAppBackend: other than text-messages not implemented")

        # Acks, that message has "arrived"
        self.toLower(messageProtocolEntity.ack())
        # Acks, that message has been "read"
        self.toLower(messageProtocolEntity.ack(True))

    @ProtocolEntityCallback("receipt")
    def on_receipt(self, entity):
        self.toLower(entity.ack())

    def on_text_message(self,messageProtocolEntity):
        msg = Message(backend="whatsapp1",
            channel=messageProtocolEntity.getFrom(),
            nickname=messageProtocolEntity.getNotify(),
            text=messageProtocolEntity.getBody())
        self.getProp(self.__class__.PROP_OUTGOING).put(msg)

    def incoming_msg(self, channel, message):
        outgoingMessage = TextMessageProtocolEntity(message, to = channel)
        self.toLower(outgoingMessage)


class WhatsAppBackend(Backend):
    def __init__(self, name, phone, password):
        self.name = name
        self.credentials = (phone, password)
        self.channels = []

    def start(self, incoming, outgoing):
        # TODO: Is encryption possible with groups?
        use_encryption = False
        self.incoming = incoming

        stackBuilder = YowStackBuilder()
        self.stack = stackBuilder \
            .pushDefaultLayers(use_encryption) \
            .push(MsgCenterLayer) \
            .build()

        self.stack.setCredentials(self.credentials)
        self.stack.setProp(MsgCenterLayer.PROP_OUTGOING, outgoing)
        self.stack.broadcastEvent(YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT))

        # TODO:Use multiprocessing. There seems to be a problem with yowsup:
        # https://github.com/tgalal/yowsup/issues/717
        p = Thread(target=self.wait_incoming_msgs)
        p.start()

        try:            
            self.stack.loop()                
        except AuthError as e:
            print("Authentication Error: %s" % e)

    def join(self, channel):
        self.channels.append(channel)

    def wait_incoming_msgs(self):
        while True:
            if self.incoming.poll(0.2):
                info = self.incoming.recv()
                self.stack.emitEvent(
                    YowLayerEvent(
                        MsgCenterLayer.EVENT_NEW_MSG, 
                        to=info["to"], 
                        text=info["msg"].pretty_str().encode("utf-8")
                    )
                )
