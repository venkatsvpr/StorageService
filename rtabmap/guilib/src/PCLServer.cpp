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

    PCLServer::PCLServer(pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr cloud):
    QTcpServer(0)
    {
        _cloud = cloud;
        _pclutils = new PCLUtils();
        _kdtree = new pcl::KdTreeFLANN<pcl::PointXYZRGBNormal>();
        _kdtree->setInputCloud(_cloud);
    }

    void PCLServer::runServer() {

        if (this->listen(QHostAddress::Any, 8001)) {
            UWARN("");
            UWARN("Started server! Waiting for connections...");
        }

    }

    void PCLServer::incomingConnection(qintptr handl) {
        QTcpSocket socket;
        socket.setSocketDescriptor(handl);

        socket.waitForReadyRead(-1);
        QDataStream ds(&socket);

        UWARN("Accepted connection.");

        float x, y, radius;
        ds >> x >> y >> radius;

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

        char * buffer = new char[1024];
        while(!outstream.eof()) {
            outstream.read(buffer, 1024);
            int size = outstream.gcount();
            socket.write(buffer, size);
            socket.waitForBytesWritten();
        }

        socket.close();
        delete[] buffer;

        UWARN("Done! Closed connection.");
    }

}