from irc_backend import IrcBackend
from message import MessageSink
from logger import logger
from multiprocessing import Process, Queue, Pipe
import json
import time

class Center(object):
    def __init__(self):
        self.backends = dict()
        self.groups = dict()
        self.pipes = dict()
        self.incoming = Queue()

    def register(self, name, backend):
        self.backends[name] = backend

    def add_group(self, name, sinks):
        self.groups[name] = sinks
        for sink in sinks:
            self.join(sink.backend, sink.channel)

    def join(self, backend_name, channel):
        if self.backends.has_key(backend_name):
            b = self.backends[backend_name]
            b.join(channel)

    def start(self):
        for name, b in self.backends.iteritems():
            recv_conn, send_conn = Pipe(False)
            self.pipes[name] = send_conn
            p = Process(target=b.start, args=(recv_conn, self.incoming,))
            p.start()

        self.consume()

    def get_groups_for(self, channel):
        logger.debug("searching groups for:" + channel)

        ret = dict()
        for name, sinks in self.groups.iteritems():
            for sink in sinks:
                if sink.channel == channel:
                    ret[name] = sinks
                    break
        return ret

    def consume(self):
        while 1:
            # get() blocks, if there are no messages
            msg = self.incoming.get()
            logger.debug("new message arrived from " + msg.channel)

            groups = self.get_groups_for(msg.channel)
            for name, sinks in groups.iteritems():
                for sink in sinks:
                    if msg.backend == sink.backend and msg.channel == sink.channel:
                        continue

                    logger.debug("sending to:" + sink.channel)
                    self.pipes[sink.backend].send({"to": sink.channel, "msg": msg})

def parse_config(center):
    with open("config.json") as file:
        config = json.loads(file.read())

        for name, conf in config["backend"].iteritems():
            if conf["type"] == "irc":
                center.register(name, IrcBackend(name, conf["server"], conf["port"], conf["nick"]))
            #elif conf.type == "whatsapp":
            #    center.register(WhatsAppBackend(conf.phone, conf.password))

        for name, sink_defs in config["group"].iteritems():
            sinks = []
            for sink in sink_defs:
                new_sink = MessageSink(sink["backend"], sink["channel"])
                sinks.append(new_sink)
            
            center.add_group(name, sinks) 

def main():
    center = Center()
    parse_config(center)
    center.start()

if __name__ == "__main__":
    main()
