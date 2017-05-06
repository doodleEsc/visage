#!/usr/bin/python

from visage.agent.virtio import ChannelAgent
from visage.dispatch.dispatcher import Dispatcher

def main():
    chardev = "/dev/virtio-ports/org.qemu.guest_agent.1"
    handler = open(chardev, "r+")
    #backends = ['visage.backend.test.Test']

    backends = {
        "Test": "visage.backend.test.Test"
    }

    dispatcher = Dispatcher(**backends)
    ga = ChannelAgent(handler, chardev, dispatcher)
    ga.run()

if __name__ == '__main__':
    main()
