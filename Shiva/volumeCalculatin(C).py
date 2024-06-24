import rasterio
import numpy as np
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import Polygon

class VolumeCalculationToolStandalone:
    def __init__(self):
        pass

    def calculate_volume_above_second_dem_base(self, dem_path, second_dem_path, shapefile_path, pixel_size_x, pixel_size_y):
        # Load the shapefile using geopandas
        shapefile = gpd.read_file(shapefile_path)
        shapes = [feature["geometry"] for feature in shapefile.__geo_interface__["features"]]
        
        volumes = []
        pixel_area = pixel_size_x * pixel_size_y
        
        with rasterio.open(dem_path) as src, rasterio.open(second_dem_path) as second_src:
            for shape in shapes:
                # Mask the main DEM with the current polygon
                dem_masked, _ = mask(src, [shape], crop=True, filled=True, nodata=np.nan)
                dem_masked = dem_masked[0]
                
                # Get the base level from the second DEM
                second_dem_masked, _ = mask(second_src, [shape], crop=True, filled=True, nodata=np.nan)
                second_dem_masked = second_dem_masked[0]
                
                # Calculate volume above the base level from second DEM
                base_level = np.nanmean(second_dem_masked)  # Average base level from second DEM
                
                # Set values below base_level to NaN
                dem_masked[dem_masked <= base_level] = np.nan
                
                # Calculate volume above the base level
                volume_above_base_level = np.nansum((dem_masked - base_level) * pixel_area)
                
                volumes.append(volume_above_base_level)
        
        return volumes

# Example usage
if __name__ == "__main__":
    tool = VolumeCalculationToolStandalone()
    dem_path = r"Z:\Others\Shiva\sampleDEM2.tif" # Path to your main DEM
    second_dem_path = r"C:\Users\Copy\Documents\Analytics\Tiff Files\DTmfrom earth.tif"  # Path to your second DEM as base
    shapefile_path = r"Z:\Others\Shiva\samplePolygon2.shp" # Path to your shapefile
    pixel_size_x = 0.07  # Example pixel size in x direction (meters)
    pixel_size_y = 0.07  # Example pixel size in y direction (meters)
    volumes = tool.calculate_volume_above_second_dem_base(dem_path, second_dem_path, shapefile_path, pixel_size_x, pixel_size_y)

    for i, volume in enumerate(volumes):
        print(f"Calculated Volume above second DEM base for polygon {i + 1}: {volume} m³")
