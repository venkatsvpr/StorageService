from globals import all

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
    logClient ("  Sending request type,size : "+str(type)+" "+str(size))
    sock.sendall (struct.pack('!i i',type,size))
    sendFileOnSock(sock,path)
    return

def getPlyRequest (sock, x, y, z, r):
    sendTypeTwoRequest(sock, x, y, z, r)
    return

def sendTypeTwoRequest (sock, x, y, z, radius):
    type = 2
    logClient(" Sending request type,x,y,z,radius : "+str(type)+","+str(x)+","+str(y)+","+str(z)+","+str(radius))
    sock.sendall (struct.pack('!i d d d d',type, x, y, z, radius))
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

def asyncGet(x, y, z, r, cache, cacheLock):
    try:
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
    except:
        print (" Cannot connect to server ")
    return

def fetchAround (x, y, r, cache, cacheLock):
    firstLevel = [(x+r,y), (x-r,y) , (x,y+r), (x,y-r)]
    for (x1,y1) in firstLevel:
        if (canSupressRequest(cache, x1, y1, r)):
            continue;
        asyncGet(x1, y1, r, cache, cacheLock)
    return

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
    if (True == canSupressRequest(Cache, x, y, z, radius)):
        return;

    outFilePath = "/tmp/client/" + str(x) + "_" + str(y) + "_" + str(r) + ".ply"

    plyRequestToServer(sock, x, y, z, radius)
    binaryData = PlyResponse(sock)

    writeBinaryDataToFile(binaryData, outFilePath)

    cacheLock.acquire()
    cache[(x,y,r)] = outFilePath
    cacheLock.release()
    startorUpdateDisplay(outFilePath)
    return

def imgProcessingService (cache, cacheLock, imgQueue, pointQueue):
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
    return

def cachingService (cache, cacheLock, queue):
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
    return

def main (Cache, CacheLock, imgQueue, pointQueue):
    global CurrentSession
    if (True):
        try:
            (x,y,z,r) = input(" Enter x,y,z,r :>> ")
        except:
            print (" Exiting! ")
            killDisplaySession(CurrentSession)
            break
        pointQueue.put((x,y,z))

        serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress = (ServerIp, ServerPort)
        serverSock.connect(serverAddress)

        syncGet(serverSock, x,y,z, Cache, CacheLock)
        serverSock.close()
    return;

Cache = dict()
CacheLock = threading.Lock()
imageQueue = Queue.Queue()
pointQueue = Queue.Queue()


# Start the caching thread
cacheThread = threading.Thread(target=cachingService, args=(Cache, CacheLock, pointQueue))
cacheThread.start()

# Localization Thread
imgProcessThread = threading.Thread(target=imgProcessingService, args=(Cache, CacheLock, imageQueue, pointQueue))
cacheThread.start()

# Start the Main Thread
main(Cache, CacheLock,imageQueue, messageQueue)

cacheThread.exit = True
cacheThread.join()

imgProcessThread.exit = True
imgProcessThread.join()

