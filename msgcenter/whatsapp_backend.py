from .backend import Backend
from .message import Message
from .logger import logger
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
import sys

def to_raw_unicode(string):
    # Ensures compatibility between Python 2.x and 3.x
    return string.encode("raw_unicode_escape") if sys.version_info >= (3,0) else string

def message_to_text(entity):
    ret = ""
    if entity.getType() == "text":
        ret = to_raw_unicode(entity.getBody())
    elif entity.getType() == "media":
        if entity.getMediaType() == "image":
            ret = "*IMAGE* " + entity.getMediaUrl()
        elif entity.getMediaType() == "video":
            ret = "*VIDEO* " + entity.getMediaUrl()
        elif entity.getMediaType() == "audio":
            ret = "*AUDIO* " + entity.getMediaUrl()
        elif entity.getMediaType() == "location":
            ret = "*LOCATION* http://www.google.com/maps/place/" + entity.getLatitude() + "," + entity.getLongitude()
        elif entity.getMediaType() == "vcard":
            ret = "*VCARD* " + entity.getName()
        else:
            ret = "*UNKNOWN MEDIA*"
            logger.warning("WhatsAppBackend: formatting for %s not implemented. Entity: %s" % (entity.getType(), entity))
    else:
        ret = "*UNKNOWN MESSAGE*"
        logger.warning("WhatsAppBackend: formatting for %s not implemented. Entity: %s" % (entity.getType(), entity))

    if hasattr(entity, "getCaption") and callable(getattr(entity, "getCaption")):
        ret += " "
        ret += to_raw_unicode(entity.getCaption()).decode("utf-8")

    return ret

class MsgCenterLayer(YowInterfaceLayer):
    PROP_OUTGOING = "com.github.ndob.msgcenter.whatsappbackend.incoming"
    PROP_BACKEND_NAME = "com.github.ndob.msgcenter.whatsappbackend.backend_name"
    EVENT_NEW_MSG = "com.github.ndob.msgcenter.whatsappbackend.new_message"

    def onEvent(self, event):
        if event.getName() == self.__class__.EVENT_NEW_MSG:
            self._incoming_msg(event.getArg("to"), event.getArg("text"))
            return True

    @ProtocolEntityCallback("message")
    def on_message(self, entity):
        msg = Message(backend = self.getProp(self.__class__.PROP_BACKEND_NAME),
            channel = entity.getFrom(),
            nickname = entity.getNotify(),
            text = message_to_text(entity))
        self.getProp(self.__class__.PROP_OUTGOING).put(msg)

        # Acks, that message has "arrived"
        self.toLower(entity.ack())
        # Acks, that message has been "read"
        self.toLower(entity.ack(True))

    @ProtocolEntityCallback("receipt")
    def on_receipt(self, entity):
        self.toLower(entity.ack())

    def _incoming_msg(self, channel, message):
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
        self.stack.setProp(MsgCenterLayer.PROP_BACKEND_NAME, self.name)
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
