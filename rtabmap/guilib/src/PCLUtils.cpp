//
// Created by nox on 10/28/18.
//

#include "rtabmap/gui/PCLUtils.h"
#include "rtabmap/utilite/ULogger.h"

#include <pcl/filters/conditional_removal.h>
#include <pcl/io/pcd_io.h>
#include <pcl/io/ply_io.h>


namespace rtabmap {

    pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr PCLUtils::filterOutliers(
            pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr cloud,
            pcl::KdTreeFLANN<pcl::PointXYZRGBNormal> * kdtree,
            float x,
            float y,
            float radius) {
        pcl::PointXYZRGBNormal startPoint;
        startPoint.x = x;
        startPoint.y = y;

        std::vector<int> foundIndices;
        std::vector<float> sqDistances;

        pcl::PointCloud<pcl::PointXYZRGBNormal>::Ptr subCloud (new pcl::PointCloud<pcl::PointXYZRGBNormal>);

        if (kdtree->radiusSearch(startPoint, radius, foundIndices, sqDistances) <= 0) {
            UWARN("No points found, return empty cloud!");
            return subCloud;
        }

        for (size_t i = 0; i < foundIndices.size (); ++i) {
            subCloud->points.push_back(cloud->points[foundIndices[i]]);
        }

        subCloud->width = subCloud->points.size();
        subCloud->height = 1;
        subCloud->is_dense = cloud->is_dense;

        return subCloud;
    }


