import geopandas as gpd
from shapely.geometry import LineString,Point
import numpy as np
import matplotlib.pyplot as plt
import os
import rioxarray

class NormalPlotter:
    def __init__(self,shapefiles_dir,dem, haulRoads, resolution=1, smoothing_factor=3, interval=5):
        self.shapefiles_dir=shapefiles_dir
        self.haulRoads = haulRoads
        self.dem = dem
        self.resolution = resolution
        self.interval = interval
        self.gdf = gpd.read_file(haulRoads)
        self.tile = rioxarray.open_rasterio(self.dem).squeeze()


    def extend_normal(self, normal_line, polygon):
        extended_line = normal_line
        if polygon.contains(normal_line):
            direction_vector = normal_line.coords[1][0] - normal_line.coords[0][0], normal_line.coords[1][1] - normal_line.coords[0][1]
            step_size = 0.1
            
            while polygon.contains(extended_line):
                extended_line = LineString([(extended_line.coords[0][0] - direction_vector[0] * step_size, extended_line.coords[0][1] - direction_vector[1] * step_size),
                                            (extended_line.coords[1][0] + direction_vector[0] * step_size, extended_line.coords[1][1] + direction_vector[1] * step_size)])
            
            return extended_line
        else:
            return normal_line

    def generate_normals_extended(self, centerline, polygon):
        normals = []
        normal_lengths = []
        for i in range(0, len(centerline.coords) - 1, self.interval):
            p1 = Point(centerline.coords[i])
            p2 = Point(centerline.coords[i+1])
            dx = p2.x - p1.x
            dy = p2.y - p1.y
            length = np.sqrt(dx**2 + dy**2)
            nx = -dy / length
            ny = dx / length
            
            normal_length = 0
            for dist in np.arange(0.1, length, 0.1):
                n1 = Point(p1.x + nx * dist, p1.y + ny * dist)
                n2 = Point(p1.x - nx * dist, p1.y - ny * dist)
                if polygon.contains(n1):
                    normal_length = dist
                if polygon.contains(n2):
                    normal_length = dist
            
            if normal_length > 0:
                normal_line = LineString([Point(p1.x + nx * normal_length, p1.y + ny * normal_length), Point(p1.x - nx * normal_length, p1.y - ny * normal_length)])
                extended_normal = self.extend_normal(normal_line, polygon)
                normals.append(extended_normal)
                normal_lengths.append(extended_normal.length)
        
        return normals, normal_lengths

    def extract_along_line(self, line,length):
        ithNormalPoints = []
        coords = list(line.coords)
        elevs=[]
        for coord in coords:
            elevation = self.tile.sel(x=coord[0], y=coord[1], method="nearest").data
            elevs.append(elevation)
            point=Point(coord[0],coord[1],elevation)
            ithNormalPoints.append(point)
        max_index = elevs.index(max(elevs))  # Get the index of the maximum value
        gradient=(max(elevs)-min(elevs))/length
        return LineString(ithNormalPoints),gradient,max_index

   

    def getLines(self):
        centerlines=[]
        Linedata=[]
        for filename in os.listdir(self.shapefiles_dir):
            if filename.endswith(".shp"):
                shapefile_path = os.path.join(self.shapefiles_dir, filename)
                mygdf = gpd.read_file(shapefile_path)
                for line in mygdf.geometry:
                    centerlines.append(line)

        for i,(centerline, poly) in enumerate(zip(centerlines, self.gdf.geometry)):
            normals, normal_lengths = self.generate_normals_extended(centerline, poly)
            for normal,Lengths in zip(normals,normal_lengths):
                # IthCenterline.append(self.extract_along_line(normal))
                IthCenterline,gradient,higherPt=self.extract_along_line(normal,Lengths)
                Linedata.append({
                                'widths': Lengths,
                                'direction':higherPt,
                                'RoadNo':i,
                                'slope':gradient,
                                'geometry': LineString(IthCenterline)
                                })

        normals3D = gpd.GeoDataFrame(Linedata)

        return normals3D

    def saveLines(self,output_directory,name,lines):
        os.makedirs(output_directory, exist_ok=True)
        for i, centerline in enumerate(lines):
            output_shapefile = os.path.join(output_directory, f"{name}_{i}.shp")
            lines.to_file(output_shapefile)
            print(f"{name} {i} has been saved to {output_shapefile}")


# Usage example
# dem = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\HaulRoads_DEM.tif"
# haulRoads = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\HaulRoads_SHP.shp"
# CLDirectory = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\centrelines"
# generator = NormalPlotter(CLDirectory,dem,haulRoads)
# generator.getLines()
