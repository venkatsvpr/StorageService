//
// Created by nox on 10/27/18.
//


#include <iostream>
#include <fstream>

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
        QTcpSocket socket;
        socket.setSocketDescriptor(_sd);

        socket.waitForReadyRead(-1);
        QDataStream ds(&socket);

        UWARN("Accepted connection.");

        float x, y, radius;
        ds >> x >> y >> radius;

        char *fileName = new char[1024];
        sprintf(fileName,"/tmp/server/%f_%f_%f.ply",x,y,radius);
        std::ifstream tFile(fileName);

        // Check if the file is there meaning we have already processed this.
        // just get it from cache and sent it over
        if (tFile.good()) {
            tFile.close();
            UWARN (" Caching already exists on Server.. Sending the file back to client.. ");

            std::fstream inFile;
            inFile.open (fileName, std::ios::in | std::ios::binary	 );
            inFile.seekg(0, std::ios::end);
            unsigned int fileSize = inFile.tellg();
            inFile.seekg(0, std::ios::beg);

            // get the size and send it over
            ds << fileSize;
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
                if(fileSize - bytesSent >= 1024)
                    bytesToSend = 1024;
                else
                    bytesToSend = fileSize - bytesSent;
                socket.write(fileBuffer+bytesSent, bytesToSend);
                socket.waitForBytesWritten();
                bytesSent += bytesToSend;
            }
            delete [] fileBuffer;
        } else {
            // Get from the ply cache and send it over.
            UWARN(" > requesting x=%g, y=%g, radius=%g", x, y, radius);

            pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr target = _pclutils->filterOutliers(_cloud, _kdtree, x, y, radius);
            std::stringstream outstream(std::stringstream::in | std::stringstream::out | std::ios::binary);
            _pclutils->pclToBinary(*target, outstream);

            outstream.seekg (0, outstream.end);
            int size = outstream.tellg();
            outstream.seekg (0, outstream.beg);

            UWARN("Sending %d bytes...", size);

            ds << size;
            socket.waitForBytesWritten();

            std::fstream file;
            file.open (fileName, std::ios::out | std::ios::binary	 );

            char * buffer = new char[1024];
            while(!outstream.eof()) {
                outstream.read(buffer, 1024);
                int size = outstream.gcount();
                file.write(buffer,size);
                socket.write(buffer, size);
                socket.waitForBytesWritten();
            }

            file.close();
            delete[] buffer;
        }
        socket.close();
        UWARN("Done! Closed connection.");
    }
}