    int PCLUtils::pclToBinary(pcl::PointCloud<pcl::PointXYZRGBNormal> & cloudToConvert, std::stringstream & outstream)
    {
        bool use_camera = true;

        pcl::PCLPointCloud2 cloud;
        pcl::toPCLPointCloud2(cloudToConvert, cloud);

        Eigen::Quaternionf orientation = cloudToConvert.sensor_orientation_;
        Eigen::Vector4f origin = cloudToConvert.sensor_origin_;

        if (cloud.data.empty ())
        {
            return (-1);
        }

        unsigned int nr_points  = cloud.width * cloud.height;
        unsigned int point_size = static_cast<unsigned int> (cloud.data.size () / nr_points);

        // Compute the range_grid, if necessary, and then write out the PLY header
        bool doRangeGrid = !use_camera && cloud.height > 1;
        std::vector<pcl::io::ply::int32> rangegrid (nr_points);
        if (doRangeGrid)
        {
            unsigned int valid_points = 0;

            // Determine the field containing the x-coordinate
            int xfield = pcl::getFieldIndex (cloud, "x");
            if (xfield >= 0 && cloud.fields[xfield].datatype != pcl::PCLPointField::FLOAT32)
                xfield = -1;

            // If no x-coordinate field exists, then assume all points are valid
            if (xfield < 0)
            {
                for (unsigned int i=0; i < nr_points; ++i)
                    rangegrid[i] = i;
                valid_points = nr_points;
            }
                // Otherwise, look at their x-coordinates to determine if points are valid
            else
            {
                for (size_t i=0; i < nr_points; ++i)
                {
                    float value;
                    memcpy(&value, &cloud.data[i * point_size + cloud.fields[xfield].offset], sizeof(float));
                    if (pcl_isfinite(value))
                    {
                        rangegrid[i] = valid_points;
                        ++valid_points;
                    }
                    else
                        rangegrid[i] = -1;
                }
            }
            outstream << _generateHeader(cloud, origin, true, use_camera, valid_points);
        }
        else
        {
            outstream << _generateHeader(cloud, origin, true, use_camera, nr_points);
        }

        // Iterate through the points
        for (unsigned int i = 0; i < nr_points; ++i)
        {
            // Skip writing any invalid points from range_grid
            if (doRangeGrid && rangegrid[i] < 0)
                continue;

            size_t total = 0;
            for (size_t d = 0; d < cloud.fields.size (); ++d)
            {
                int count = cloud.fields[d].count;
                if (count == 0)
                    count = 1; //workaround
                if (count > 1)
                {
                    static unsigned int ucount (count);
                    outstream.write (reinterpret_cast<const char*> (&ucount), sizeof (unsigned int));
                }
                // Ignore invalid padded dimensions that are inherited from binary data
                if (cloud.fields[d].name == "_")
                {
                    total += cloud.fields[d].count; // jump over this many elements in the string token
                    continue;
                }

                for (int c = 0; c < count; ++c)
                {
                    switch (cloud.fields[d].datatype)
                    {
                        case pcl::PCLPointField::INT8:
                        {
                            char value;
                            memcpy (&value, &cloud.data[i * point_size + cloud.fields[d].offset + (total + c) * sizeof (char)], sizeof (char));
                            outstream.write (reinterpret_cast<const char*> (&value), sizeof (char));
                            break;
                        }
                        case pcl::PCLPointField::UINT8:
                        {
                            unsigned char value;
                            memcpy (&value, &cloud.data[i * point_size + cloud.fields[d].offset + (total + c) * sizeof (unsigned char)], sizeof (unsigned char));
                            outstream.write (reinterpret_cast<const char*> (&value), sizeof (unsigned char));
                            break;
                        }
                        case pcl::PCLPointField::INT16:
                        {
                            short value;
                            memcpy (&value, &cloud.data[i * point_size + cloud.fields[d].offset + (total + c) * sizeof (short)], sizeof (short));
                            outstream.write (reinterpret_cast<const char*> (&value), sizeof (short));
                            break;
                        }
                        case pcl::PCLPointField::UINT16:
                        {
                            unsigned short value;
                            memcpy (&value, &cloud.data[i * point_size + cloud.fields[d].offset + (total + c) * sizeof (unsigned short)], sizeof (unsigned short));
                            outstream.write (reinterpret_cast<const char*> (&value), sizeof (unsigned short));
                            break;
                        }
                        case pcl::PCLPointField::INT32:
                        {
                            int value;
                            memcpy (&value, &cloud.data[i * point_size + cloud.fields[d].offset + (total + c) * sizeof (int)], sizeof (int));
                            outstream.write (reinterpret_cast<const char*> (&value), sizeof (int));
                            break;
                        }
                        case pcl::PCLPointField::UINT32:
                        {
                            if (cloud.fields[d].name.find ("rgba") == std::string::npos)
                            {
                                unsigned int value;
                                memcpy (&value, &cloud.data[i * point_size + cloud.fields[d].offset + (total + c) * sizeof (unsigned int)], sizeof (unsigned int));
                                outstream.write (reinterpret_cast<const char*> (&value), sizeof (unsigned int));
                            }
                            else
                            {
                                pcl::RGB color;
                                memcpy (&color, &cloud.data[i * point_size + cloud.fields[d].offset + (total + c) * sizeof (unsigned int)], sizeof (pcl::RGB));
                                unsigned char r = color.r;
                                unsigned char g = color.g;
                                unsigned char b = color.b;
                                unsigned char a = color.a;
                                outstream.write (reinterpret_cast<const char*> (&r), sizeof (unsigned char));
                                outstream.write (reinterpret_cast<const char*> (&g), sizeof (unsigned char));
                                outstream.write (reinterpret_cast<const char*> (&b), sizeof (unsigned char));
                                outstream.write (reinterpret_cast<const char*> (&a), sizeof (unsigned char));
                            }
                            break;
                        }
                        case pcl::PCLPointField::FLOAT32:
                        {
                            if (cloud.fields[d].name.find ("rgb") == std::string::npos)
                            {
                                float value;
                                memcpy (&value, &cloud.data[i * point_size + cloud.fields[d].offset + (total + c) * sizeof (float)], sizeof (float));
                                outstream.write (reinterpret_cast<const char*> (&value), sizeof (float));
                            }
                            else
                            {
                                pcl::RGB color;
                                memcpy (&color, &cloud.data[i * point_size + cloud.fields[d].offset + (total + c) * sizeof (float)], sizeof (pcl::RGB));
                                unsigned char r = color.r;
                                unsigned char g = color.g;
                                unsigned char b = color.b;
                                outstream.write (reinterpret_cast<const char*> (&r), sizeof (unsigned char));
                                outstream.write (reinterpret_cast<const char*> (&g), sizeof (unsigned char));
                                outstream.write (reinterpret_cast<const char*> (&b), sizeof (unsigned char));
                            }
                            break;
                        }
                        case pcl::PCLPointField::FLOAT64:
                        {
                            double value;
                            memcpy (&value, &cloud.data[i * point_size + cloud.fields[d].offset + (total + c) * sizeof (double)], sizeof (double));
                            outstream.write (reinterpret_cast<const char*> (&value), sizeof (double));
                            break;
                        }
                        default:
                            break;
                    }
                }
            }
        }

        if (use_camera)
        {
            // Append sensor information
            float t;
            for (int i = 0; i < 3; ++i)
            {
                if (origin[3] != 0)
                    t = origin[i]/origin[3];
                else
                    t = origin[i];
                outstream.write (reinterpret_cast<const char*> (&t), sizeof (float));
            }
            Eigen::Matrix3f R = orientation.toRotationMatrix ();
            for (int i = 0; i < 3; ++i)
                for (int j = 0; j < 3; ++j)
                {
                    outstream.write (reinterpret_cast<const char*> (&R (i, j)),sizeof (float));
                }

            const float zerof = 0;
            for (int i = 0; i < 5; ++i)
                outstream.write (reinterpret_cast<const char*> (&zerof), sizeof (float));

            // width and height
            int width = cloud.width;
            outstream.write (reinterpret_cast<const char*> (&width), sizeof (int));

            int height = cloud.height;
            outstream.write (reinterpret_cast<const char*> (&height), sizeof (int));

            for (int i = 0; i < 2; ++i)
                outstream.write (reinterpret_cast<const char*> (&zerof), sizeof (float));
        }
        else if (doRangeGrid)
        {
            // Write out range_grid
            for (size_t i=0; i < nr_points; ++i)
            {
                pcl::io::ply::uint8 listlen;

                if (rangegrid[i] >= 0)
                {
                    listlen = 1;
                    outstream.write (reinterpret_cast<const char*> (&listlen), sizeof (pcl::io::ply::uint8));
                    outstream.write (reinterpret_cast<const char*> (&rangegrid[i]), sizeof (pcl::io::ply::int32));
                }
                else
                {
                    listlen = 0;
                    outstream.write (reinterpret_cast<const char*> (&listlen), sizeof (pcl::io::ply::uint8));
                }
            }
        }
    }

