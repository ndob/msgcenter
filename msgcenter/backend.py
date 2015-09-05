from abc import ABCMeta, abstractmethod

class Backend:
    """Interface for messaging backends.

    All backends should implement this interface.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def start(self, incoming, outgoing):
        """Starts the backend operations.

        Args:
            incoming: A pipe (type: multiprocessing.Connection), which provides 
                incoming messages from other backends to a certain channel on
                this backend. Incoming messages are provided as a dict 
                with fields:
                    to: target channel id (type: string)
                    msg: message data (type: Message)
            outgoing: A queue (type: multiprocessing.Queue) to which all 
                outgoing messages (type: Message) should be pushed.
        """
        pass

    @abstractmethod
    def join(self, channel):
        """Joins a channel provided by the backend.

        Args:
            channel: Backend dependent channel id to join.
        """
        pass
