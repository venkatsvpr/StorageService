from globals import *

def writeToCSVFile (file, content):
    global csvLock
    csvLock.acquire()
    print (" acuired the lock")
    file.write(getCurrTime()+","+str(content)+"\n")
    print (" wrote releaseing the lock")
    csvLock.release()
    print (" returning")
    return

def localizationRequest (sock, size, path):
    sendTypeOneRequest(sock, size, path)
    return

def getLocalizationResponse (sock):
    a = sock.recv(28)
    type,x,y,z = struct.unpack('!i d d d', a)
    #type = readIntegerFromNetwork(sock)
    #x = readDoubleFromNetwork(sock)
    #y = readDoubleFromNetwork(sock)
    #z = readDoubleFromNetwork(sock)
    print (" local response ",type,x,y,z)
    return x,y,z

def sendTypeOneRequest (sock, size, path):
    type = LocalizationMessageType
    logClient ("  Sending request type,size : "+str(type)+" "+str(size))
    print("  Sending request type,size : "+str(type)+" "+str(size))
    sock.sendall (struct.pack('!i i',type,size))
    sendFileOnSock (sock,path)
    return

def getPlyRequest (sock, x, y, z, r):
    sendTypeTwoRequest (sock, x, y, z, r)
    return

def sendTypeTwoRequest (sock, x, y, z, radius):
    type = CachingMessageType
    logClient (" Sending request type,x,y,z,radius : "+str(type)+","+str(x)+","+str(y)+","+str(z)+","+str(radius))
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

def asyncGet(x, y, z, cache, cacheLock):
    global radius
    if True:
        logClient (" Opportunistic fetching x,y,z,r "+str(x)+","+str(y)+","+str(z)+","+str(radius))
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress = (ServerIp, ServerPort)
        sock.connect(serverAddress)

        outFilePath = getCacheFilePath (x,y,z,radius)

        getPlyRequest (sock, x, y, z, radius)
        binaryData = getPlyResponse(sock)
        sock.close()
        writeBinaryDataToFile(binaryData, outFilePath)
        startorUpdateDisplay(outFilePath)

        cacheLock.acquire()
        cache[(x,y,z,radius)] = outFilePath
        cacheLock.release()
    """
    except:
        print (" Cannot connect to server ")
    """
    return

def fetchAround (x, y, z, cache, cacheLock):
    global asyncFile
    global radius
    firstLevel = [(x+radius,y,z), (x-radius,y,z) , (x,y+radius,z), (x,y-radius,z)]
    startTime = time.time()
    Threads = []
    for (x1,y1,z1) in firstLevel:
        if (canSupressRequest(cache, x1, y1, z1)):
            continue;
        asyncThread = threading.Thread(target=asyncGet,args=(x1,y1,z1,cache, cacheLock))
        Threads.append(asyncThread)
        asyncThread.start()
    endTime = time.time()
    writeToCSVFile(asyncFile, endTime - startTime)
    return

def canSupressRequest (Cache, x, y, z):
    global radius
    pq = Queue.PriorityQueue()
    # Find the closest point
    for (x1,y1,z1,radius) in Cache:
        dist = math.sqrt((x-x1)**2 + (y-y1)**2 + (z-z1)**2)
        pq.put((dist, (x1,y1,z1)))
    if (0 == pq.qsize()):
        return False
    (dist, tup) = pq.get()
    if (dist < (radius/3)):
        return True
    return False

def syncGet (x, y, z, cache, cacheLock):
    global radius
    if (True == canSupressRequest(Cache, x, y, z)):
        return;
    outFilePath = getCacheFilePath(x, y, z, radius)
    startTime = time.time()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverAddress = (ServerIp, ServerPort)
    sock.connect(serverAddress)
    #ply request
    getPlyRequest(sock, x, y, z, radius)
    binaryData = getPlyResponse(sock)
    sock.close()

    endTime = time.time()
    writeToCSVFile(syncFile, endTime - startTime)

    writeBinaryDataToFile(binaryData, outFilePath)
    startorUpdateDisplay(outFilePath)

    cacheLock.acquire()
    cache[(x,y,z,radius)] = outFilePath
    cacheLock.release()
    return

