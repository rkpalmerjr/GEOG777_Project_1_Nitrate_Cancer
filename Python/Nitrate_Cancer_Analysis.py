# Kevin Palmer
# University of Wisconsin-Madison
# GEOG 777 -Capstone in GIS Development
# Fall 2019


# Import Modules
import os
import arcpy


# ------------------------------------------------------------------------------


# Project setup
# Set global variables

# Source data
# Input Data
# Well Points
wells = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\GEOG777_Project_1_Nitrate_Cancer\Data\g777_project1_shapefiles\well_nitrate\well_nitrate.shp"
# Census Tracts
tracts = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\GEOG777_Project_1_Nitrate_Cancer\Data\g777_project1_shapefiles\cancer_tracts\cancer_tracts.shp"
# ReferenceData
# Census Counties
counties = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\GEOG777_Project_1_Nitrate_Cancer\Data\g777_project1_shapefiles\cancer_county\cancer_county.shp"

# User input variables
idwK = 3 # <-- This value needs to be a variable input by app user
hexSize = 10 # <-- This value needs to be a variable input by app user
hexUnit = "Miles" # <-- This value needs to be a variable input by app user

#
print("Starting job...\n")
print("\nUser Input:\nIDW K Value: " + str(idwK) + "\nHexbin Size: " + str(hexSize) + "_Square " + hexUnit)

# Create project GDB
# https://desktop.arcgis.com/en/arcmap/10.3/manage-data/administer-file-gdbs/create-file-geodatabase.htm
#
print ("\nCreating project geodatabase...")
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1"
projectFolder = arcpy.env.workspace
projectGDB = arcpy.CreateFileGDB_management(projectFolder, "Test.gdb")
projectGDBPath = os.path.join(projectFolder, "Test.gdb")

print("\nProject geodatabase created:\n" + projectGDBPath)

# Copy source to project GDB
#
print("\nCopying source data to project geodatabase...")
arcpy.FeatureClassToFeatureClass_conversion(wells, projectGDBPath, "Well_Nitrate")
arcpy.FeatureClassToFeatureClass_conversion(tracts, projectGDBPath, "Wisc_Tracts")
arcpy.FeatureClassToFeatureClass_conversion(counties, projectGDBPath, "Wisc_Counties")

#
print("\nSource data copied to project geodatabase.")


# ------------------------------------------------------------------------------


# Generate IDW raster from well_nitrate.shp nitrate values
# http://desktop.arcgis.com/en/arcmap/10.6/tools/spatial-analyst-toolbox/idw.htm
def runIDW(wells, idwK, projectGDBPath):
	#
	print("\nGenerating nitrate IDW raster...")

	# Check out the ArcGIS Spatial Analyst extension license
	arcpy.CheckOutExtension("Spatial")

	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1\Scratch"
	dataFolder = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\GEOG777_Project_1_Nitrate_Cancer\Data"
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
	nitrateIDW.save(os.path.join(projectGDBPath, "nitrateIDW"))

	# Delete local variables
	del dataFolder, inPointFeatures, zField, powerK

	# Check in the ArcGIS Spatial Analyst extension license
	arcpy.CheckInExtension("Spatial")

	#
	print("\nNitrate IDW raster generated.")

	# Return nitrateIDW to global scope
	return nitrateIDW


# ------------------------------------------------------------------------------


# Generate Feature to Raster raster from census tracts cancer rate values
# http://desktop.arcgis.com/en/arcmap/10.6/tools/spatial-analyst-toolbox/idw.htm
def runFeatToRast(tracts, projectGDBPath):
	#
	print("\nGenerating cancer rate raster...")

	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1\Scratch"
	dataFolder = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\GEOG777_Project_1_Nitrate_Cancer\Data"

	# Set local variables for Feature to Raster
	inFeatures = os.path.join(dataFolder, tracts)
	field = "canrate"
	canrateRaster = os.path.join(projectGDBPath, "canrate")
	# cellSize =

	# Execute Feature to Raster
	arcpy.FeatureToRaster_conversion(inFeatures, field, canrateRaster, "")

	# Delete local variables
	del dataFolder, inFeatures, field

	#
	print("\nCancer rate raster generated.")

	# Return canrateRaster to global scope
	return canrateRaster


