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
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverAddress = (ip, port)
    print ("Connnecting to server socket")
    serverSock.connect(serverAddress)


    numberOfCoordinates = len(listOfCoordinates)
    if (numberOfCoordinates <= 0):
        return None

    payload_out = Length(numberOfCoordinates)
    nsent = 0
    nsent += serverSock.send(payload_out)
    print (listOfCoordinates)
    for item in listOfCoordinates:
        payload_out = Payload(item[0], item[1], item[2])
        nsent += serverSock.send(payload_out)

    buffer = serverSock.recv(sizeof(Length))
    lengthToRead = Length.from_buffer_copy(buffer)
    toRead = lengthToRead.len

    # the file path should be in some format
    # TODO
    outFile = open("/tmp/1", "wb")
    data = None
    while (True):
        data = None
        if (toRead < 1024):
            data = serverSock.recv(toRead)
        else:
            data = serverSock.recv(1024)
        if (data == None) or (len(data) == 0):
            break
        outFile.write(data)
    outFile.close()
    return "/tmp/1"

def validateInput (x,y,r):
    """
    :param x:  X co-ordinate
    :param y:  Y co-ordinate
    :param r:  R radius
    :return: True/False Value

    We have to validate the x,y,radius and return True/False value
    """
    return True

def main ():
    """ Temporarily Cache the path corresponding to (x,y,r), Objective is to cache the file in client side """
    """ 
    TODO
    1)  This could be really a robust cache.. Like if we have cached 1,1 to  5,5 and we get a request for
        2,2 to 4,4 we could pull 1,1 to 5,5 in constant time rather than fetching 
    2)  (1) is at the cost of more memory on client.. we could offload this work to server
    """
    Cache = dict()
    while (True):
        (x,y,r) = input(" Enter x,y,r in the same order and format. >> ")
        if (validateInput(x,y,r)):
            if ((x,y,r)  not in Cache):
                Cache[(x,y,r)] = sendRequestToServer(ServerIp, ServerPort, [[x,y,r]])
            else:
                print ("File Locally Cached, Bringing it back!! ")
            pathToPointCloudFile  = Cache[(x,y,r)]
            print (" will be triggering on ",pathToPointCloudFile)

main()
