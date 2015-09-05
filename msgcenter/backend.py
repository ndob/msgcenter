from abc import ABCMeta, abstractmethod

class Backend:
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self, incoming, outgoing):
        pass

    @abstractmethod
    def join(self, channel):
        pass
