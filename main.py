from msgcenter.irc_backend import IrcBackend
from msgcenter.message import MessageSink
from msgcenter.center import Center
import json

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
