# fireDashboardScript.py
# ===========================================
# Date Modified: January 27, 2022
# Author: Cat Schooley
# ===========================================

#============================================ Set-up ============================================

# import modules
import arcpy, arcgis, os, sys
from zipfile import ZipFile
from arcpy import env
from arcgis.gis import GIS
from getpass import getpass 
from time import process_time

startTime = process_time()

# User input
# This can be hardcoded instead
folderPath = r'C:\Users\cschooley\Documents\Work\fireDashboardTesting'
arcpy.env.workspace = folderPath
arcpy.env.overwriteOutput = True

portalURL = r'https://arcgis.com'
username = 'cschooley_OGM'
print("Enter Password: ")
password = getpass()  #can be hardcoded, not recommended
gis = GIS(portalURL, username, password)

# ======================================== Input Hosted Feature Layers ======================================

fireLayerLocation = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/Current_WildlandFire_Perimeters/FeatureServer/0"
coalLayerLocation = "https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/Coalpermit/FeatureServer/0"
mineralLayerLocation = "https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/Large_Small_Mines_2019_NAD83/FeatureServer/0"
oilgasLayerLocation = "https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/viewAGRC_WellData_Surf/FeatureServer/0"
amrLayerLocation = "https://services.arcgis.com/ZzrwjTRez6FJiOq4/arcgis/rest/services/viewAGRC_AMR/FeatureServer/0"

# ======================================== Output Shapefile Locations =====================================

utahFires = folderPath + "\\utahFires"
fireBuffers = folderPath + "\\fireBuffers"
coalLocations = folderPath + "\\coalLocations"
mineralLocations = folderPath + "\\mineralLocations"
oilGasLocations = folderPath + "\\oilGasLocations"
amrLocations = folderPath + "\\amrLocations"

coalJoined = folderPath + "\\coalJoined"
mineralJoined = folderPath + "\\mineralJoined"
oilGasJoined = folderPath + "\\oilGasJoined"
amrJoined = folderPath + "\\amrJoined"

# ======================================== Output Hosted Feature Layers ===================================

fireBuffersItemId = "4c9a54f53ca1404597b590d1d37873ee"
coalJoinedItemId = "ca42728a00ee421f88e2585b201edb3f"
mineralJoinedItemId = "d0c45ddee4624854b3a7bacfd6a12b10"
oilGasJoinedItemId = "d0b88683ea294d55bd39af95ae25f9c0"
amrJoinedItemId = "0ceef6b8862143cf804fd4931badd1ea"

# ======================================= Create Temporary Local Feature Layers =========================================

def createFeatureLayer(inFeatures, outLayer, whereClause):
    arcpy.management.MakeFeatureLayer(in_features = inFeatures,
                                      out_layer = outLayer,
                                      where_clause = whereClause)


createFeatureLayer(fireLayerLocation, utahFires, "irwin_POOState = 'US_UT'")
fireCount = int(arcpy.GetCount_management(utahFires).getOutput(0))
print(fireCount)
print(type(fireCount))
if fireCount < 1:
    print("No fire boundaries in Utah at this time")
    sys.exit()
createFeatureLayer(coalLayerLocation, coalLocations, "")
createFeatureLayer(mineralLayerLocation, mineralLocations, "")
createFeatureLayer(oilgasLayerLocation, oilGasLocations, "")
createFeatureLayer(amrLayerLocation, amrLocations, "")

# ======================================== Beginning of Geoprocessing ===================================================
# Be aware of feature layers with text cells exceeding 254 characters. They may be truncated or unable to write to the new feature class.
# Field names may also be truncated
# Use your best judgement to decide if you need to perform manual field mapping

# Create buffers around fire perimeters at .1 (this helps to include the area within perimeter), 1 mile, and 5 miles
arcpy.analysis.MultipleRingBuffer(Input_Features = UtahFires,
                                  Output_Feature_class = fireBuffers,
                                  Distances = [0.1, 1, 5],
                                  Buffer_Unit = "Miles")

# Function for creating buffers
def spatialJoinBuffers(targetFeatures, joinFeatures, outFeatureClass, matchOption):
    arcpy.analysis.SpatialJoin(target_features = targetFeatures,
                               join_features = joinFeatures,
                               out_feature_class = outFeatureClass,
                               match_option = matchOption)

