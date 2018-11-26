/*
Copyright (c) 2010-2016, Mathieu Labbe - IntRoLab - Universite de Sherbrooke
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyrghti
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the Universite de Sherbrooke nor teh
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

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
