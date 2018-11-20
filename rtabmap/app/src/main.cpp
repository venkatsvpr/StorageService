//
// Created by vikramsingh on 11/18/18.
//
#include <QApplication>
#include <QtCore/QDir>
#include "rtabmap/utilite/UEventsManager.h"
#include "rtabmap/core/RtabmapThread.h"
#include "rtabmap/core/Rtabmap.h"
#include "rtabmap/gui/MainWindow.h"
#include <QMessageBox>
#include "rtabmap/utilite/UObjDeletionThread.h"
#include "rtabmap/utilite/UFile.h"
#include "rtabmap/utilite/UConversion.h"
#include "ObjDeletionHandler.h"
#include "rtabmap/core/CameraRGB.h"
#include "rtabmap/core/Transform.h"
#include <opencv2/core/core.hpp>
#include "rtabmap/utilite/UFile.h"
#include <stdio.h>
#include <pcl/io/pcd_io.h>
#include <pcl/io/ply_io.h>
#include <pcl/filters/filter.h>
#include "rtabmap/core/util3d.h"
#include <sqlite3.h>


using namespace rtabmap;

static int callback(void *data, int argc, char **argv, char **azColName){
    int i;
    fprintf(stderr, "%s: ", (const char*)data);
    
    for(i = 0; i<argc; i++){
        printf("%s = %s\n", azColName[i], argv[i] ? argv[i] : "NULL");
    }
    
    printf("\n");
    return 0;
}


int main(int argc, char * argv[])
{
    
    
    std::string imageDir = "/home/vikramsingh/acs/cooke_col_2";
    std::string configFile = "/home/vikramsingh/acs/working_config.ini";
    std::string databasePath = "/home/vikramsingh/Downloads/map_01.db";
    
    
    //    sqlite3 *db;
    //    char *zErrMsg = 0;
    //    int rc;
    //    const char* data = "Callback function called";
    //    char *query = "SELECT * FROM Node WHERE id = 50";
    //
    //    rc = sqlite3_open("/home/vikramsingh/Downloads/map_01.db", &db);
    //
    //    if( rc ) {
    //        fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
    //        return(0);
    //    }
    //
    //    rc = sqlite3_exec(db, query, callback, (void*)data, &zErrMsg);
    //    if( rc != SQLITE_OK ){
    //
    //        fprintf(stderr, "SQL error: %s\n", zErrMsg);
    //
    //        sqlite3_free(zErrMsg);
    //
    //    }else{
    //
    //        fprintf(stdout, "Operation done successfully\n");
    //
    //    }
    //    sqlite3_close(db);
    
    
    
    rtabmap::CameraImages camera(imageDir);
    
    if(!camera.init())
    {
        printf("Camera init failed, using path \"%s\"\n", imageDir.c_str());
        exit(1);
    }
    
    rtabmap::Rtabmap rtabmap;
    rtabmap.init(configFile, databasePath);
    
    //    std::list<int> wm = rtabmap.getWM();
    //
    //    for(int i =0; i<wm.size(); i++){
    //        int id = wm.front();
    //        printf("%d \n", id);
    //        wm.pop_front();
    //
    //        printf("x = %f \n",rtabmap.getPose(id).x());
    //
    //    }
    
    
    rtabmap::SensorData data1 = camera.takeImage();
    int nextIndex = rtabmap.getLastLocationId()+1;
    while(!data1.imageRaw().empty())
    {
        rtabmap.process(data1.imageRaw(), nextIndex);
        int localizedId = rtabmap.getLoopClosureId();
        if(localizedId > 0)
        {
            rtabmap::Transform const rtab_pose = rtabmap.getPose(rtabmap.getLoopClosureId());
            printf("xxxx %f \n",rtab_pose.x());
            
            printf("localization successful. id is %d", localizedId);
        }
        else
        {
            std::cout<<"could not localize";
        }
        ++nextIndex;
        data1 = camera.takeImage();
    }
    
    rtabmap.close();
    return 0;
}
