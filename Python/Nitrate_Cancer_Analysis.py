# Kevin Palmer
# University of Wisconsin-Madison
# GEOG 777 -Capstone in GIS Development
# Fall 2019


# ------------------------------------------------------------------------------


# Import Modules
import os
import arcpy


# ------------------------------------------------------------------------------


# Project setup


# ------------------------------------------------------------------------------


arcpy.env.overwriteOutput = True
arcpy.env.addOutputsToMap = True

# Get variables
# Source data
# Input Data
# Well Points
wells = arcpy.GetParameterAsText(0)
# Census Tracts
tracts = arcpy.GetParameterAsText(1)
# ReferenceData
# Census Counties
counties = arcpy.GetParameterAsText(2)

# User input variables
idwK = arcpy.GetParameterAsText(3)
hexSize = arcpy.GetParameterAsText(4)
hexUnit = "Miles"

#
arcpy.AddMessage("\nStarting job...")
arcpy.AddMessage("\nUser Input:\nIDW K Value: " + idwK + "\nHexbin Size: " + hexSize + " Square " + hexUnit)

# Create project GDB
# https://desktop.arcgis.com/en/arcmap/10.3/manage-data/administer-file-gdbs/create-file-geodatabase.htm
#
arcpy.AddMessage("\nCreating project geodatabase...")
projectFolder = arcpy.env.scratchFolder
projectGDB = arcpy.CreateFileGDB_management(projectFolder, "Nitrate_Cancer_Analysis.gdb")
#
arcpy.AddMessage("\n" + arcpy.GetMessages())
projectGDBPath = os.path.join(projectFolder, "Nitrate_Cancer_Analysis.gdb")

arcpy.AddMessage("\nProject geodatabase created:\n" + projectGDBPath)

# Copy source to project GDB
# http://desktop.arcgis.com/en/arcmap/10.3/tools/conversion-toolbox/feature-class-to-feature-class.htm
#
arcpy.AddMessage("\nCopying source data to project geodatabase...")
arcpy.FeatureClassToFeatureClass_conversion(wells, projectGDBPath, "Well_Nitrate")
#
arcpy.AddMessage("\n" + arcpy.GetMessages())
arcpy.FeatureClassToFeatureClass_conversion(tracts, projectGDBPath, "Wisc_Tracts")
#
arcpy.AddMessage("\n" + arcpy.GetMessages())
arcpy.FeatureClassToFeatureClass_conversion(counties, projectGDBPath, "Wisc_Counties")
#
arcpy.AddMessage("\n" + arcpy.GetMessages())

#
arcpy.AddMessage("\nSource data copied to project geodatabase.")


# ------------------------------------------------------------------------------


# Functions


# ------------------------------------------------------------------------------


# Generate IDW raster from well_nitrate.shp nitrate values
# http://desktop.arcgis.com/en/arcmap/10.6/tools/spatial-analyst-toolbox/idw.htm
def runIDW(wells, idwK, projectGDBPath):
	#
	arcpy.AddMessage("\nGenerating nitrate IDW raster...")

	# Check out the ArcGIS Spatial Analyst extension license
	arcpy.CheckOutExtension("Spatial")

	# Set local variables for IDW
	inPointFeatures = wells
	field = "nitr_ran"
	# cellSize =
	powerK = idwK
	# searchRadius =
	# in_barrier_polyline_features =
	nitrateIDWPath = os.path.join(projectGDBPath, "nitrateIDW")

	# Execute IDW
	nitrateIDW = arcpy.sa.Idw(inPointFeatures, field, "", powerK, "", "")
	# Get IDW Messages
	arcpy.AddMessage("\n" + arcpy.GetMessages())

	# Save the output
	nitrateIDW.save(nitrateIDWPath)

	# Add the output to the MXD
	arcpy.SetParameterAsText(5, nitrateIDW)

	#
	arcpy.AddMessage("\nNitrate IDW raster generated:\n" + nitrateIDWPath)

	# Delete local variables
	del inPointFeatures, field, powerK, nitrateIDWPath

	# Check in the ArcGIS Spatial Analyst extension license
	arcpy.CheckInExtension("Spatial")

	# Return nitrateIDW to global scope
	return nitrateIDW


# ------------------------------------------------------------------------------


