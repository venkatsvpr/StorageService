from ctypes import *
import os
import sys
import socket
import time
import struct
from ctypes import *
from datetime import datetime
from ast import literal_eval as make_tuple
import shlex, subprocess
import threading
import Queue as Queue
import math
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
from urlparse import parse_qs



""" Global Variables """
MyIp = "127.0.0.1"
MyPort = 11111

ServerIp ="127.0.0.1"
ServerPort = 8001

CurrentSession = 1
""" Log File """
ClientLogFile = "/tmp/ClientLog.log"
ServerLogFile = "/tmp/ServerLog.log"

plyViewerStarted = False
""" Some Structures for Inter Process Communication """
class Payload(Structure):
    _fields_ = [("x", c_uint32), ("y", c_uint32), ("r", c_uint32)]

class Length(Structure):
    _fields_ = [("len",c_uint32)]

class Coordinates(object):
    def __init__ (self, x,y,r):
        self.x = int(x)
        self.y = int(y)
        self.r = int(r)

class Length(Structure):
    _fields_ = [("len",c_uint32)]

def getCurrTime():
    return str(datetime.now())

def log (header, logFile, msg):
    logFile = open(logFile,"a")
    print("["+header+"] ["+getCurrTime()+"]"+msg)
    logFile.write("["+header+"] ["+getCurrTime()+"]"+msg+"\n")
    logFile.close()
    return

def readIntegerFromNetwork (connection):
    readData = None
    readData = connection.recv(4)
    if (len(readData) == 0):
        return 0
    toRead = struct.unpack('!i', readData)[0]
    return toRead

def readCoOrdinatesFromNetwork (connection):
    readData = None
    readData = connection.recv(12)
    if (len(readData) == 0):
        return None
    x = struct.unpack('!d d d', readData)[0]
    y = struct.unpack('!d d d', readData)[1]
    r = struct.unpack('!d d d', readData)[2]
    coord = Coordinates(x,y,r)
    return coord

def getSize(filename):
    st = os.stat(filename)
    return st.st_size


def sendFileOnSock (sock, path):
    print ("Sending file to client")
    file = open(filePath,'rb')
    data = file.read(1024)
    while (data):
       sock.send(data)
       data = file.read(1024)
    print ("sent")
    file.close()
    return

def killDisplaySession (sessionNumber):
    args = ["displaz", "-label", str(sessionNumber),"-quit"]
    p = subprocess.Popen(args)
    return

def logClient (msg):
    return log("ClientLog", ClientLogFile, msg)

def writeBinaryDataToFile (binaryData, filePath):
    myfile = open(outFilePath, "wb")
    myfile.write(binaryData)
    myfile.close()
    return


def startorUpdateDisplay (pathToPlyFile):
    """
    :param pathToPlyFile:
    :return:
    We have to handle the case where the x,y,r is already present on the viewer
    we may have to replace it or skip duplicate updates.
    """
    global plyViewerStarted
    global CurrentSession

    if (False == plyViewerStarted):
        plyViewerStarted = True
        args = ["displaz" , "-label", str(CurrentSession), str(pathToPlyFile)]
    else:
        args = ["displaz" , "-label", str(CurrentSession), "-add", str(pathToPlyFile)]
    p = subprocess.Popen(args)
    return


def getCacheFilePath (x, y, z, radius):
    outFilePath = "/tmp/client/" + str(x) + "_" + str(y) + "_"  + str(z) + "_" + str(radius) + ".ply"
    return outFilePath


def readByteFromSock (sock, toReadSize):
    binaryData = b''
    while (toReadSize):
        packet = sock.recv(toReadSize)
        if not packet:
            break
        toReadSize -= len(packet)
        binaryData += packet
    return binaryData
