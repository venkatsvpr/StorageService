//
// Created by nox on 10/27/18.
//

#ifndef RTABMAP_SERVER_H
#define RTABMAP_SERVER_H


#include <QRunnable>

#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/pcl_base.h>


namespace rtabmap {

    class ServerThread: public QRunnable {
    public:
        ServerThread(pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr);
        void run();


    private:
        pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr _cloud;

    };

}

#endif
