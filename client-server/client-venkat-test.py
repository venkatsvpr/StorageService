#!/usr/bin/env python3

import socket
import struct
import time
from os import system

HOST = '127.0.0.1'
PORT = 8001
FILE = "/tmp/client/received.ply"  # change it to whatever you want


def main():
    system('displaz -label 1 &')
    if True:
        #try:
        #    x, y, radius = list(map(float, input().split()))
        #except (TypeError, ValueError):
        #    print('Bye.')
        #    break
        with open("./log","w") as outfp:
            with open("./points","r") as fp:
                lines = fp.readlines()
            for line in lines:
                lt = line.split()
                x = float(lt[0])
                y = float(lt[1])
                radius = 5.0
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                myfile = open(FILE, 'wb+')
                myfile.write(data)
                myfile.close()
                s.close()
                
                system('displaz -label 1 -add %s' % FILE)
                print(' %f %f %f ' %(x,y,radius))
                print('Time taken: %f seconds' % (time.time() - st))
                print('Received: {0:,d} bytes\n'.format(len(data)))
                outfp.write(" %f %f %f %f %d \n" %(x,y,radius,time.time()-st,len(data)))
if __name__ == '__main__':
    main()
