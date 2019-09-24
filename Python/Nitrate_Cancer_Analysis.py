# Kevin Palmer
# University of Wisconsin-Madison
# GEOG 777 -Capstone in GIS Development
# Fall 2019


# Import Modules
import os
import arcpy



# ------------------------------------------------------------------------------


# Set global variables

# Reference data
# Census Counties
counties = r"g777_project1_shapefiles\cancer_county\cancer_county.shp"

# Input Data
# Well Points
wells = r"g777_project1_shapefiles\well_nitrate\well_nitrate.shp"
# Census Tracts
tracts = r"g777_project1_shapefiles\cancer_tracts\cancer_tracts.shp"

# User input variables
idwK = 3 # <-- This value needs to be a variable input by app user
hexSize = 10 # <-- This value needs to be a variable input by app user
hexUnit = "Miles" # <-- This value needs to be a variable input by app user


# ------------------------------------------------------------------------------


# Generate IDW raster from well_nitrate.shp nitrate values
# http://desktop.arcgis.com/en/arcmap/10.6/tools/spatial-analyst-toolbox/idw.htm
def runIDW(wells, idwK):
	# Check out the ArcGIS Spatial Analyst extension license
	arcpy.CheckOutExtension("Spatial")

	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\GEOG777_Project_1_Nitrate_Cancer\Data"
	dataFolder = arcpy.env.workspace
	arcpy.env.overwriteOutput = True

	# Set local variables for IDW
	inPointFeatures = os.path.join(dataFolder, wells)
	zField = "nitr_ran"
	# cellSize =
	powerK = idwK
	# searchRadius =
	# in_barrier_polyline_features =

	# Execute IDW
	nitrateIDW = arcpy.sa.Idw(inPointFeatures, zField, "", powerK, "", "")

	# Save the output
	nitrateIDW.save(r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1\nitrateIDW")

	# Delete local variables
	del dataFolder, inPointFeatures, zField, powerK

	# Check in the ArcGIS Spatial Analyst extension license
	arcpy.CheckInExtension("Spatial")

	#
	print("nitrateIDW generated")

	# Return nitrateIDW to global scope
	return nitrateIDW


# ------------------------------------------------------------------------------


# Generate Feature to Raster raster from census tracts cancer rate values
# http://desktop.arcgis.com/en/arcmap/10.6/tools/spatial-analyst-toolbox/idw.htm
def runFeatToRast(tracts):
	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\GEOG777_Project_1_Nitrate_Cancer\Data"
	dataFolder = arcpy.env.workspace
	arcpy.env.overwriteOutput = True

	# Set local variables for Feature to Raster
	inFeatures = os.path.join(dataFolder, tracts)
	field = "canrate"
	canrateRaster = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1\canrate"
	# cellSize =

	# Execute Feature to Raster
	arcpy.FeatureToRaster_conversion(inFeatures, field, canrateRaster, "")

	# Delete local variables
	del dataFolder, inFeatures, field

	#
	print("canrateRaster generated")

	# Return canrateRaster to global scope
	return canrateRaster


# ------------------------------------------------------------------------------


# Generate Tessellation hexagons --> User chooses hexagon size but default value is 10 sq. mi. and extent is the census tracts
# http://desktop.arcgis.com/en/arcmap/10.6/tools/data-management-toolbox/generatetesellation.htm
def generateHexbins(counties, hexSize, hexUnit):
	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\GEOG777_Project_1_Nitrate_Cancer\Data"
	dataFolder = arcpy.env.workspace
	arcpy.env.overwriteOutput = True

	# Set local variables for Generate Tessellation
	outputFolder = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1"
	outputName = "Hexagons_" + str(hexSize) + "_sq_" + hexUnit + ".shp"
	output = os.path.join(outputFolder, outputName)
	extentFeature = os.path.join(dataFolder, counties)
	description = arcpy.Describe(extentFeature)
	extent = description.extent
	area = str(hexSize) + " Square" + hexUnit
	spatial_ref = extent.spatialReference

	# Execute Generate Tessellation
	arcpy.GenerateTessellation_management (output, extent, "Hexagon", area, spatial_ref)
	hexBins = output


	# Delete the hexagons that don't intersect with the counties
	# http://desktop.arcgis.com/en/arcmap/10.6/tools/data-management-toolbox/select-layer-by-location.htm
	# Make layers for hexbins and counties
	hexBins_lyr = arcpy.MakeFeatureLayer_management(hexBins, "hexBins_lyr")
	counties_lyr = arcpy.MakeFeatureLayer_management(extentFeature, "counties_lyr")

	# Select hexagons that DO NOT intersect with the counties layer
	arcpy.SelectLayerByLocation_management(hexBins_lyr, "intersect", counties_lyr, "", "", "INVERT")

	# Delete the selection
	# http://desktop.arcgis.com/en/arcmap/10.3/tools/data-management-toolbox/delete-features.htm
	arcpy.DeleteFeatures_management(hexBins_lyr)

	# Delete local variables
	del dataFolder, outputFolder, outputName, output, extentFeature, description, extent, area, spatial_ref, \
		hexBins_lyr, counties_lyr

	#
	print("hexBins generated")

	# Return hexBins to global scope
	return hexBins


# ------------------------------------------------------------------------------


# Calculate Zonal Statistics as Table for the nitrate raster into the hexagons --> choose all statistics
# http://desktop.arcgis.com/en/arcmap/10.6/tools/spatial-analyst-toolbox/zonal-statistics-as-table.htm
def zonalStatsNitrate(nitrateIDW, hexBins):
	# Check out the ArcGIS Spatial Analyst extension license
	arcpy.CheckOutExtension("Spatial")

	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1"
	dataFolder = arcpy.env.workspace
	arcpy.env.overwriteOutput = True

	# Set local variables for Zonal Statistics as Table
	inZoneData = hexBins
	zoneField = "GRID_ID"
	inValueRaster = nitrateIDW
	outTableName = "nitrateZSat"
	outTable = os.path.join(dataFolder, outTableName)

	# Execute Zonal Statistics as Table for nitrateIDW
	nitrateZSaT = arcpy.sa.ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "NODATA", "ALL")

	# Delete local variables
	del dataFolder, inZoneData, zoneField, inValueRaster, outTableName, outTable

	# Check in the ArcGIS Spatial Analyst extension license
	arcpy.CheckInExtension("Spatial")

	#
	print("nitrateZSaT generated")

	# Return nitrataeZSAT to global scope
	return nitrateZSaT


