import rasterio
import numpy as np
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import Polygon

class VolumeCalculationToolStandalone:
    def __init__(self):
        pass

    def calculate_volume_above_manual_base(self, dem_path, shapefile_path, pixel_size_x, pixel_size_y, manual_base_level):
        # Load the shapefile using geopandas
        shapefile = gpd.read_file(shapefile_path)
        shapes = [feature["geometry"] for feature in shapefile.__geo_interface__["features"]]
        
        volumes = []
        pixel_area = pixel_size_x * pixel_size_y
        
        with rasterio.open(dem_path) as src:
            for shape in shapes:
                # Mask the main DEM with the current polygon
                dem_masked, _ = mask(src, [shape], crop=True, filled=True, nodata=np.nan)
                dem_masked = dem_masked[0]
                
                # Manually set base level
                base_level = manual_base_level
                
                # Set values below base_level to NaN
                dem_masked[dem_masked <= base_level] = np.nan
                
                # Calculate volume above the base level
                volume_above_base_level = np.nansum((dem_masked - base_level) * pixel_area)
                
                volumes.append(volume_above_base_level)
        
        return volumes

# Example usage
if __name__ == "__main__":
    tool = VolumeCalculationToolStandalone()
    dem_path = r"Z:\Others\Shiva\sampleDEM2.tif"  # Path to your main DEM
    shapefile_path = r"Z:\Others\Shiva\samplePolygon2.shp"  # Path to your shapefile
    pixel_size_x = 0.07  # Example pixel size in x direction (meters)
    pixel_size_y = 0.07  # Example pixel size in y direction (meters)
    manual_base_level = 100.0  # Manually specified base level in meters

    volumes = tool.calculate_volume_above_manual_base(dem_path, shapefile_path, pixel_size_x, pixel_size_y, manual_base_level)

    for i, volume in enumerate(volumes):
        print(f"Calculated Volume above manual base level for polygon {i + 1}: {volume} m³")
