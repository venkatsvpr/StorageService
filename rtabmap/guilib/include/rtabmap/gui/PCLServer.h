//
// Created by nox on 10/27/18.
//

#ifndef RTABMAP_SERVER_H
#define RTABMAP_SERVER_H


#include <QTcpServer>
#include <QRunnable>
#include <QThreadPool>

#include "rtabmap/core/Rtabmap.h"
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
        PCLServer(Rtabmap *, pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr);

        void runServer();

    private:
        Rtabmap * _rt;
        PCLUtils * _pclutils;
        pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr _cloud;
        pcl::KdTreeFLANN<pcl::PointXYZRGBNormal> * _kdtree;
        QThreadPool * pool;

    protected:
        void incomingConnection(qintptr) override;

    };


    class PCLServerWorker : public QObject, public QRunnable {

    Q_OBJECT

    public:
        PCLServerWorker(Rtabmap * rt, PCLUtils * pclutils, pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr cloud,
                        pcl::KdTreeFLANN<pcl::PointXYZRGBNormal> * kdtree, qintptr sd):
                        _rt(rt), _pclutils(pclutils), _cloud(cloud), _kdtree(kdtree), _sd(sd) {};

    protected:
        void run();

    private:
        Rtabmap * _rt;
        PCLUtils * _pclutils;
        pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr _cloud;
        pcl::KdTreeFLANN<pcl::PointXYZRGBNormal> *_kdtree;
        qintptr _sd;
    };

}
#endif
