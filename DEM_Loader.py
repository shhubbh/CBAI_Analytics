#loads DEM and pre-processes it
import rasterio
from rasterio.plot import show
import numpy as np
import matplotlib.pyplot as plt
  

dem_path = "C:\\Users\\shubh\\Desktop\\small.tif"
 

with rasterio.open(dem_path) as src:
    dem_data = src.read(1)  # Read the first band
    profile = src.profile  # Get metadata
 

print(f"DEM profile: {profile}")
print(f"DEM shape: {dem_data.shape}")

dataset = rasterio.open(r"C:\\Users\\shubh\\Desktop\\small.tif")


#plt.figure(figsize=(10, 8))
#plt.imshow(dem_data, cmap='terrain')
#plt.colorbar(label='Elevation (meters)')
#plt.title('Digital Elevation Model (DEM)')
#plt.xlabel('X Coordinate')
#plt.ylabel('Y Coordinate')
#plt.show()
