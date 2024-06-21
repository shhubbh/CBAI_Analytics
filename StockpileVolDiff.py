import Whitebox_workflows as wbw
import numpy as np
import rasterio

dem_file = "path/to/your/dem.tif"
output_difference_file = "path/to/output/difference.tif"


wbt = whitebox.WhiteboxTools()


with rasterio.open(dem_file) as dem_dataset:
    dem_data = dem_dataset.read(1)
    pixel_size = dem_dataset.transform[0] 
    nodata_value = dem_dataset.nodata

   
    ground_elevation = np.min(dem_data[dem_data != nodata_value])

   
    difference_data = dem_data - ground_elevation
    difference_data[dem_data == nodata_value] = nodata_value  

    
    profile = dem_dataset.profile
    with rasterio.open(output_difference_file, 'w', **profile) as dst:
        dst.write(difference_data, 1)


with rasterio.open(output_difference_file) as difference_dataset:
    difference_data = difference_dataset.read(1)

    
    valid_data = difference_data[difference_data != nodata_value]


    volume = np.sum(valid_data) * pixel_size**2 

print(f"Total volume of the stockpiles: {volume} cubic units")
