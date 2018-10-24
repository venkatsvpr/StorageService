import sys
import socket
from ctypes import *

""" Global Variables """
MyIp = "http://localhost"
MyPort = 11111

ServerIp = "http://localhost"
ServerPort = 33333

class Coordinates(object):
    def __init__ (self, x,y,r):
        self.x = int(x)
        self.y = int(y)
        self.r = int(r)

class Payload():
    _fields_ = [("x", c_uint32), ("y", c_uint32), ("r", c_uint32)]

class Length():
    _fields_ = [("len",c_uint32)]

def sendRequestToServer (ip, port, listOfCoordinates):
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverAddress = (ip, port)
    serverSock.connect(serverAddress)

    numberOfCoordinates = len(listOfCoordinates)
    if (numberOfCoordinates <= 0):
        return None

    payload_out = Length(numberOfCoordinates)
    nsent = 0
    nsent += serverSock.send(payload_out)
    for coord in listOfCoordinates:
        payload_out = Payload(coord.x, coord.y, coord.r)
        nsent += serverSock.send(payload_out)

    buffer = serverSock.recv(sizeof(Length))
    lengthToRead = Length.from_buffer_copy(buffer)
    toRead = lengthToRead.len

    outFile = open("/tmp/Test.ply", "wb")
    while (True):
        data = None
        if (toRead < 1024):
            data = serverSock.recv(toRead)
        else:
            data = serverSock.recv(1024)
        if (data == None):
            break
        outFile.write(data)
    outFile.close()

    return True

def validateInput (x,y,r):
    return True

def main ():
    """ Temporarily Cache the path corresponding to (x,y,r), Objective is to cache the file in client side """
    Cache = dict()
    while (True):
        (x,y,r) = input(" Enter x,y,r in the same order and format.")
        if (validateInput(x,y,r)):
            if ((x,y,r)  not in Cache):
                Cache[(x,y,r)] = sendRequestToServer(ServerIp, ServerPort, [[x,y,r]])
            pathToPointCloudFile  = Cache[(x,y,r)]
            print (" will be triggering on ",pathToPointCloudFile)
main()
