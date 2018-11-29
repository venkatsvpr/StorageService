#!/usr/bin/env python3

import socket
import struct
import time
from os import system

HOST = '127.0.0.1'
PORT = 8001
FILE = "/Users/nox/Desktop/received.ply"  # change it to whatever you want


def main():
    while True:
        try:
            ctype = int(input('Connection type: '))
            if ctype not in [1, 2]:
                raise TypeError
        except (TypeError, ValueError):
            print('Bye.')
            break

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            if ctype == 1:
                iname = int(input('image file name: '))
                with open('../mapImages/rgb/%d.jpg' % iname, 'rb') as f:
                    data = f.read()
                size = len(data)
                st = time.time()
                s.sendall(struct.pack('!i i', ctype, size))
                s.sendall(data)
                a = s.recv(28)
                num = struct.unpack('!i d d d', a)
                print(num)
            else:
                system('displaz &')
                x, y, z, r = list(map(float, input('x, y, z, r: ').split()))
                st = time.time()
                s.sendall(struct.pack('!i d d d d', ctype, x, y, z, r))
                data = s.recv(8)
                t, size = struct.unpack('!i i', data)
                data = b''
                while size - len(data):
                    packet = s.recv(size)
                    if not packet:
                        break
                    data += packet
                with open(FILE, 'bw') as myfile:
                    myfile.write(data)
                print('Received: {0:,d} bytes'.format(len(data)))
                system('displaz -clear %s' % FILE)

        print('Time taken: %f seconds\n' % (time.time() - st))



if __name__ == '__main__':
    main()
