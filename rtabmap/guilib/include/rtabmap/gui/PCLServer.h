//
// Created by nox on 10/27/18.
//

#ifndef RTABMAP_SERVER_H
#define RTABMAP_SERVER_H


#include <QTcpServer>

#include "rtabmap/gui/PCLUtils.h"

#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/pcl_base.h>
#include <pcl/filters/conditional_removal.h>
#include <pcl/filters/radius_outlier_removal.h>


namespace rtabmap {

    class PCLServer : public QTcpServer {

    Q_OBJECT

    public:
        PCLServer(pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr);

        void runServer();

    private:
        PCLUtils * _pclutils;
        pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr _cloud;
        pcl::KdTreeFLANN<pcl::PointXYZRGBNormal> *_kdtree;

    protected:
        void incomingConnection(qintptr) override;

    };

}
#endif
