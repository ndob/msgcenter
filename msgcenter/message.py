class Message(object):
    def __init__(self, backend, channel, nickname, text):
        self.backend = backend
        self.channel = channel
        self.nickname = nickname
        if type(text) != unicode:
            self.text = text.decode("utf-8")
        else:
            self.text = text

    def __str__(self):
        """Ascii string-representation.

        Returns:
            Message as ascii string.
        """
        return "".join([
            "[",
            self.nickname,
            "@",
            self.channel,
            "-",
            self.backend,
            "] ",
            self.text.encode("ascii", "replace")
        ])

    def pretty_str(self):
        """Prettified unicode string-representation.

        Returns:
            Message as prettified unicode string.
        """
        return unicode("[" + self.nickname + "] ") + self.text

class MessageSink(object):
    def __init__(self, backend, channel):
        self.backend = backend
        self.channel = channel