    std::string PCLUtils::_generateHeader (
        pcl::PCLPointCloud2 &cloud,
        Eigen::Vector4f &origin,
        bool binary,
        bool use_camera,
        int valid_points)
    {
        std::ostringstream oss;
        // Begin header
        oss << "ply";
        if (!binary)
            oss << "\nformat ascii 1.0";
        else
        {
            if (cloud.is_bigendian)
                oss << "\nformat binary_big_endian 1.0";
            else
                oss << "\nformat binary_little_endian 1.0";
        }
        oss << "\ncomment PCL generated";

        if (!use_camera)
        {
            oss << "\nobj_info is_cyberware_data 0"
                   "\nobj_info is_mesh 0"
                   "\nobj_info is_warped 0"
                   "\nobj_info is_interlaced 0";
            oss << "\nobj_info num_cols " << cloud.width;
            oss << "\nobj_info num_rows " << cloud.height;
            oss << "\nobj_info echo_rgb_offset_x " << origin[0];
            oss << "\nobj_info echo_rgb_offset_y " << origin[1];
            oss << "\nobj_info echo_rgb_offset_z " << origin[2];
            oss << "\nobj_info echo_rgb_frontfocus 0.0"
                   "\nobj_info echo_rgb_backfocus 0.0"
                   "\nobj_info echo_rgb_pixelsize 0.0"
                   "\nobj_info echo_rgb_centerpixel 0"
                   "\nobj_info echo_frames 1"
                   "\nobj_info echo_lgincr 0.0";
        }

        oss << "\nelement vertex "<< valid_points;

        for (std::size_t i = 0; i < cloud.fields.size (); ++i)
        {
            if (cloud.fields[i].name == "normal_x")
            {
                oss << "\nproperty float nx";
            }
            else if (cloud.fields[i].name == "normal_y")
            {
                oss << "\nproperty float ny";
            }
            else if (cloud.fields[i].name == "normal_z")
            {
                oss << "\nproperty float nz";
            }
            else if (cloud.fields[i].name == "rgb")
            {
                oss << "\nproperty uchar red"
                       "\nproperty uchar green"
                       "\nproperty uchar blue";
            }
            else if (cloud.fields[i].name == "rgba")
            {
                oss << "\nproperty uchar red"
                       "\nproperty uchar green"
                       "\nproperty uchar blue"
                       "\nproperty uchar alpha";
            }
            else
            {
                oss << "\nproperty";
                if (cloud.fields[i].count != 1)
                    oss << " list uint";
                switch (cloud.fields[i].datatype)
                {
                    case pcl::PCLPointField::INT8 : oss << " char "; break;
                    case pcl::PCLPointField::UINT8 : oss << " uchar "; break;
                    case pcl::PCLPointField::INT16 : oss << " short "; break;
                    case pcl::PCLPointField::UINT16 : oss << " ushort "; break;
                    case pcl::PCLPointField::INT32 : oss << " int "; break;
                    case pcl::PCLPointField::UINT32 : oss << " uint "; break;
                    case pcl::PCLPointField::FLOAT32 : oss << " float "; break;
                    case pcl::PCLPointField::FLOAT64 : oss << " double "; break;
                    default :
                    {
                        PCL_ERROR ("[pcl::PLYWriter::generateHeader] unknown data field type!");
                        return ("");
                    }
                }
                oss << cloud.fields[i].name;
            }
        }

        if (use_camera)
        {
            oss << "\nelement camera 1"
                   "\nproperty float view_px"
                   "\nproperty float view_py"
                   "\nproperty float view_pz"
                   "\nproperty float x_axisx"
                   "\nproperty float x_axisy"
                   "\nproperty float x_axisz"
                   "\nproperty float y_axisx"
                   "\nproperty float y_axisy"
                   "\nproperty float y_axisz"
                   "\nproperty float z_axisx"
                   "\nproperty float z_axisy"
                   "\nproperty float z_axisz"
                   "\nproperty float focal"
                   "\nproperty float scalex"
                   "\nproperty float scaley"
                   "\nproperty float centerx"
                   "\nproperty float centery"
                   "\nproperty int viewportx"
                   "\nproperty int viewporty"
                   "\nproperty float k1"
                   "\nproperty float k2";
        }
        else if (cloud.height > 1)
        {
            oss << "\nelement range_grid " << cloud.width * cloud.height;
            oss << "\nproperty list uchar int vertex_indices";
        }

        // End header
        oss << "\nend_header\n";
        return (oss.str ());
    }
}