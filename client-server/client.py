from globals import *

def sendRequestToServer (ip, port, listOfCoordinates):
    """
    :param ip:  ServerIpAddress
    :param port:  ServerPort Number
    :param listOfCoordinates:  List of Co-ordinates
    :return: path to the ply file on Client

    Server Request:
    ==============
    [Number of Co-ordinates][Co-ordinate 1][Co-ordinate 2]....[Co-ordinate N]]
    [Co-ordinate] = [x,y,z]

    Logic Flow:
    ===========
    Send a Number of Co-ordinates, Followed by the co-ordinates..
    Expect a File size from Server and then create a file on client and get the contents from Server stream.
    Once done, return the file.
    """
    try:
        serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress = (ip, port)
        serverSock.connect(serverAddress)


        numberOfCoordinates = len(listOfCoordinates)
        if (numberOfCoordinates <= 0):
            return None

        payload_out = Length(numberOfCoordinates)
        nsent = 0
        nsent += serverSock.send(payload_out)

        outFile = ""
        for item in listOfCoordinates:
            outFile = str(item[0])+"_"+str(item[1])+"_"+str(item[2])+".ply"
            payload_out = Payload(item[0], item[1], item[2])
            nsent += serverSock.send(payload_out)

        buffer = serverSock.recv(sizeof(Length))
        lengthToRead = Length.from_buffer_copy(buffer)
        toRead = lengthToRead.len

        # the file path should be in some format
        # TODO
        outFilePath = "/tmp/client"+outFile
        outFd = open(outFilePath, "wb")
        data = None
        while (True):
            data = None
            if (toRead < 1024):
                data = serverSock.recv(toRead)
            else:
                data = serverSock.recv(1024)
            if (data == None) or (len(data) == 0):
                break
            outFd.write(data)
        outFd.close()
        return outFilePath
    except:
        return None

def validateInput (x,y,r):
    """
    :param x:  X co-ordinate
    :param y:  Y co-ordinate
    :param r:  R radius
    :return: True/False Value

    We have to validate the x,y,radius and return True/False value
    """
    return True


def startorUpdateDisplay(x,y,r,pathToPlyFile):
    """
    :param x:
    :param y:
    :param r:
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

def killDisplaySession (sessionNumber):
    args = ["displaz", "-label", str(sessionNumber),"-quit"]
    p = subprocess.Popen(args)
    return

def logClient (msg):
    return log("ClientLog", ClientLogFile, msg)

def main ():
    """ Temporarily Cache the path corresponding to (x,y,r), Objective is to cache the file in client side """
    """ 
    TODO
    1)  This could be really a robust cache.. Like if we have cached 1,1 to  5,5 and we get a request for
        2,2 to 4,4 we could pull 1,1 to 5,5 in constant time rather than fetching 
    2)  (1) is at the cost of more memory on client.. we could offload this work to server
    """
    global CurrentSession
    Cache = dict()
    while (True):
        try:
            (x,y,r) = input(" Enter x,y,r :>> ")
        except:
            print (" Exiting! ")
            killDisplaySession(CurrentSession)
            break;

        logClient(" Send request! pt: x="+str(x)+" y="+str(y)+" radius="+str(r))
        if (validateInput(x,y,r)):
            if ((x,y,r)  not in Cache):
                result = sendRequestToServer(ServerIp, ServerPort, [[x,y,r]])
                if (result):
                    logClient(" Obtained reply! pt: x=" + str(x) + " y=" + str(y) + " radius=" + str(r))
                    Cache[(x,y,r)] = result
                else:
                    logClient(" Connection Failed! pt: x=" + str(x) + " y=" + str(y) + " radius=" + str(r))
                    continue;
            else:
                logClient(" Fetch from Local Cache! pt: x="+str(x)+" y="+str(y)+" radius="+str(r))
            pathToPointCloudFile  = Cache[(x,y,r)]
            startorUpdateDisplay (x,y,r,pathToPointCloudFile)
main()
