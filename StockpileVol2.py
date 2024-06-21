from whitebox_workflows import PhotometricInterpretation, RasterDataType, WbEnvironment

wbe = WbEnvironment()
wbe.verbose = True
wbe.max_procs = -1

# Let's begin by downloading the Whitebox Workflows 'Jay_State_Forest' sample data
wbe.working_directory = wbe.download_sample_data('Jay_State_Forest')
print(f'Data have been stored in: {wbe.working_directory}')

# Now read the 'DEM.tif' file...
dem = wbe.read_raster('DEM.tif')

# The RasterConfigs of a Raster object contains useful metadata about the Raster.
print(f'Rows: {dem.configs.rows}')
print(f'Columns: {dem.configs.columns}')
print(f'Resolution (x direction): {dem.configs.resolution_x}')
print(f'Resolution (y direction): {dem.configs.resolution_y}')
print(f'North: {dem.configs.north}')
print(f'South: {dem.configs.south}')
print(f'East: {dem.configs.east}')
print(f'West: {dem.configs.west}')
print(f'Min value: {dem.configs.minimum}')
print(f'Max value: {dem.configs.maximum}')
print(f'EPSG code: {dem.configs.epsg_code}') # 0 if not set
print(f'Nodata value: {dem.configs.nodata}')
# What data type are stored in raster grid cells?
# See the RasterDataType class for more info.
print(f'Data type: {dem.configs.data_type}') 
# What is the photometric interpretation, continuous, categorical, RGB, etc.?
# See the PhotometricInterpretation class for more info.
print(f'Photometric interpretation: {dem.configs.photometric_interp}')

# We create new rasters most frequently by copying the RasterConfigs from another
# existing Raster object. We can also create a new RasterConfigs manually but
# when we want to create a new Raster that has the same rows, columns and extent
# as another Raster, copying the other Raster's RasterConfigs, and modifying it
# as needed, is a good way forward.
out_configs = dem.configs

# Once you create a new Raster, you cannot change certain things about it, such
# as the number of rows and columns and the data type. The RasterDataType must
# be able to hold the data values. In the case below, we are reclassifying the
# raster to a Boolean, with 1's and 0's. So we really only need small, integer
# level data. I16 is used in this case to allow for NoData values, which will
# be set to -32768, the smallest possible 16-bit int.
out_configs.data_type = RasterDataType.I16 
out_configs.nodata = -32768.0
out_configs.photometric_interp = PhotometricInterpretation.Categorical

# Now let's create the new raster, based on our customized RasterConfigs...
high_areas = wbe.new_raster(out_configs)

# When we create a new raster, it is initially filled with NoData values, as
# set in its RasterConfigs.
print(f'Cell(500, 500) = {high_areas[500, 500]}') # = -32768.0

# Let's manipulate the raster data at the individual grid cell level.
print("Finding high elevations")
old_progress = -1
for row in range(dem.configs.rows):
    for col in range(dem.configs.columns):
        elev = dem[row, col] # Read a cell value from a Raster
        if elev > 800.0 and elev != dem.configs.nodata:
            high_areas[row, col] = 1.0 # Write the cell value of a Raster

            # Regardless of the RasterDataType used to store the cell
            # data in memory and in file, data are always passed to and
            # returned from rasters as floats. Note that the cell value
            # is set to 1.0 above and not 1.
        elif elev != dem.configs.nodata:
            # We must do the check for NoData, or else we'll replace
            # NoData values in the input raster with 0's in the output. 
            # NoData in must be NoData out.
            high_areas[row, col] = 0.0
    
    # Update the progress after each completed row scan.
    progress = int(((row + 1.0) / dem.configs.rows) * 100.0)
    if progress != old_progress:
        old_progress = progress
        print(f'Progress: {progress}%')

# Write the new Raster to file.
print('Saving data to file...')
wbe.write_raster(high_areas, 'high_areas.tif', compress=True)

# This allows for very fine-grained raster manipulation for custom data processing.
# But if the same functionality exists within the WbW toolset, you should always 
# prefer the native solution, because it will be faster than the Python alternative. 
# The code above could have been more efficiently processed using the following:
#high_areas = dem > 800.0
