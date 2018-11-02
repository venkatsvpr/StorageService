from globals import  *

def validateInput (x,y,r):
    """
    :param x:  X co-ordinate
    :param y:  Y co-ordinate
    :param r:  R radius
    :return: True/False Value

    We have to validate the x,y,radius and return True/False value
    """
    return True

def sendFileSizeOnConnection (filePath, connection):
    size = getSize(filePath)
    connection.sendall(struct.pack('!i', size))

def sendFileOnConnection (filePath, connection):
    print ("Sending file to client")
    file = open(filePath,'rb')
    data = file.read(1024)
    while (data):
       connection.send(data)
       data = file.read(1024)
    print ("sent")
    file.close()

def logServer (msg):
    return log("ServerLog", ServerLogFile, msg)

def main ():
    if True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ServerIp, ServerPort))
        sock.listen(1)
        # Receive data from the server and shut down
        while True:
            logServer (" waiting to accept ..")
            connection, address = sock.accept()

            logServer (" accepting connection conn: <"+str(connection)+"> address: <"+str(address)+">\n");

            #toRead = readIntegerFromNetwork (connection)
            coord = readCoOrdinatesFromNetwork(connection)
            #serverFilePath = "/tmp/server/"+str(coord.x)+"_"+str(coord.y)+"_"+str(coord.r)+".ply"
            serverFilePath= "/tmp/server/0_0_5.ply"
            logServer(" processing point "+str(coord.x)+" "+str(coord.y)+" "+str(coord.r))

            sendFileSizeOnConnection (serverFilePath,connection)
            sendFileOnConnection (serverFilePath, connection)
            logServer (" done with servicing. Closing the connection. \n")
            connection.close()
main()  
