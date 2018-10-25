from ctypes import *
import os
import sys
import socket
from ctypes import *
from datetime import datetime
from ast import literal_eval as make_tuple

""" Global Variables """
MyIp = "127.0.0.1"
MyPort = 11111

ServerIp = "127.0.0.1"
ServerPort = 33334

""" Log File """
ClientLogFile = "/tmp/ClientLog.log"
ServerLogFile = "/tmp/ServerLog.log"

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
    print("["+header+"] ["+getCurrTime()+"]"+msg+"\n")
    logFile.write("["+header+"] ["+getCurrTime()+"]"+msg+"\n")
    logFile.close()
    return
