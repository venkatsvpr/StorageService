#!/usr/bin/env python3

import socket
import struct
import time
from os import system

HOST = '127.0.0.1'
PORT = 8001
FILE = "/Users/nox/Desktop/received.ply"  # change it to whatever you want


def main():
    system('displaz &')
    while True:
        try:
            x, y, radius = list(map(float, input().split()))
        except (TypeError, ValueError):
            print('Bye.')
            break

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            st = time.time()
            s.connect((HOST, PORT))
            s.sendall(struct.pack('!d d d', x, y, radius))
            data = s.recv(4)
            num = struct.unpack('!i', data)[0]

            data = b''
            while num - len(data):
                packet = s.recv(num)
                if not packet:
                    break
                data += packet

        with open(FILE, 'bw') as myfile:
            myfile.write(data)

        system('displaz -clear %s' % FILE)

        print('Time taken: %f seconds' % (time.time() - st))
        print('Received: {0:,d} bytes\n'.format(len(data)))


if __name__ == '__main__':
    main()