# Generate Feature to Raster raster from census tracts cancer rate values
# http://desktop.arcgis.com/en/arcmap/10.6/tools/spatial-analyst-toolbox/idw.htm
def runFeatToRast(tracts, projectGDBPath):
	#
	arcpy.AddMessage("\nGenerating cancer rate raster...")

	# Set local variables for Feature to Raster
	inFeatures = tracts
	field = "canrate"
	canrateRasterPath = os.path.join(projectGDBPath, "canrateRaster")
	# cellSize =

	# Execute Feature to Raster
	arcpy.FeatureToRaster_conversion(inFeatures, field, canrateRasterPath, "")
	# Get Feature to Raster Messages
	arcpy.AddMessage("\n" + arcpy.GetMessages())

	# Create a raster layer to add to the MXD
	canrateRasterLyr = arcpy.MakeRasterLayer_management(canrateRasterPath, "canrateRaster")

	# Add the output to the MXD
	arcpy.SetParameterAsText(6, canrateRasterLyr)

	#
	arcpy.AddMessage("\nCancer rate raster generated:\n" + canrateRasterPath)

	# Delete local variables
	del inFeatures, field, canrateRasterPath

	# Return canrateRaster to global scope
	return canrateRasterLyr


# ------------------------------------------------------------------------------


# Generate Tessellation hexagons --> User chooses hexagon size but default value is 10 sq. mi. and extent is the census tracts
# http://desktop.arcgis.com/en/arcmap/10.6/tools/data-management-toolbox/generatetesellation.htm
def runGenerateHexbins(counties, hexSize, hexUnit, projectGDBPath):
	#
	arcpy.AddMessage("\nGenerating tessellation hexagons...")

	# Set local variables for Generate Tessellation
	outputName = "Hexagons_" + hexSize + "_Sq_" + hexUnit
	if ("." in outputName):
		outputName = outputName.replace(".", "point")
	output = os.path.join(projectGDBPath, outputName)

	# https://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-functions/describe.htm
	description = arcpy.Describe(counties)
	extent = description.extent
	area = hexSize + " Square" + hexUnit
	spatial_ref = extent.spatialReference

	# Execute Generate Tessellation
	arcpy.GenerateTessellation_management(output, extent, "Hexagon", area, spatial_ref)
	# Get Generate Tesselation Messages
	arcpy.AddMessage("\n" + arcpy.GetMessages())

	#
	hexBins = output

	# Delete the hexagons that don't intersect with the counties
	# http://desktop.arcgis.com/en/arcmap/10.6/tools/data-management-toolbox/select-layer-by-location.htm
	# Make layers for hexbins and counties
	hexBinsLyr = arcpy.MakeFeatureLayer_management(hexBins, "hexBinsLyr")
	#
	arcpy.AddMessage("\n" + arcpy.GetMessages())

	counties_lyr = arcpy.MakeFeatureLayer_management(counties, "counties_lyr")
	#
	arcpy.AddMessage("\n" + arcpy.GetMessages())


	# Select hexagons that intersect with the counties layer
	arcpy.SelectLayerByLocation_management(hexBinsLyr, "intersect", counties_lyr, "", "", "")
	# Switch selection
	arcpy.SelectLayerByLocation_management(hexBinsLyr, "", "", "", "SWITCH_SELECTION", "")
	#
	arcpy.AddMessage("\n" + arcpy.GetMessages())

	# Delete the selection
	# http://desktop.arcgis.com/en/arcmap/10.3/tools/data-management-toolbox/delete-features.htm
	arcpy.DeleteFeatures_management(hexBinsLyr)
	#
	arcpy.AddMessage("\n" + arcpy.GetMessages())

	# Add a Unique ID integer field to use later in OLS regression
	arcpy.AddField_management(hexBinsLyr, "UID", "SHORT", "", "", "", "UID")
	#
	arcpy.AddMessage("\n" + arcpy.GetMessages())

	# Calculate the UID field from the FID field
	arcpy.CalculateField_management(hexBinsLyr, "UID", "!OBJECTID!", "PYTHON")
	#
	arcpy.AddMessage("\n" + arcpy.GetMessages())

	# Add the output to the MXD
	arcpy.SetParameterAsText(7, hexBinsLyr)

	#
	arcpy.AddMessage("\nTessellation hexagons generated:\n" + hexBins)

	# Delete local variables
	del outputName, output, description, extent, area, spatial_ref, \
		hexBins, counties_lyr

	# Return hexBins to global scope
	return hexBinsLyr


# ------------------------------------------------------------------------------


