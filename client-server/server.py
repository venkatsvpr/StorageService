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

def getSize(filename):
    st = os.stat(filename)
    return st.st_size

def sendFileSizeOnConnection (filePath, connection):
    file = open(filePath, "rb")
    size = getSize(filePath)
    payload_out = Length(size)
    nsent = connection.send(payload_out)
    file.close()

def sendFileOnConnction (filePath, connection):
    file = open(filePath,'rb')
    data = file.read(1024)
    while (data):
       connection.send(data)
       data = file.read(1024)
    file.close()


def main ():
    if True:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((ServerIp, ServerPort))
        sock.listen(1)
        # Receive data from the server and shut down
        while True:
            connection, address = sock.accept()
            print (" accepting connection ",connection,address)
            Points = []
            buffer = connection.recv(sizeof(Length))
            lengthToRead = Length.from_buffer_copy(buffer)
            toRead = lengthToRead.len
            for i in range(int(toRead)):
                buffer = connection.recv(sizeof(Payload))
                coord = Payload.from_buffer_copy(buffer)
                Points.append(coord)
            """ do some function call here """
            print ("point ",int(coord.x),int(coord.y),int(coord.r))
            filePath ="/tmp/2"
            sendFileSizeOnConnection (filePath,connection)
            sendFileOnConnction (filePath, connection)
            print (" Done! ")
            connection.close()
        #except:
    #    print (" Catching Exception")
main()
