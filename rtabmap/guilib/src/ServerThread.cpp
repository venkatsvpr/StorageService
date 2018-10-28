//
// Created by nox on 10/27/18.
//

#include "rtabmap/gui/ServerThread.h"


namespace rtabmap {

    ServerThread::ServerThread(pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr cloud) {
        _cloud = cloud;
    }

    void ServerThread::run() {

    }

}