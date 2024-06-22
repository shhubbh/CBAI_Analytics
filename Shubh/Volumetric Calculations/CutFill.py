import whitebox
import numpy as np
import rasterio

# Initialize WhiteboxTools
wbt = whitebox.WhiteboxTools()

# Paths to the input DEM and DTM files
dem_file = "path/to/your/dem.tif"
reference_elevation = 0  # Assuming reference elevation
output_cut_fill_file = "path/to/output_cut_fill.tif"

# If you only have a DEM and no DTM, you can create a flat reference raster
with rasterio.open(dem_file) as dem_dataset:
    profile = dem_dataset.profile
    dem_data = dem_dataset.read(1)
    nodata_value = dem_dataset.nodata

    # Create a flat reference raster with the same shape and no-data value
    dtm_data = np.full(dem_data.shape, reference_elevation)
    dtm_data[dem_data == nodata_value] = nodata_value

    # Save the reference raster (flat DTM)
    dtm_file = "path/to/flat_dtm.tif"
    with rasterio.open(dtm_file, 'w', **profile) as dst:
        dst.write(dtm_data, 1)

# Perform cut-and-fill analysis using the DEM and flat DTM
wbt.cut_fill(dem_file, dtm_file, output_cut_fill_file)

# Open the resulting cut-fill file and calculate the volumes
with rasterio.open(output_cut_fill_file) as cut_fill_dataset:
    cut_fill_data = cut_fill_dataset.read(1)
    pixel_size = cut_fill_dataset.transform[0]  # Assuming square pixels

    # Separate cut and fill data
    cut_data = cut_fill_data[cut_fill_data < 0]
    fill_data = cut_fill_data[cut_fill_data > 0]

    # Calculate volumes
    cut_volume = np.sum(cut_data) * pixel_size**2  # Volume in cubic units (negative)
    fill_volume = np.sum(fill_data) * pixel_size**2  # Volume in cubic units

print(f"Total cut volume: {abs(cut_volume)} cubic units")
print(f"Total fill volume: {fill_volume} cubic units")