# Calculate Zonal Statistics as Table for the nitrate raster into the hexagons --> choose all statistics
# http://desktop.arcgis.com/en/arcmap/10.6/tools/spatial-analyst-toolbox/zonal-statistics-as-table.htm
def runZonalStatsNitrate(nitrateIDW, hexBins_lyr, projectGDBPath):
	#
	arcpy.AddMessage("\nGenerating nitrate level statistics per hexagon...")

	# Check out the ArcGIS Spatial Analyst extension license
	arcpy.CheckOutExtension("Spatial")

	# Set local variables for Zonal Statistics as Table
	inZoneData = hexBins_lyr
	zoneField = "GRID_ID"
	inValueRaster = nitrateIDW
	outTableName = "nitrateZSat"
	outTable = os.path.join(projectGDBPath, outTableName)

	# Execute Zonal Statistics as Table for nitrateIDW
	nitrateZSaT = arcpy.sa.ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "NODATA", "ALL")
	#
	arcpy.AddMessage("\n" + arcpy.GetMessages())

	# Add the output to the MXD
	arcpy.SetParameterAsText(8, nitrateZSaT)

	#
	arcpy.AddMessage("\nNitrate level statistics per hexagon generated:\n" + outTable)

	# Delete local variables
	del nitrateIDW, inZoneData, zoneField, inValueRaster, outTableName, outTable

	# Check in the ArcGIS Spatial Analyst extension license
	arcpy.CheckInExtension("Spatial")

	# Return nitrateZSAT to global scope
	return nitrateZSaT


# ------------------------------------------------------------------------------


# Calculate Zonal Statistics as Table for the canrate raster into the hexagons --> choose all statistics
# http://desktop.arcgis.com/en/arcmap/10.6/tools/spatial-analyst-toolbox/zonal-statistics-as-table.htm
def runZonalStatsCanRate(canrateRasterLyr, hexBins_lyr, projectGDBPath):
	#
	arcpy.AddMessage("\nGenerating cancer rate statistics per hexagon...")

	# Check out the ArcGIS Spatial Analyst extension license
	arcpy.CheckOutExtension("Spatial")

	# Set local variables for Zonal Statistics as Table
	inZoneData = hexBins_lyr
	zoneField = "GRID_ID"
	inValueRaster = canrateRasterLyr
	outTableName = "canrateZSat"
	outTable = os.path.join(projectGDBPath, outTableName)

	# Execute Zonal Statistics as Table for canrateIDW
	canrateZSaT = arcpy.sa.ZonalStatisticsAsTable(inZoneData, zoneField, inValueRaster, outTable, "NODATA", "ALL")
	#
	arcpy.AddMessage("\n" + arcpy.GetMessages())

	# Add the output to the MXD
	arcpy.SetParameterAsText(9, canrateZSaT)

	#
	arcpy.AddMessage("\nCancer rate statistics per hexagon generated:\n" + outTable)

	# Delete local variables
	del canrateRasterLyr, inZoneData, zoneField, inValueRaster, outTableName, outTable

	# Check in the ArcGIS Spatial Analyst extension license
	arcpy.CheckInExtension("Spatial")

	# Return canrateZSAT to global scope
	return canrateZSaT


# ------------------------------------------------------------------------------


# Rename fields in the nitrate table with "nitrate_" prefix
# https://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-functions/listfields.htm
# http://desktop.arcgis.com/en/arcmap/10.6/tools/data-management-toolbox/alter-field-properties.htm

def runPrefixNitrateZSat(projectGDBPath):
	#
	arcpy.AddMessage("\nRenaming nitrate level statistics table fields...")

	# Set local variables for Alter Field
	table = os.path.join(projectGDBPath, "nitrateZSaT")
	prefix = "nit_"
	# newTableName = "nitrateZSatPrefix"
	fieldList = arcpy.ListFields(table)

	# Execute Alter Field for nitrateZSaT table
	for field in fieldList:
		if (field.name != "OBJECTID"):
			prefixName = prefix + field.name
			arcpy.AlterField_management(table, field.name, prefixName, prefixName)
			#
			arcpy.AddMessage("\n" + arcpy.GetMessages())
			del prefixName

	# Delete local variables
	del table, prefix, fieldList

	#
	arcpy.AddMessage("\nNitrate level statistics table fields renamed.")


# ------------------------------------------------------------------------------


# Rename fields in the canrate table with "canrate_" prefix
# https://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-functions/listfields.htm
# http://desktop.arcgis.com/en/arcmap/10.6/tools/data-management-toolbox/alter-field-properties.htm

def runPrefixCanrateZSat(projectGDBPath):
	#
	arcpy.AddMessage("\nRenaming cancer rate statistics table fields...")

	# Set local variables for Alter Field
	table = os.path.join(projectGDBPath, "canrateZSat")
	prefix = "can_"
	# newTableName = "canrateZSatPrefix"
	fieldList = arcpy.ListFields(table)

	# Execute Alter Field for canrateZSaT table
	for field in fieldList:
		if (field.name != "OBJECTID"):
			prefixName = prefix + field.name
			arcpy.AlterField_management(table, field.name, prefixName, prefixName)
			#
			arcpy.AddMessage("\n" + arcpy.GetMessages())
			del prefixName

	# Delete local variables
	del table, prefix, fieldList

	#
	arcpy.AddMessage("\nCancer rate statistics table fields renamed.")


