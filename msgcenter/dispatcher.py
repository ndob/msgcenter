from .logger import logger
from multiprocessing import Process, Queue, Pipe
import time
import six

class Dispatcher(object):
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
            if sink.backend in self.backends:
                logger.debug("Dispatcher: adding sink " + sink.channel + "@" + sink.backend)
                b = self.backends[sink.backend]
                b.join(sink.channel)
            else:
                logger.error("no backend with name: " + sink.backend)

    def start(self):
        for name, b in six.iteritems(self.backends):
            recv_conn, send_conn = Pipe(False)
            self.pipes[name] = send_conn
            p = Process(target=b.start, args=(recv_conn, self.incoming,))
            p.start()

        self._consume()

    def _get_groups_for(self, channel):
        logger.debug("searching groups for:" + channel)

        ret = dict()
        for name, sinks in six.iteritems(self.groups):
            for sink in sinks:
                if sink.channel == channel:
                    ret[name] = sinks
                    break
        return ret

    def _consume(self):
        while 1:
            # get() blocks, if there are no messages
            msg = self.incoming.get()
            logger.debug("new message arrived from " + msg.channel)

            groups = self._get_groups_for(msg.channel)
            for name, sinks in six.iteritems(groups):
                for sink in sinks:
                    if msg.backend == sink.backend and msg.channel == sink.channel:
                        continue

                    logger.debug("sending to:" + sink.channel)
                    self.pipes[sink.backend].send({"to": sink.channel, "msg": msg})

            # prevent flooding
            time.sleep(0.1)