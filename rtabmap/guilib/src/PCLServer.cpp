//
// Created by nox on 10/27/18.
//


#include <iostream>
#include <fstream>
#include <vector>

#include "rtabmap/gui/PCLServer.h"
#include "rtabmap/utilite/ULogger.h"

#include <QTcpServer>
#include <QTcpSocket>
#include <QDataStream>


namespace rtabmap {

    PCLServer::PCLServer(Rtabmap * rt, pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr cloud):
    QTcpServer(0)
    {
        _rt = rt;
        _cloud = cloud;
        _pclutils = new PCLUtils();
        _kdtree = new pcl::KdTreeFLANN<pcl::PointXYZRGBNormal>();
        _kdtree->setInputCloud(_cloud);

        // create the thread pool
        pool = new QThreadPool(this);
        pool->setMaxThreadCount(5);
    }

    void PCLServer::runServer() {

        if (this->listen(QHostAddress::Any, 8001)) {
            UWARN("");
            UWARN("Started server! Waiting for connections...");
        }

    }

    void PCLServer::incomingConnection(qintptr sd) {
        PCLServerWorker * worker = new PCLServerWorker(_rt, _pclutils, _cloud, _kdtree, sd);
        worker->setAutoDelete(true);
        pool->start(worker);
    }


    void PCLServerWorker::run() {
        int connection_type;
        QTcpSocket socket;
        socket.setSocketDescriptor(_sd);
        QDataStream ds(&socket);

        UWARN("Accepted connection.");

        socket.waitForReadyRead();
        ds >> connection_type;
        UWARN("Connection type is %i", connection_type);

        switch(connection_type) {
            case 1:
            {
                handle_type1(socket, ds);
                break;
            }
            case 2:
            {
                handle_type2(socket, ds);
                break;
            }
            default:
                UWARN("Unknown connection type.");
        }

        socket.close();
        UWARN("Done! Closed connection.");
    }

    void PCLServerWorker::handle_type1(QTcpSocket &socket, QDataStream &ds) {
        int image_size, read = 0, bytes = 0;
        ds >> image_size;
        char * image_buffer = new char[image_size];

        UWARN("Reading input image of size %i bytes...", image_size);
        while(read < image_size) {
            bytes = (int) socket.read(image_buffer + read,
                                      (image_size-read) < CHUNK_SIZE ? (image_size-read) : CHUNK_SIZE);
            if(bytes == 0 && !socket.waitForReadyRead()) {
                UWARN("Connection unexpectedly closed");
                delete[] image_buffer;
                return;
            }
            read += bytes;
        }

        UWARN("Done! Performing localization...");
        float x, y, z;
        if (!localize(x, y, z, image_buffer, image_size)) {
            UWARN("Unable to localize");
            delete[] image_buffer;
            return;
        }
        UWARN("Done! x=%g, y=%g, z=%g", x, y, z);

        ds << 1 << x << y << z;
        socket.waitForBytesWritten();

        delete[] image_buffer;
    }

    void PCLServerWorker::handle_type2(QTcpSocket &socket, QDataStream &ds) {
        float x, y, z, radius;
        ds >> x >> y >> z >> radius;

        UWARN("Request for x=%g, y=%g, z=%g, radius=%g", x, y, z, radius);

        char *fileName = new char[CHUNK_SIZE];
        sprintf(fileName,"/tmp/server/%f_%f_%f.ply",x,y,radius);
        std::ifstream tFile(fileName);

        // Check if the file is there meaning we have already processed this.
        // just get it from cache and sent it over
        if (tFile.good()) {
            tFile.close();
            UWARN ("Caching already exists on Server.. Sending the file back to client.. ");

            std::fstream inFile;
            inFile.open (fileName, std::ios::in | std::ios::binary);
            inFile.seekg(0, std::ios::end);
            unsigned int fileSize = inFile.tellg();
            inFile.seekg(0, std::ios::beg);

            // get the size and send it over
            ds << 2 << fileSize;
            socket.waitForBytesWritten();

            //get the file in buffer
            char* fileBuffer = new char[fileSize];
            inFile.read (fileBuffer, fileSize);
            inFile.close();

            //send file in chunks
            unsigned int bytesSent = 0;
            int bytesToSend = 0;

            // send it in multiples of 1024 bytes
            while(bytesSent < fileSize)
            {
                if(fileSize - bytesSent >= CHUNK_SIZE)
                    bytesToSend = CHUNK_SIZE;
                else
                    bytesToSend = fileSize - bytesSent;
                socket.write(fileBuffer+bytesSent, bytesToSend);
                socket.waitForBytesWritten();
                bytesSent += bytesToSend;
            }
            delete [] fileBuffer;
        } else {
            // Get from the ply cache and send it over.
            pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr target = _pclutils->filterOutliers(_cloud, _kdtree, x, y, radius);
            std::stringstream outstream(std::stringstream::in | std::stringstream::out | std::ios::binary);
            _pclutils->pclToBinary(*target, outstream);

            outstream.seekg (0, outstream.end);
            int size = outstream.tellg();
            outstream.seekg (0, outstream.beg);

            UWARN("Sending %d bytes...", size);

            ds << 2 << size;
            socket.waitForBytesWritten();

            std::fstream file;
            file.open (fileName, std::ios::out | std::ios::binary);

            char * buffer = new char[CHUNK_SIZE];
            while(!outstream.eof()) {
                outstream.read(buffer, CHUNK_SIZE);
                int size = outstream.gcount();
                file.write(buffer,size);
                socket.write(buffer, size);
                socket.waitForBytesWritten();
            }

            file.close();
            delete[] buffer;
        }
    }

    bool PCLServerWorker::localize(float &x, float &y, float &z, char *image_buffer, int image_size) {
        std::vector<char> encoded_image(image_buffer, image_buffer + image_size);
        cv::Mat image = cv::imdecode(encoded_image, cv::IMREAD_ANYCOLOR);

        _rt->process(image, _rt->getLastLocationId()+1);
        int localizedId = _rt->getLoopClosureId();
        if(localizedId <= 0)
            return false;

        const Transform t = _rt->getMemory()->getSignature(localizedId)->getPose();
        x = t.x();
        y = t.y();
        z = t.z();

        return true;
    }
}