def imgProcessingService (cache, cacheLock, imgQueue, pointQueue):
    global localFile, syncFile
    while True:
        currThread = threading.currentThread()

        if (getattr(currThread, "exit", False)):
            return
        try:
            print ("Waiting for activity on imgQueue")
            path = imgQueue.get(timeout=2)
        except:
            continue;
        print (" got path "+path)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress = (ServerIp, ServerPort)
        sock.connect(serverAddress)

        fileSize = getSize(path)
        if (fileSize <= 0):
            continue;
        startTime = time.time()
        localizationRequest(sock, fileSize, path)
        (x,y,z) = getLocalizationResponse(sock)
        print (" going to close")
        sock.close()
        print (" closed the socket")
        endTime = time.time()
        print (" time "+str(endTime))
        writeToCSVFile (localFile, endTime-startTime)
        pointQueue.put((float(x),float(y),float(z)))
        print (" added to pointqueue")

    return

def cachingService (cache, cacheLock, queue):
    currThread = threading.currentThread()
    while True:
        if (getattr(currThread, "exit", False)):
            break
        try:
            print ("Waiting for activity on pointQueue")
            (x,y,z) = queue.get(timeout= 2)
        except:
            continue;
        syncGet(x, y, z, cache, cacheLock)
        fetchAround(x, y, z, cache, cacheLock)
    return

def main (Cache, CacheLock, imgQueue, pointQueue):
    global CurrentSession
    if (True):
        try:
            (x,y,z,r) = input(" Enter x,y,z,r :>> ")
        except:
            killDisplaySession(CurrentSession)
            return;
        pointQueue.put((x,y,z))

        serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serverAddress = (ServerIp, ServerPort)
        serverSock.connect(serverAddress)

        syncGet(serverSock, x,y,z, Cache, CacheLock)
        serverSock.close()
    return;



def guiService (cache,imgQueue):
    currThread = threading.currentThread()

    class S(BaseHTTPRequestHandler):
        def _set_headers(self):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

        def do_GET(self):
            print self.path
            query_dict =  parse_qs(self.path[2:])
            file_path = query_dict.get("url")[0]
            print file_path
            imgQueue.put(file_path)
            self._set_headers()
            self.wfile.write("<html><body><h1>File location has been sent</h1></body></html>")

        def do_HEAD(self):
            self._set_headers()

        def do_POST(self):
            # Doesn't do anything with posted data
            self._set_headers()
            self.wfile.write("<html><body><h1>Post</h1></body></html>")

    server_address = ('', 8099)
    server_class=HTTPServer
    handler_class=S
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd...'
    httpd.serve_forever()
    return

# Initializing Cache and CacheLock
global LocalizationCsv, SyncFetchCsv, AsyncFetchCsv, localFile, syncFile, asyncFile
localFile = open(LocalizationCsv, "w+")
syncFile = open(SyncFetchCsv, "w+")
asyncFile = open(AsyncFetchCsv, "w+")

Cache = dict()
CacheLock = threading.Lock()

global csvLock
csvLock = threading.Lock()

# Initialize Queues
imageQueue = Queue.Queue()
pointQueue = Queue.Queue()

# Initializing guiService
guiThread = threading.Thread(target=guiService, args=(Cache,imageQueue))
# Initializing cachingService
cacheThread = threading.Thread(target=cachingService, args=(Cache, CacheLock, pointQueue))
# Initializing Image-processing Service
imgProcessThread = threading.Thread(target=imgProcessingService, args=(Cache, CacheLock, imageQueue, pointQueue))

guiThread.start()
cacheThread.start()
imgProcessThread.start()

# Start the Main Thread
main(Cache, CacheLock,imageQueue, pointQueue)

# Setting exit so that the threads may exit
guiThread.exit = True
imgProcessThread.exit = True
cacheThread.exit = True
cacheThread.join()
imgProcessThread.join()
guiThread.join()

localFile.close()
syncFile.close()
asyncFile.close()