# ------------------------------------------------------------------------------


# Generate Tessellation hexagons --> User chooses hexagon size but default value is 10 sq. mi. and extent is the census tracts
# http://desktop.arcgis.com/en/arcmap/10.6/tools/data-management-toolbox/generatetesellation.htm
def runGenerateHexbins(counties, hexSize, hexUnit, projectGDBPath):
	#
	print("\nGenerating tessellation hexagons...")

	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1\Scratch"
	dataFolder = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\GEOG777_Project_1_Nitrate_Cancer\Data"

	# Set local variables for Generate Tessellation
	outputName = "Hexagons_" + str(hexSize) + "_sq_" + hexUnit
	output = os.path.join(projectGDBPath, outputName)
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

	# Add a Unique ID integer field to use later in OLS regression
	arcpy.AddField_management(hexBins_lyr, "UID", "SHORT", "", "", "", "UID")

	# Calculate the UID field from the FID field
	arcpy.CalculateField_management(hexBins_lyr, "UID", "!OBJECTID!", "PYTHON")

	# Delete local variables
	del dataFolder, outputName, output, extentFeature, description, extent, area, spatial_ref, \
		hexBins_lyr, counties_lyr

	#
	print("\nTessellation hexagons generated.")

	# Return hexBins to global scope
	return hexBins


# ------------------------------------------------------------------------------


# Calculate Zonal Statistics as Table for the nitrate raster into the hexagons --> choose all statistics
# http://desktop.arcgis.com/en/arcmap/10.6/tools/spatial-analyst-toolbox/zonal-statistics-as-table.htm
def runZonalStatsNitrate(nitrateIDW, hexBins, projectGDBPath):
	#
	print("\nGenerating nitrate level statistics per hexagon...")

	# Check out the ArcGIS Spatial Analyst extension license
	arcpy.CheckOutExtension("Spatial")

	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1\Scratch"

	# Set local variables for Zonal Statistics as Table
	inZoneData = hexBins
	zoneField = "GRID_ID"
	inValueRaster = nitrateIDW
	outTableName = "nitrateZSat"
	outTable = os.path.join(projectGDBPath, outTableName)

	# Execute Zonal Statistics as Table for nitrateIDW
	nitrateZSaT = arcpy.sa.ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "NODATA", "ALL")

	# Delete local variables
	del inZoneData, zoneField, inValueRaster, outTableName, outTable

	# Check in the ArcGIS Spatial Analyst extension license
	arcpy.CheckInExtension("Spatial")

	#
	print("\nNitrate level statistics per hexagon generated.")

	# Return nitrateZSAT to global scope
	return nitrateZSaT


# ------------------------------------------------------------------------------


# Calculate Zonal Statistics as Table for the canrate raster into the hexagons --> choose all statistics
# http://desktop.arcgis.com/en/arcmap/10.6/tools/spatial-analyst-toolbox/zonal-statistics-as-table.htm
def runZonalStatsCanRate(canrate, hexBins, projectGDBPath):
	#
	print("\nGenerating cancer rate statistics per hexagon...")

	# Check out the ArcGIS Spatial Analyst extension license
	arcpy.CheckOutExtension("Spatial")

	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1\Scratch"

	# Set local variables for Zonal Statistics as Table
	inZoneData = hexBins
	zoneField = "GRID_ID"
	inValueRaster = canrate
	outTableName = "canrateZSat"
	outTable = os.path.join(projectGDBPath, outTableName)

	# Execute Zonal Statistics as Table for canrateIDW
	canrateZSaT = arcpy.sa.ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "NODATA", "ALL")

	# Delete local variables
	del inZoneData, zoneField, inValueRaster, outTableName, outTable

	# Check in the ArcGIS Spatial Analyst extension license
	arcpy.CheckInExtension("Spatial")

	#
	print("\nCancer rate statistics per hexagon generated.")

	# Return canrateZSAT to global scope
	return canrateZSaT


# ------------------------------------------------------------------------------


