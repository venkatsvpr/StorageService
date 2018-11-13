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
            serverSock.sendall(struct.pack('!d d d', x, y, r))

            toReadSize = readIntegerFromNetwork(serverSock)
            binaryData = b''

            while (toReadSize):
                packet = serverSock.recv(toReadSize)
                if not packet:
                    break
                toReadSize -= len(packet)
                binaryData += packet

            myfile = open(outFilePath, "wb")
            myfile.write(binaryData)
            myfile.close()
        serverSock.close()
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

def asyncGet(x, y, r, cache, cacheLock):
    #sock.sendall(struct.pack('!i', numberOfCoordinates))
    logClient (" Opportunistic fetching x,y,r "+str(x)+","+str(y)+","+str(r))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverAddress = (ServerIp, ServerPort)
    sock.connect(serverAddress)

    outFilePath = "/tmp/client/" + str(x) + "_" + str(y) + "_" + str(r) + ".ply"
    sock.sendall(struct.pack('!d d d', x, y, r))

    toReadSize = readIntegerFromNetwork(sock)
    binaryData = b''

    while (toReadSize):
        packet = sock.recv(toReadSize)
        if not packet:
            break
        toReadSize -= len(packet)
        binaryData += packet
    myfile = open(outFilePath, "wb")
    myfile.write(binaryData)
    myfile.close()
    sock.close()


    cacheLock.acquire()
    cache[(x,y,r)] = outFilePath
    cacheLock.release()

    startorUpdateDisplay(x, y, r, outFilePath)


def fetchAround (x, y, r, cache, cacheLock):
    print (" fetchAround  ")
    firstLevel = [(x+r,y), (x-r,y) , (x,y+r), (x,y-r)]
    for (x1,y1) in firstLevel:
        if (canSupressRequest(cache, x1, y1, r)):
            continue;
        asyncGet(x1, y1, r, cache, cacheLock)

def cachingService (cache, cacheLock, queue):
    print (" cachingService ")
    currThread = threading.currentThread()
    while True:
        if (getattr(currThread, "exit", False)):
            print (" going to break")
            break;
        print (" waiting on queue")
        try:
            (x,y,r) = queue.get(timeout= 1)
        except:
            continue;
        print ("getting from queue x,y,r ",x,y,r)
        if (r == -1):
            break;
        print (" Started Caching Service ",x,y,r)
        fetchAround(x,y,r,cache,cacheLock)

def canSupressRequest (Cache, x, y, r):
    pq = Queue.PriorityQueue()
    # Find the closest point
    for (x1,y1,r1) in Cache:
        dist = math.sqrt((x-x1)**2 + (y-y1)**2)
        pq.put((dist, (x1,y1,r1)))
    if (0 == pq.qsize()):
        print (" canSupressRequest return false",x,y,r)
        return False
    (dist, tup) = pq.get()
    print (" closest ",dist,tup)
    if (dist < (r/3)):
        print (" canSupressRequest returning true",x,y,r," dist ",dist," 1+r/2",1+r/2)
        return True
    print (" canSupressRequest returning false ",x,y,r)
    return False

def main (Cache, CacheLock, messageQueue):
    prevX = prevY = prevR = None
    global CurrentSession
    if (True):
        #try:
        #    (x,y,r) = input(" Enter x,y,r :>> ")
        #except:
        #    print (" Exiting! ")
        #    killDisplaySession(CurrentSession)
        #    break;
        log = open("./vlog","wa+")
        fp = open("./points", "r")
        print (' reading lines ')
        lines = fp.readlines()
        for line in lines:
            lt = line.split()
            x = float(lt[0])
            y = float(lt[1])
            r = 5.0
            logClient(" Send request! pt: x="+str(x)+" y="+str(y)+" radius="+str(r))
            if (validateInput(x,y,r)):
                # Replace this by  some sort of closeness logic
                canSupress = False
                canSupress = canSupressRequest(Cache, x, y, r)
                messageQueue.put((float(x), float(y), float(r)))
                if (False == canSupress) and ((x,y,r)  not in Cache):
                    st = time.time()
                    result = sendRequestToServer(ServerIp, ServerPort, [[x,y,r]])
                    if (result):
                        log.write(str(x)+" "+str(y)+" "+str(r)+" "+str(time.time()- st)+" "+str(getSize(result))+"\n")
                        print (" Co-ordinate : x = %f y = %f radius = %f" %(x,y,r))
                        print (" Size        : %s bytes" %(getSize(result)))
                        print (" Timetaken   : %f seconds " %(time.time()- st))
                        #logClient(" Obtained reply! pt: x=" + str(x) + " y=" + str(y) + " radius=" + str(r) + " time: "+str(time.time()-st)+" seconds")
                        CacheLock.acquire()
                        Cache[(x,y,r)] = result
                        CacheLock.release()
                    else:
                        #logClient(" Connection Failed! pt: x=" + str(x) + " y=" + str(y) + " rad   ius=" + str(r))
                        continue;
                else:
                    logClient(" Fetching from from Local Cache!")
                    log.write(str(x) + " " + str(y) + " " + str(r) + "  0   N/a \n")
                if (canSupress == False):
                    pathToPointCloudFile  = Cache[(x,y,r)]
                    startorUpdateDisplay (x,y,r,pathToPointCloudFile)
            time.sleep(2)
    #killDisplaySession(CurrentSession)
Cache = dict()
CacheLock = threading.Lock()
messageQueue = Queue.Queue()

# Start the caching thread
cacheThread = threading.Thread(target=cachingService,args=(Cache, CacheLock, messageQueue))
cacheThread.start()

# Start the Main Thread
main(Cache, CacheLock, messageQueue)
print (" out of main ..")
cacheThread.exit = True
messageQueue.put(-1,-1,-1)
cacheThread.join()
