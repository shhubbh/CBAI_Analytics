import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal, osr
from skimage import feature
from PIL import Image
import cv2
import geopandas as gpd
from shapely.geometry import LineString
from skimage import measure
import os
from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
import sys

# Supply path to qgis install location (update this path if necessary)
qgis_path = r"C:\Program Files\QGIS 3.38.1\apps\qgis"
QgsApplication.setPrefixPath(qgis_path, True)

# Create a reference to the QgsApplication
qgs = QgsApplication([], False)

# Load providers
qgs.initQgis()

# Add the path to Processing framework
sys.path.append(os.path.join(qgis_path, 'python', 'plugins'))

# Import and initialize Processing
import processing
from processing.core.Processing import Processing
Processing.initialize()

QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

print("QGIS version:", Qgis.QGIS_VERSION)
print("Processing algorithms:", len(QgsApplication.processingRegistry().algorithms()))

# Check if the algorithm exists and print its parameters
alg = QgsApplication.processingRegistry().algorithmById('native:dtmslopebasedfilter')
if alg:
    print("Algorithm found. Parameters:")
    for param in alg.parameterDefinitions():
        print(f"- {param.name()}: {param.description()}")
else:
    print("Algorithm 'native:dtmslopebasedfilter' not found")

try:
    # Create a QgsRasterLayer for input
    input_path = r"C:\Users\Copy\Desktop\koustav\Analytics Data\Analytics Data\DEM\DEM.tif"
    input_raster = QgsRasterLayer(input_path, 'input')
    if not input_raster.isValid():
        raise Exception("Invalid input raster")

    # Print debug information about the input raster
    print("Input raster info:")
    print(f"- Is valid: {input_raster.isValid()}")
    print(f"- CRS: {input_raster.crs().authid()}")
    print(f"- Width: {input_raster.width()}")
    print(f"- Height: {input_raster.height()}")
    print(f"- Bands: {input_raster.bandCount()}")

    # Specify output file paths
    output_ground_path = r'C:\Users\Copy\Desktop\files_kp\DATA\edge detection - toe+crest\DEM1\temp\hillshade.tif'

    # Create a feedback object
    feedback = QgsProcessingFeedback()

    # Run the algorithm
    result = processing.run("native:hillshade", {
        'INPUT':input_raster,
        'Z_FACTOR':1,
        'AZIMUTH':300,
        'V_ANGLE':40,
        'OUTPUT':output_ground_path
    }, feedback=feedback)

    print("DTM Filter Algorithm executed. Result:", result)

except Exception as e:
    print("Error executing algorithm:", str(e))
    import traceback
    print(traceback.format_exc())

# File path for the input .tif file (replace with your path)
input_path = r'C:\Users\Copy\Desktop\files_kp\DATA\edge detection - toe+crest\DEM1\temp\hillshade.tif'

# Check if the file exists
if not os.path.exists(input_path):
    print(f"Error: The file {input_path} does not exist.")
    exit()

# Load the input image using GDAL
dataset = gdal.Open(input_path)
if dataset is None:
    print(f"Error: Unable to open the file {input_path}. It may not be a valid GDAL dataset.")
    exit()

try:
    input_image = dataset.ReadAsArray()
except Exception as e:
    print(f"Error reading the dataset: {str(e)}")
    exit()

# Get the geotransform and projection
geotransform = dataset.GetGeoTransform()
projection = dataset.GetProjection()

# Create a spatial reference object
srs = osr.SpatialReference(wkt=projection)

# Apply Bilateral filter for edge-preserving smoothing using OpenCV
blurred = cv2.bilateralFilter(input_image.astype(np.float32), d=27, sigmaColor=95, sigmaSpace=95)

# v=np.median(blurred)
# # sigma=27
# l=int(max(0,(1.0-27)*v))
# u=int(max(255,(1.0+27)*v))
# print(l,u)

# Apply Canny edge detection (adjusted parameters for open pit mine) low=0.05 high=0.2
edges = feature.canny(blurred, sigma=50, low_threshold=0.05, high_threshold=0.2)

# Convert edges to vector contours
contours = measure.find_contours(edges, level=0.5)

# Function to convert pixel coordinates to georeferenced coordinates
def pixel_to_geo(x, y, geotransform):
    geo_x = geotransform[0] + x * geotransform[1] + y * geotransform[2]
    geo_y = geotransform[3] + x * geotransform[4] + y * geotransform[5]
    return geo_x, geo_y

# Convert the contours into shapely LineStrings with correct coordinates
line_strings = []
for contour in contours:
    if len(contour) > 1:
        geo_coords = [pixel_to_geo(x, y, geotransform) for y, x in contour]
        line_strings.append(LineString(geo_coords))

# Create a GeoDataFrame to store the line strings
gdf = gpd.GeoDataFrame(geometry=line_strings, crs=srs.ExportToProj4())

# Save the contours as a shapefile
shapefile_output_path = r"C:\Users\Copy\Desktop\files_kp\DATA\edge detection - toe+crest\DEM1\temp\edges.shp"
gdf.to_file(shapefile_output_path)

# # Create a new raster for the edge detection result
# driver = gdal.GetDriverByName('GTiff')
# edge_dataset = driver.Create(r"C:\Users\Copy\Desktop\files_kp\DATA\edge detection - toe+crest\DEM1\temp\edges.tif", 
#                              dataset.RasterXSize, dataset.RasterYSize, 1, gdal.GDT_Byte)
# edge_dataset.SetGeoTransform(geotransform)
# edge_dataset.SetProjection(projection)

# # Write the edge detection result to the new raster
# edge_dataset.GetRasterBand(1).WriteArray((edges * 255).astype(np.uint8))
# edge_dataset.FlushCache()

# # Plot the filtered image and the Canny edge detection output
# fig, ax = plt.subplots(1, 2, figsize=(12, 8))

# # Display the Bilateral filtered image
# ax[0].imshow(blurred, cmap='gray')
# ax[0].set_title('Bilateral Filtered Image')
# ax[0].axis('off')

# # Display the Canny edge detection result
# ax[1].imshow(edges, cmap='gray')
# ax[1].set_title('Canny Edge Detection (Open Pit Mine)')
# ax[1].axis('off')

# plt.show()

# Close datasets
dataset = None
edge_dataset = None