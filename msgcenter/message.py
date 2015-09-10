import six

def ensure_unicode(text):
    if type(text) == six.binary_type:
        return text.decode("utf-8")
    else:
        return text
    return text


class Message(object):
    def __init__(self, backend, channel, nickname, text):
        self.backend = ensure_unicode(backend)
        self.channel = ensure_unicode(channel)
        self.nickname = ensure_unicode(nickname)
        self.text = ensure_unicode(text)

    def __str__(self):
        """Ascii string-representation.

        Returns:
            Message as ascii string.
        """
        return ("".join([
            "[",
            self.nickname,
            "@",
            self.channel,
            "-",
            self.backend,
            "] ",
            self.text
        ])).encode("ascii", "replace")

    def pretty_str(self):
        """Prettified unicode string-representation.

        Returns:
            Message as prettified unicode string.
        """
        return six.text_type("[" + self.nickname + "] " + self.text)

class MessageSink(object):
    def __init__(self, backend, channel):
        self.backend = backend
        self.channel = channel
