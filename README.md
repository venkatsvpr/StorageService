# StorageService
Storage Services for RTabMap 

## Client - Capabilities
The client connect to server pushes the RGB-Image and localizes it on the Map (obtains a x,y,z)
After obtaining a x,y,z use it to fetch the ply chunck of interest from the server
Start Asynchronus fetch the ply of the points that are around x,y,z
The client caches request and suppressess request if it already has the point cloud 

## Server - Capabilities
Convert the db-file to a in memory ply-cache
Performs localization on the image sent by the client
When a fetch for x,y,z,radius is given chunk a part of the PlyCache and send it to the client
Ther sever pefroms caching of the request so that selecting a part of the PlyCache is not done every time.



