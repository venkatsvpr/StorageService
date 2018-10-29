//
// Created by nox on 10/28/18.
//

#ifndef RTABMAP_PCLUTILS_H
#define RTABMAP_PCLUTILS_H

#include <pcl/point_cloud.h>
#include <pcl/point_types.h>
#include <pcl/pcl_base.h>
#include <pcl/conversions.h>
#include <pcl/filters/radius_outlier_removal.h>


namespace rtabmap {

    class PCLUtils {
    public:
        pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr filterOutliers(
                pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr,
                pcl::KdTreeFLANN<pcl::PointXYZRGBNormal> *,
                float,
                float,
                float);

        int pclToBinary(pcl::PointCloud<pcl::PointXYZRGBNormal> &, std::stringstream &);

    private:
        std::string _generateHeader(pcl::PCLPointCloud2 &, Eigen::Vector4f &, bool, bool, int);
    };
}

#endif //RTABMAP_PCLUTILS_H
