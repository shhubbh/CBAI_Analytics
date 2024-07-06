
import geopandas as gpd
from shapely.geometry import LineString, Polygon, MultiLineString
from shapely.ops import linemerge
from shapely.validation import make_valid
from skimage.morphology import skeletonize, thin
from scipy.ndimage import gaussian_filter
import sknw
import numpy as np
import rasterio
from rasterio.features import rasterize
import matplotlib.pyplot as plt
import os

class CenterlineGenerator:
    def __init__(self, input_shapefile, resolution=1, smoothing_factor=3):
        self.input_shapefile = input_shapefile
        self.resolution = resolution
        self.smoothing_factor = smoothing_factor
        self.gdf = gpd.read_file(input_shapefile)
        self.final_centerlines = []
        self.process_polygons()

    def merge_lines(self, lines):
        merged = linemerge(lines)
        if isinstance(merged, LineString):
            return [merged]
        elif isinstance(merged, MultiLineString):
            return list(merged.geoms)
        return []

    def smooth_line(self, line):
        x, y = line.xy
        x = gaussian_filter(x, self.smoothing_factor)
        y = gaussian_filter(y, self.smoothing_factor)
        return LineString(np.column_stack([x, y]))

    def get_centerline(self, polygon):
        bounds = polygon.bounds
        transform = rasterio.transform.from_bounds(*bounds, int((bounds[2]-bounds[0])/self.resolution), int((bounds[3]-bounds[1])/self.resolution))
        binary_image = rasterize([polygon], out_shape=(int((bounds[3]-bounds[1])/self.resolution), int((bounds[2]-bounds[0])/self.resolution)), transform=transform, fill=0, all_touched=True)

        binary_image = gaussian_filter(binary_image.astype(float), sigma=1)
        binary_image = (binary_image > 0.5).astype(np.uint8)
        skeleton = thin(binary_image)

        graph = sknw.build_sknw(skeleton)
        
        lines = []
        for (s, e) in graph.edges():
            ps = graph[s][e]['pts']
            coords = [(p[1] * self.resolution + bounds[0], (binary_image.shape[0] - p[0]) * self.resolution + bounds[1]) for p in ps]
            line = LineString(coords)
            lines.append(line)
        
        return lines

    def process_polygons(self):
        for poly in self.gdf.geometry:
            if isinstance(poly, Polygon):
                initial_lines = self.get_centerline(poly)
                merged_initial_lines = self.merge_lines(initial_lines)
                valid_centerlines = [make_valid(line) for line in merged_initial_lines]
                smoothed_centerlines = [self.smooth_line(line) for line in valid_centerlines]
                self.final_centerlines.extend(smoothed_centerlines)
            else:
                print(f"Non-polygon geometry found: {type(poly)}. Skipping...")

    def get_centerline_by_index(self, index):
        if index < 0 or index >= len(self.final_centerlines):
            raise IndexError("Index out of range")
        return self.final_centerlines[index]

    def save_centerlines(self, output_directory):
        os.makedirs(output_directory, exist_ok=True)
        for i, centerline in enumerate(self.final_centerlines):
            centerline_gdf = gpd.GeoDataFrame(geometry=[centerline], crs=self.gdf.crs)
            output_shapefile = os.path.join(output_directory, f"centerline_{i}.shp")
            centerline_gdf.to_file(output_shapefile)
            print(f"Centerline {i} has been saved to {output_shapefile}")

    def plot_centerlines(self,ax):
        # fig, ax = plt.subplots(figsize=(10, 10))
        self.gdf.boundary.plot(ax=ax, linewidth=1, edgecolor='blue')
        for centerline in self.final_centerlines:
            gpd.GeoSeries([centerline]).plot(ax=ax, linewidth=0.2, color='black')
        # plt.title("Polygons and Generated Centerlines")
        # plt.xlabel("Longitude")
        # plt.ylabel("Latitude")
        # plt.show()


    def gradientFlag(self):
        # coords=np.array(self.final_centerlines[0].coords)
        point = self.final_centerlines[0].interpolate(16, normalized=False)
        print(point)
        highGradient=LineString(self.final_centerlines[0].coords[500:700])
        gpd.GeoSeries([highGradient]).plot(ax=self.ax, linewidth=2, color='yellow')
    
        

if __name__ == "__main__":
    input_shapefile = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\HaulRoads_SHP.shp"
    output_directory = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\centrelines"

    generator = CenterlineGenerator(input_shapefile)
    # generator.save_centerlines(output_directory)
    generator.plot_centerlines()
    generator.gradientFlag()
