#!/usr/bin/python

from visage.agent.channel import ChannelAgent
from visage.dispatch.dispatcher import Dispatcher

def main():

    chardev = "/dev/virtio-ports/org.qemu.guest_agent.1"

    handler = open(chardev, "r+")
    backends = ['visage.backend.test.Test']

    dispatcher = Dispatcher(*backends)
    ga = ChannelAgent(dispatcher, handler, chardev)

    ga.enter_main_loop()

if __name__ == '__main__':
    main()