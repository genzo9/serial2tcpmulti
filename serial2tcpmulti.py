#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import asyncio
import serial_asyncio
import socket


class Tcp(asyncio.Protocol):
    def __init__(self, outputs):
        self.outputs = outputs

    def connection_made(self, transport):
        self.outputs['tcp'][self] = transport

        s = transport.get_extra_info('socket')
        s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)

    def data_received(self, data):
        if self.outputs['serial']:
            self.outputs['serial'].write(data)

    def connection_lost(self, exc):
        del self.outputs['tcp'][self]


class Serial(asyncio.Protocol):
    def __init__(self, outputs):
        self.outputs = outputs

    def connection_made(self, transport):
        self.outputs['serial'] = transport

    def data_received(self, data):
        for transport in self.outputs['tcp'].values():
            transport.write(data)

    def connection_lost(self, exc):
        self.outputs['serial'] = None


def main():
    parser = argparse.ArgumentParser(description='Serial TCP bridge')
    parser.add_argument('-l', dest='listen', action='store_true', help='If this option is used, it will be in server mode, otherwise it will be in client mode.')
    parser.add_argument('-a', dest='address', metavar='ADDRESS', type=str, required=True, help='In client mode, specify connection destination address. In server mode, specify listen address.')
    parser.add_argument('-p', dest='port', metavar='PORT', type=int, required=True, help='In client mode, specify connection destination port number. In server mode, specify listen port number.')
    parser.add_argument('-d', dest='device', metavar='DEVICE', type=str, required=True, help='serial dvice. e.g. /dev/ttyS0')
    parser.add_argument('-b', dest='baudrate', metavar='BAUDRATE', type=int, required=True, help='baudrate')
    args = parser.parse_args()

    outputs = {'tcp': {}, 'serial': None}

    loop = asyncio.get_event_loop()

    coro_serial = serial_asyncio.create_serial_connection(loop, lambda: Serial(outputs), args.device, baudrate=args.baudrate)
    loop.create_task(coro_serial)

    if args.listen:
        coro_server = loop.create_server(lambda: Tcp(outputs), args.address, args.port)
        loop.create_task(coro_server)
    else:
        coro_client = loop.create_connection(lambda: Tcp(outputs), args.address, args.port)
        loop.create_task(coro_client)

    loop.run_forever()
    loop.close()


if __name__ == '__main__':
    main()
