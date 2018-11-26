from globals import

def localizationRequest (sock, size, path):
    sendTypeOneRequest(sock, size, path)
    return

def getLocalizationResponse (sock):
    type = readIntegerFromNetwork(sock)
    x = readDoubleFromNetwork(sock)
    y = readDoubleFromNetwork(sock)
    z = readDoubleFromNetwork(sock)
    return x,y,z

def sendTypeOneRequest (sock, size, path):
    type = 1
    sock.sendall (struct.pack('!d d',type,size))
    sendFileOnSock(sock,path)
    return

def getPlyRequest (sock, x, y, z, r):
    sendTypeTwoRequest(sock, x, y, z, r)
    return

def sendTypeTwoRequest (sock, x, y, z, radius):
    type = 2
    sock.sendall (struct.pack('!d d d d',type, x, y, z, radius))
    return

def getPlyResponse (sock):
    type = readIntegerFromNetwork(sock)
    toReadSize = readIntegerFromNetwork(sock)
    binaryData = b''
    while (toReadSize):
        packet = sock.recv(toReadSize)
        if not packet:
            break
        toReadSize -= len(packet)
        binaryData += packet
    return binaryData


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
        serverAddress = (ServerIp, ServerPort)
        serverSock.connect(serverAddress)

        numberOfCoordinates = len(listOfCoordinates)
        if (numberOfCoordinates <= 0):
            return None

        #serverSock.sendall(struct.pack('!i', numberOfCoordinates))

        for item in listOfCoordinates:
            x = item[0]
            y = item[1]
            r = item[2]
            print (" going to request ",x,y,r)
            outFilePath = "/tmp/client/"+str(x)+"_"+str(y)+"_"+str(r)+".ply"

            plyRequestToServer(serverSock, x, y, z, r)
            binaryData = getPlyResponse(serverSock)
            writeBinaryDataToFile(binaryData, outFilePath)
        serverSock.close()
        return outFilePath
    except:
        return None

def validateInput (x,y,z,r):
    """
    :param x:  X co-ordinate
    :param y:  Y co-ordinate
    :param r:  R radius
    :return: True/False Value

    We have to validate the x,y,radius and return True/False value
    """
    return True


def startorUpdateDisplay(pathToPlyFile):
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

def asyncGet(x, y, z, r, cache, cacheLock):
    #sock.sendall(struct.pack('!i', numberOfCoordinates))
    logClient (" Opportunistic fetching x,y,r "+str(x)+","+str(y)+","+str(r))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverAddress = (ServerIp, ServerPort)
    sock.connect(serverAddress)

    outFilePath = "/tmp/client/" + str(x) + "_" + str(y) + "_" + str(r) + ".ply"

    plyRequestToServer (sock, x, y, z, r)
    binaryData = getPlyResponse(sock)

    writeBinaryDataToFile(binaryData, outFilePath)
    sock.close()

    cacheLock.acquire()
    cache[(x,y,r)] = outFilePath
    cacheLock.release()

    startorUpdateDisplay(outFilePath)


def fetchAround (x, y, r, cache, cacheLock):
    #print (" fetchAround  ")
    firstLevel = [(x+r,y), (x-r,y) , (x,y+r), (x,y-r)]
    for (x1,y1) in firstLevel:
        if (canSupressRequest(cache, x1, y1, r)):
            continue;
        asyncGet(x1, y1, r, cache, cacheLock)

def cachingService (cache, cacheLock, queue):
    #print (" cachingService ")
    currThread = threading.currentThread()
    while True:
        if (getattr(currThread, "exit", False)):
            break;
        try:
            print ("Waiting for activity on pointQueue")
            (x,y,r) = queue.get(timeout= 2)
        except:
            continue;
        if (r == -1):
            break;
        fetchAround(x,y,r,cache,cacheLock)

def canSupressRequest (Cache, x, y, r):
    pq = Queue.PriorityQueue()
    # Find the closest point
    for (x1,y1,r1) in Cache:
        dist = math.sqrt((x-x1)**2 + (y-y1)**2)
        pq.put((dist, (x1,y1,r1)))
    if (0 == pq.qsize()):
        return False
    (dist, tup) = pq.get()
    if (dist < (r/3)):
        return True
    return False

def syncGet (sock, x, y, z, cache, cacheLock):
    global radius
    if (False == validateInput(x,y,z)):
        return;
    if (True == canSupressRequest(Cache, x, y, z, radius)):
        return;

    outFilePath = "/tmp/client/" + str(x) + "_" + str(y) + "_" + str(r) + ".ply"

    plyRequestToServer(sock, x, y, z, r)
    binaryData = getPlyResponse(sock)

    writeBinaryDataToFile(binaryData, outFilePath)

    cacheLock.acquire()
    cache[(x,y,r)] = outFilePath
    cacheLock.release()
    startorUpdateDisplay(outFilePath)
    return

def processimageQueue (cache, cacheLock, imgQueue, pointQueue):
    try:
        serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress = (ServerIp, ServerPort)
        serverSock.connect(serverAddress)

        currThread = threading.currentThread()
        while True:
            if (getattr(currThread, "exit", False)):
                break;
            print (" Waiting for activity on imageQueue ")
            try:
                path = imgQueue.get(timeout= 3)
            except:
                continue;

            fileSize = getSize(path)
            if (fileSize <= 0):
                continue;

            localizationRequest( sock, fileSize, path)
            (x,y,z) = getLocalizationResponse(sock)

            syncGet(sock, x, y, z, cache, cacheLock)

            pointQueue.put((float(x),float(y),float(z)))
        serverSock.close()
    except:
        print (" Cannot connect to server ")

def main (Cache, CacheLock, imgQueue, pointQueue):
    global CurrentSession
    if (True):
        try:
            (x,y,z,r) = input(" Enter x,y,z,r :>> ")
        except:
            print (" Exiting! ")
            killDisplaySession(CurrentSession)
            break;
        pointQueue.put((x,y,z))
        # connect to server
        serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress = (ServerIp, ServerPort)
        serverSock.connect(serverAddress)
        # Get the ply file syncronously
        syncGet(serverSock, x,y,z, Cache, CacheLock)
        serverSock.close()
    return;

Cache = dict()
CacheLock = threading.Lock()
imageQueue = Queue.Queue()
pointQueue = Queue.Queue()

# Start the caching thread
cacheThread = threading.Thread(target=cachingService,args=(Cache, CacheLock, pointQueue))
cacheThread.start()

# Localization Thread
imgProcessThread = threading.Thread(target=processimageQueue,args=(Cache, CacheLock, imageQueue, pointQueue))
cacheThread.start()

# Start the Main Thread
main(Cache, CacheLock,imageQueue, messageQueue)

cacheThread.exit = True
cacheThread.join()

imgProcessThread.exit = True
imgProcessThread.join()

