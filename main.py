from msgcenter.irc_backend import IrcBackend
from msgcenter.whatsapp_backend import WhatsAppBackend
from msgcenter.message import MessageSink
from msgcenter.dispatcher import Dispatcher
import json
import sys

DEFAULT_CONFIG_FILENAME = "config.json"

def apply_config(filename, dispatcher):
    with open(filename) as file:
        config = json.loads(file.read())

        for name, conf in config["backend"].iteritems():
            if conf["type"] == "irc":
                dispatcher.register(name, IrcBackend(name, conf["server"], conf["port"], conf["nick"]))
            elif conf["type"] == "whatsapp":
                dispatcher.register(name, WhatsAppBackend(name, conf["phone"], conf["password"]))

        for name, sink_defs in config["group"].iteritems():
            sinks = []
            for sink in sink_defs:
                new_sink = MessageSink(sink["backend"], sink["channel"])
                sinks.append(new_sink)
            
            dispatcher.add_group(name, sinks) 

def main():
    d = Dispatcher()
    
    if len(sys.argv) == 2:
        config_filename = sys.argv[1]
    else:
        config_filename = DEFAULT_CONFIG_FILENAME

    apply_config(config_filename, d)
    d.start()

if __name__ == "__main__":
    main()