# ------------------------------------------------------------------------------


# Calculate Zonal Statistics as Table for the canrate raster into the hexagons --> choose all statistics
# http://desktop.arcgis.com/en/arcmap/10.6/tools/spatial-analyst-toolbox/zonal-statistics-as-table.htm
def zonalStatsCanRate(canrate, hexBins):
	# Check out the ArcGIS Spatial Analyst extension license
	arcpy.CheckOutExtension("Spatial")

	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1"
	dataFolder = arcpy.env.workspace
	arcpy.env.overwriteOutput = True

	# Set local variables for Zonal Statistics as Table
	inZoneData = hexBins
	zoneField = "GRID_ID"
	inValueRaster = canrate
	outTableName = "canrateZSat"
	outTable = os.path.join(dataFolder, outTableName)

	# Execute Zonal Statistics as Table for canrateIDW
	canrateZSaT = arcpy.sa.ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "NODATA", "ALL")

	# Delete local variables
	del dataFolder, inZoneData, zoneField, inValueRaster, outTableName, outTable

	# Check in the ArcGIS Spatial Analyst extension license
	arcpy.CheckInExtension("Spatial")

	#
	print("canrateZSaT generated")

	# Return canrataeZSAT to global scope
	return canrateZSaT


# ------------------------------------------------------------------------------


# Rename fields in the nitrate table with "nitrate_" prefix


# ------------------------------------------------------------------------------


# Rename fields in the canrate table with "canrate_" prefix


# ------------------------------------------------------------------------------


# Join both tables to the hexagons


# ------------------------------------------------------------------------------


# Run OLS (Ordinary Least Squares) linear regression analysis -->
# Input: Hexagons, UniqueID: rowid, Out: name, DV: canrate, IV: nitraate, OutReport: name


# ------------------------------------------------------------------------------


# Main script function
def main():
	nitrateIDW = runIDW(wells, idwK)
	canrate = runFeatToRast(tracts)
	hexBins = generateHexbins(counties, hexSize, hexUnit)
	nitrateZSat = zonalStatsNitrate(nitrateIDW, hexBins)
	canrateZSat = zonalStatsCanRate(canrate, hexBins)


# ------------------------------------------------------------------------------

# Execute main function
main()