print("Joining coal mine locations to fire buffer layer")    
spatialJoinBuffers(coalLocations, fireBuffers, coalJoined, "INTERSECT")

print("Joining mineral mine locations to fire buffer layer")
spatialJoinBuffers(mineralLocations, fireBuffers, mineralJoined, "INTERSECT")

print("Joining oil and gas well locations to fire buffer layer")
spatialJoinBuffers(oilGasLocations, fireBuffers, oilGasJoined, "INTERSECT")

print("Joining abandoned mine locations to fire buffer layer")
spatialJoinBuffers(amrLocations, fireBuffers, amrJoined, "INTERSECT")

# ============================== Overwriting Hosted Feature Layers =====================================
# Though overwriting the layers would be an option with the use of view layers as to not lose customizations like symbology and pop-ups, 
# this truncate\append workflow was used to bypass the need for view layers.

# Another note about this workflow is that each feature as added as a new feature, not as an updated feature

# Function to Zip FGD
def zipDir(dirPath, zipPath):
    zipf = ZipFile(zipPath , mode='w')
    gdb = os.path.basename(dirPath)
    for root, _ , files in os.walk(dirPath):
        for file in files:
            if 'lock' not in file:
               filePath = os.path.join(root, file)
               zipf.write(filePath , os.path.join(gdb, file))
    zipf.close()

# Function to update hosted feature layers by truncating the one currently hosted and appending the new data to it
def updateHosted(fc, fsItemId):
    print("Creating temporary File Geodatabase")
    arcpy.CreateFileGDB_management(arcpy.env.scratchFolder, "TempGDB")
    # Export feature classes to temporary File Geodatabase
    fcName = os.path.basename(fc)
    fcName = fcName.split('.')[-1]
    print("Exporting {0} to temp FGD".format(fcName))
    arcpy.conversion.FeatureClassToFeatureClass(fc, os.path.join(arcpy.env.scratchFolder, "TempGDB.gdb"), fcName)

    # Zip temp FGD
    print("Zipping temp FGD")
    zipDir(os.path.join(arcpy.env.scratchFolder, "TempGDB.gdb"), os.path.join(arcpy.env.scratchFolder, "TempGDB.gdb.zip"))

    # Check if FGD exists, if True, delete item
    searchResults = gis.content.search(f'title:tempFGD AND owner:{username}', item_type='File Geodatabase')
    if len(searchResults) > 0:
        item = searchResults[0]
        item.delete()

    # Upload zipped File Geodatabase
    print("Uploading File Geodatabase")
    fgdProperties={'title':'tempFGD', 'tags':'temp file geodatabase', 'type':'File Geodatabase'}
    fgdItem = gis.content.add(item_properties=fgdProperties,
                              data=os.path.join(arcpy.env.scratchFolder, "TempGDB.gdb.zip"))

    # Truncate Feature Service
    print("Truncating Feature Service")
    premiseLayer = gis.content.get(fsItemId)
    fLyr = premiseLayer.layers[0]
    fLyr.manager.truncate()

    # Append features from feature class
    print("Appending features")
    fLyr.append(item_id=fgdItem.id,
                upload_format="filegdb",
                upsert=False,
                field_mappings=[])

    # Delete Uploaded File Geodatabase
    print("Deleting uploaded File Geodatabase")
    fgdItem.delete()

    # Delete temporary File Geodatabase and zip file
    print("Deleting temporary FGD and zip file")
    arcpy.Delete_management(os.path.join(arcpy.env.scratchFolder, "TempGDB.gdb"))
    os.remove(os.path.join(arcpy.env.scratchFolder, "TempGDB.gdb.zip"))

# Updating hosted feature layers
updateHosted(fireBuffers, fireBuffersItemId)
updateHosted(coalJoined, coalJoinedItemId)
updateHosted(mineralJoined, mineralJoinedItemId)
updateHosted(oilGasJoined, oilGasJoinedItemId)
updateHosted(amrJoined, amrJoinedItemId)

endTime = process_time()
elapsedTime = round((endTime-startTime)/60, 2)

print(startTime, endTime)
print(f"Process completed in {elapsedTime} minutes")
