import rasterio
import numpy as np
import geopandas as gpd
from rasterio.mask import mask
from shapely.geometry import Polygon

class VolumeCalculationToolStandalone:
    def __init__(self):
        pass

    def calculate_volume_above_approx_base_level(self, dem_path, shapefile_path, pixel_size_x, pixel_size_y):
        # Load the shapefile using geopandas
        shapefile = gpd.read_file(shapefile_path)
        shapes = [feature["geometry"] for feature in shapefile.__geo_interface__["features"]]
        
        volumes = []
        pixel_area = pixel_size_x * pixel_size_y
        
        with rasterio.open(dem_path) as src:
            for shape in shapes:
                # Extract vertices and find average elevation
                polygon = Polygon(shape['coordinates'][0])  # Assuming the first polygon in the shape
                exterior_coords = list(polygon.exterior.coords)
                
                # Calculate average elevation of polygon vertices
                elevations = []
                for x, y in exterior_coords:
                    try:
                        value = next(src.sample([(x, y)], indexes=1))  # Get the next value from the generator
                        if not np.isnan(value):
                            elevations.append(value)
                    except StopIteration:
                        pass
                
                if elevations:
                    avg_base_level = np.mean(elevations)
                    
                    # Calculate volume above the approximate base level
                    dem_masked, _ = mask(src, [shape], crop=True, filled=True, nodata=np.nan)
                    dem_masked = dem_masked[0]
                    
                    # Set values below avg_base_level to NaN
                    dem_masked[dem_masked <= avg_base_level] = np.nan
                    
                    # Calculate volume above the approximate base level
                    volume_above_base_level = np.nansum((dem_masked - avg_base_level) * pixel_area)
                    
                    volumes.append(volume_above_base_level)
                else:
                    volumes.append(0.0)  # No valid elevation data found
        
        return volumes

# Example usage
if __name__ == "__main__":
    tool = VolumeCalculationToolStandalone()
    dem_path = r"Z:\Others\Shiva\sampleDEM2.tif"
    shapefile_path = r"Z:\Others\Shiva\samplePolygon2.shp"
    pixel_size_x = 0.07085796904697951037  # Example pixel size in x direction (meters)
    pixel_size_y = 0.07085530815116512782  # Example pixel size in y direction (meters)
    volumes = tool.calculate_volume_above_approx_base_level(dem_path, shapefile_path, pixel_size_x, pixel_size_y)

    for i, volume in enumerate(volumes):
        print(f"Calculated Volume above approximate base level for polygon {i + 1}: {volume} m³")