# ------------------------------------------------------------------------------


# Join both tables to the hexagons
# http://desktop.arcgis.com/en/arcmap/10.3/tools/data-management-toolbox/join-field.htm

def runJoinTables(hexBins_lyr, projectGDBPath):
	#
	arcpy.AddMessage("\nJoining hexagon polygons with nitrate level and cancer rate tables...")

	# Set local variables for Add Join
	nitrateZSaT = os.path.join(projectGDBPath, "nitrateZSat")
	canrateZSaT = os.path.join(projectGDBPath, "canrateZSat")

	#
	arcpy.JoinField_management(hexBins_lyr, "GRID_ID", nitrateZSaT, "nit_GRID_ID")
	#
	arcpy.AddMessage("\n" + arcpy.GetMessages())
	arcpy.JoinField_management(hexBins_lyr, "GRID_ID", canrateZSaT, "can_GRID_ID")
	#
	arcpy.AddMessage("\n" + arcpy.GetMessages())

	#
	arcpy.AddMessage("\nHexagon polygons joined with nitrate level and cancer rate tables.")


# ------------------------------------------------------------------------------


# Run OLS (Ordinary Least Squares) linear regression analysis -->
# Input: Hexagons, UniqueID: rowid, Out: name, DV: canrate, IV: nitraate, OutReport: name
# http://desktop.arcgis.com/en/arcmap/10.3/tools/spatial-statistics-toolbox/ordinary-least-squares.htm

def runOLS(hexBins_lyr, projectFolder, projectGDBPath):
	#
	arcpy.AddMessage("\nRunning Ordinary Least Squares (OLS) linear regression on hexagon polygons using cancer rate as DV and nitrate levels as IV...")

	olsResults = os.path.join(projectGDBPath, "OLS_Results")
	olsCoefficients = os.path.join(projectGDBPath, "OLS_Coefficients")
	olsDiagnostics = os.path.join(projectGDBPath, "OLS_Diagnostics")
	olsReport = os.path.join(projectFolder, "OLS_Report.pdf")
	#
	arcpy.OrdinaryLeastSquares_stats(hexBins_lyr, "UID", olsResults, "can_MEAN", "nit_MEAN", olsCoefficients, olsDiagnostics, olsReport)
	#
	arcpy.AddMessage("\n" + arcpy.GetMessages())

	# Add the output to the MXD
	arcpy.SetParameterAsText(10, olsResults)
	arcpy.SetParameterAsText(11, olsCoefficients)
	arcpy.SetParameterAsText(12, olsDiagnostics)
	arcpy.SetParameterAsText(13, olsReport)

	#
	arcpy.AddMessage("\nOLS Results generated:\n" + olsResults)
	#
	arcpy.AddMessage("\nOLS Coefficients generated:\n" + olsCoefficients)
	#
	arcpy.AddMessage("\nOLS Diagnostics generated:\n" + olsDiagnostics)
	#
	arcpy.AddMessage("\nOLS Report generated:\n" + olsReport)

	# Delete local variables
	del hexBins_lyr, olsResults, olsCoefficients, olsDiagnostics, olsReport, projectFolder, projectGDBPath

	#
	arcpy.AddMessage("\n\nWisconsin nitrate level and cancer rate Ordinary Least Squares (OLS) linear regression analysis completed.")


# ------------------------------------------------------------------------------


# Main script function


# ------------------------------------------------------------------------------


def main():

	nitrateIDW = runIDW(wells, idwK, projectGDBPath)
	canrateRasterLyr = runFeatToRast(tracts, projectGDBPath)
	hexBinsLyr = runGenerateHexbins(counties, hexSize, hexUnit, projectGDBPath)
	runZonalStatsNitrate(nitrateIDW, hexBinsLyr, projectGDBPath)
	runZonalStatsCanRate(canrateRasterLyr, hexBinsLyr, projectGDBPath)
	runPrefixNitrateZSat(projectGDBPath)
	runPrefixCanrateZSat(projectGDBPath)
	runJoinTables(hexBinsLyr, projectGDBPath)
	runOLS(hexBinsLyr, projectFolder, projectGDBPath)


# ------------------------------------------------------------------------------


# Execute main function


# ------------------------------------------------------------------------------


main()