# Rename fields in the nitrate table with "nitrate_" prefix
# http://desktop.arcgis.com/en/arcmap/10.6/tools/data-management-toolbox/alter-field-properties.htm
# http://desktop.arcgis.com/en/arcmap/10.6/analyze/python/mapping-fields.htm
# http://desktop.arcgis.com/en/arcmap/10.3/tools/conversion-toolbox/table-to-table.htm
# https://gis.stackexchange.com/questions/143867/change-field-names-automatically

def runPrefixNitrateZSat(projectGDBPath):
	#
	print("\nRenaming nitrate level statistics table fields...")

	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1\Scratch"

	# Set local variables for Alter Field
	table = os.path.join(projectGDBPath, "nitrateZSaT")
	prefix = "nit_"
	# newTableName = "nitrateZSatPrefix"
	fieldList = arcpy.ListFields(table)

	# OPTION 1 (If using GDB) - Execute Alter Field for nitrateZSaT table
	for field in fieldList:
		if (field.name != "OBJECTID"):
			prefixName = prefix + field.name
			arcpy.AlterField_management(table, field.name, prefixName, prefixName)

	# # OPTION 2 (If using shapefiles) - Execute Field Mapping and Table to Table for nitrateZSaT table
	# # Create empty field mappings object
	# field_mappings = arcpy.FieldMappings()
	#
	# # Loop through fields.  For each field, create a corresponding FieldMap object.
	# for field in fieldList:
	# 	# Local variables to add the "nit_" prefix to all field names
	# 	oldName = field.name
	# 	newName = prefix + oldName
	#
	# 	# Create a FieldMap object for all the old field names
	# 	newField = arcpy.FieldMap()
	# 	newField.addInputField(table, oldName)
	#
	# 	# Rename the output field
	# 	newFieldName = newField.outputField
	# 	newFieldName.name = newName
	# 	newFieldName.aliasName = newName
	# 	newField.outputField = newFieldName
	#
	# 	# Add the new field to the FieldMappings object
	# 	field_mappings.addFieldMap(newField)
	#
	# 	# Delete the local variables in the for loop
	# 	del oldName, newName, newField, newFieldName
	#
	# # Create a new table from the old table using the FieldMappings object
	# nitrateZSatPrefix = arcpy.TableToTable_conversion(nitrateZSaT, dataFolder, newTableName, field_mapping = field_mappings)

	# Delete local variables
	del table, prefix, fieldList
	# del table, prefix, newTableName, fieldList, field_mappings

	#
	print("\nNitrate level statistics table fields renamed.")

	# Return nitrateZSatPrefix to global scope
	# return nitrateZSatPrefix


# ------------------------------------------------------------------------------


# Rename fields in the canrate table with "canrate_" prefix
# http://desktop.arcgis.com/en/arcmap/10.6/tools/data-management-toolbox/alter-field-properties.htm
# http://desktop.arcgis.com/en/arcmap/10.6/analyze/python/mapping-fields.htm
# http://desktop.arcgis.com/en/arcmap/10.3/tools/conversion-toolbox/table-to-table.htm
# https://gis.stackexchange.com/questions/143867/change-field-names-automatically

def runPrefixCanrateZSat(projectGDBPath):
	#
	print("\nRenaming cancer rate statistics table fields...")

	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1\Scratch"

	# Set local variables for Alter Field
	table = os.path.join(projectGDBPath, "canrateZSat")
	prefix = "can_"
	# newTableName = "canrateZSatPrefix"
	fieldList = arcpy.ListFields(table)

	# OPTION 1 (If using GDB) - Execute Alter Field for canrateZSaT table
	for field in fieldList:
		if (field.name != "OBJECTID"):
			prefixName = prefix + field.name
			arcpy.AlterField_management(table, field.name, prefixName, prefixName)

	# # OPTION 2 (If using shapefiles) - Execute Field Mapping and Table to Table for canrateZSaT table
	# # Create empty field mappings object
	# field_mappings = arcpy.FieldMappings()
	#
	# # Loop through fields.  For each field, create a corresponding FieldMap object.
	# for field in fieldList:
	# 	# Local variables to add the "nit_" prefix to all field names
	# 	oldName = field.name
	# 	newName = prefix + oldName
	#
	# 	# Create a FieldMap object for all the old field names
	# 	newField = arcpy.FieldMap()
	# 	newField.addInputField(table, oldName)
	#
	# 	# Rename the output field
	# 	newFieldName = newField.outputField
	# 	newFieldName.name = newName
	# 	newFieldName.aliasName = newName
	# 	newField.outputField = newFieldName
	#
	# 	# Add the new field to the FieldMappings object
	# 	field_mappings.addFieldMap(newField)
	#
	# 	# Delete the local variables in the for loop
	# 	del oldName, newName, newField, newFieldName
	#
	# # Create a new table from the old table using the FieldMappings object
	# canrateZSatPrefix = arcpy.TableToTable_conversion(canrateZSaT, dataFolder, newTableName, field_mapping = field_mappings)

	# Delete local variables
	del table, prefix, fieldList
	# del table, prefix, newTableName, fieldList, field_mappings

	#
	print("\nCancer rate statistics table fields renamed.")

	# Return nitrateZSatPrefix to global scope
	# return canrateZSatPrefix


