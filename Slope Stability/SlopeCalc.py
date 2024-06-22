import rasterio
import numpy as np
#import folium
#from folium.plugins import HeatMapWithTime
from tqdm import tqdm
import pandas as pd

def read_dem(file_path):
  
    with rasterio.open(file_path) as src:
        dem = src.read(1)  # Read the first band (assuming it's a single-band DEM)
        transform = src.transform  # Get the affine transformation matrix
        crs = src.crs  # Get the coordinate reference system
    return dem, transform, crs

def calculate_fos(elevation, water_table, cohesion, phi, unit_weight, slope_angle):
    
    # Convert angles from degrees to radians
    phi = np.radians(phi)
    slope_angle = np.radians(slope_angle)
    
    # Effective normal stress
    if elevation < water_table:
        effective_normal_stress = unit_weight * (water_table - elevation)
    else:
        effective_normal_stress = unit_weight * (elevation - water_table)
    
    # Shear strength (Mohr-Coulomb)
    shear_strength = cohesion + effective_normal_stress * np.tan(phi)
    
    # Driving force and resisting force components
    slice_weight = unit_weight * elevation
    driving_force = slice_weight * np.sin(slope_angle)
    resisting_force = shear_strength * elevation
    
    # Factor of Safety (FOS)
    fos = resisting_force / driving_force if driving_force != 0 else np.inf
    
    return fos

def compute_fos_map(dem, water_table, cohesion, phi, unit_weight, slope_angle):
    
    fos_map = np.zeros_like(dem, dtype=float)
    
    for i in tqdm(range(dem.shape[0])):
        for j in range(dem.shape[1]):
            elevation = dem[i, j]
            fos_map[i, j] = calculate_fos(elevation, water_table, cohesion, phi, unit_weight, slope_angle)
    
    return fos_map

def plot_interactive_heatmap_folium(dem, fos_map, transform):
   
    # Create a folium map centered at the middle of the DEM extent
    center_lat = transform[5] + dem.shape[0] * transform[4] / 2
    center_lon = transform[2] + dem.shape[1] * transform[0] / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles='Stamen Terrain')

    # Convert numpy array to list of lists format needed for HeatMapWithGradient
    data = []
    for i in tqdm(range(dem.shape[0])):
        for j in range(dem.shape[1]):
            lon, lat = transform * (j, i)  # Convert pixel coordinates to geographic coordinates
            data.append([lat, lon, fos_map[i, j]])  # Add lat, lon, and FOS value to data list

    # Add HeatMapWithGradient layer to the map
    folium.TileLayer('cartodbpositron').add_to(m)  # Add basemap
    HeatMapWithTime(data).add_to(m)

    # Save the map as an HTML file
    m.save('fos_heatmap.html')

# Example usage
if __name__ == '__main__':
    # Example parameters
    file_path = "Z:\Others\Shiva\small.tif"
    water_table = 5  # Depth of water table (m)
    cohesion = 10  # kPa
    phi = 30  # degrees
    unit_weight = 18  # kN/m³
    slope_angle = 45  # degrees
    
    
    # Read DEM data
    dem, transform, crs = read_dem(file_path)
    
    # Compute Factor of Safety (FOS) map
    fos_map = compute_fos_map(dem, water_table, cohesion, phi, unit_weight, slope_angle)
    df = pd.DataFrame(fos_map)
    df.to_csv(r"C:\Users\Copy\Documents\Analytics\saved_fos_map.csv", header=False, index=False)
    
    # Plot interactive heatmap using folium
    #plot_interactive_heatmap_folium(dem, fos_map, transform)