# ------------------------------------------------------------------------------


# Join both tables to the hexagons
# http://desktop.arcgis.com/en/arcmap/10.3/tools/data-management-toolbox/join-field.htm

def runJoinTables(hexBins, projectGDBPath):
	#
	print ("\nJoining hexagon polygons with nitrate level and cancer rate tables...")

	# Set environment settings
	arcpy.env.workspace = r"C:\Users\rkpalmerjr\Documents\School\WISC\Fall_2019\GEOG_777_Capstone_in_GIS_Development\Project_1\TESTING\Test_1\Scratch"

	# Set local variables for Add Join
	hexBinsLyr = arcpy.MakeFeatureLayer_management(hexBins, "hexBinsLyr")
	nitrateZSaT = os.path.join(projectGDBPath, "nitrateZSat")
	canrateZSaT = os.path.join(projectGDBPath, "canrateZSat")

	#
	arcpy.JoinField_management(hexBinsLyr, "GRID_ID", nitrateZSaT, "nit_GRID_ID")
	arcpy.JoinField_management(hexBinsLyr, "GRID_ID", canrateZSaT, "can_GRID_ID")

	#
	del hexBinsLyr

	#
	print ("\nHexagon polygons joined with nitrate level and cancer rate tables.")


# ------------------------------------------------------------------------------


# Run OLS (Ordinary Least Squares) linear regression analysis -->
# Input: Hexagons, UniqueID: rowid, Out: name, DV: canrate, IV: nitraate, OutReport: name
# http://desktop.arcgis.com/en/arcmap/10.3/tools/spatial-statistics-toolbox/ordinary-least-squares.htm

def runOLS(hexBins, projectFolder, projectGDBPath):
	#
	print("\nRunning Ordinary Least Squares (OLS) linear regression on hexagon polygons using cancer rate as DV and nitrate levels as IV...")
	# Set environment settings
	arcpy.env.workspace = projectFolder
	olsResults = os.path.join(projectGDBPath, "OLS_Results")
	olsCoefficients = os.path.join(projectGDBPath, "OLS_Coefficients")
	olsDiagnostics = os.path.join(projectGDBPath, "OLS_Diagnostics")
	olsReport = os.path.join(projectFolder, "OLS_Report.pdf")
	#
	arcpy.OrdinaryLeastSquares_stats(hexBins, "UID", olsResults, "can_MEAN", "nit_MEAN", olsCoefficients, olsDiagnostics, olsReport)

	#
	print("\n\nWisconsin nitrate level and cancer rate Ordinary Least Squares (OLS) linear regression analysis completed.")


# ------------------------------------------------------------------------------


# Main script function
def main():
	nitrateIDW = runIDW(wells, idwK, projectGDBPath)
	canrate = runFeatToRast(tracts, projectGDBPath)
	hexBins = runGenerateHexbins(counties, hexSize, hexUnit, projectGDBPath)
	runZonalStatsNitrate(nitrateIDW, hexBins, projectGDBPath)
	runZonalStatsCanRate(canrate, hexBins, projectGDBPath)
	runPrefixNitrateZSat(projectGDBPath)
	runPrefixCanrateZSat(projectGDBPath)
	runJoinTables(hexBins, projectGDBPath)
	runOLS(hexBins, projectFolder, projectGDBPath)


# ------------------------------------------------------------------------------

# Execute main function
main()
