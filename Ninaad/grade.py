import geopandas as gpd
from shapely.geometry import LineString,Point
import numpy as np
import matplotlib.pyplot as plt
import os
import rioxarray

class Gradient:
    def __init__(self,shapefiles_dir,sample_tif, input_shapefile, resolution=1, smoothing_factor=3, interval=10):
        self.shapefiles_dir=shapefiles_dir
        self.input_shapefile = input_shapefile
        self.sample_tif = sample_tif
        self.resolution = resolution
        self.interval = interval
        self.gdf = gpd.read_file(input_shapefile)
        self.tile = rioxarray.open_rasterio(self.sample_tif).squeeze()


    def radius_of_curvature(self,line, point_index):
        if point_index == 0 or point_index == len(line.coords) - 1:
            # print("Cannot compute curvature at the endpoints of the LineString")
            return 0
        else:
            p0 = np.array(line.coords[point_index - 1])
            p1 = np.array(line.coords[point_index])
            p2 = np.array(line.coords[point_index + 1])

            def compute_curvature(p0, p1, p2):
                # Vectors from p1 to p0 and p2
                v1 = p0 - p1
                v2 = p2 - p1
                
                # Lengths of the vectors
                a = np.linalg.norm(v1)
                b = np.linalg.norm(v2)
                c = np.linalg.norm(p2 - p0)
                
                # Area of the triangle formed by p0, p1, p2
                area = 0.5 * np.linalg.norm(np.cross(v1, v2))
                
                # Radius of the circumcircle
                if area == 0:
                    return np.inf  # Infinite radius of curvature for a straight line
                R = (a * b * c)/(4 * area)
                
                return R
            
            R = compute_curvature(p0, p1, p2)
            return R


    def extract_along_line(self,j,line):
        prev_elev = self.tile.sel(x=line.coords[0][0], y=line.coords[0][1], method="nearest").data
        gradePoints=[]
        coords = list(line.coords)
        for i in range(1, len(coords)):
            # Compute the distance from the previous point to the current point
            segment = LineString(coords[i-1:])

            point = segment.interpolate(16, normalized=False)
            elevation = self.tile.sel(x=point.x, y=point.y, method="nearest").data
            gradient = abs(elevation - prev_elev)*100/16
            pt=Point(point.x,point.y,elevation)
            prev_elev = self.tile.sel(x=segment.coords[1][0], y=segment.coords[1][1], method="nearest").data
            gradePoints.append({
                        'RoadNo':j,
                        'grade':gradient,
                        'geometry':Point(pt)
            })
        return gradePoints

   

    def getLines(self):
     
        fcl=[]
        for filename in os.listdir(self.shapefiles_dir):
            if filename.endswith(".shp"):
                shapefile_path = os.path.join(self.shapefiles_dir, filename)
                mygdf = gpd.read_file(shapefile_path)
                for line in mygdf.geometry:
                    fcl.append(line)

        curve=[]

        for i,centerline in enumerate(fcl):
            gradePoints=self.extract_along_line(i,centerline)

            clPoints = gpd.GeoDataFrame(gradePoints)
            reds=[j for j,g in enumerate(clPoints['grade']) if g >=15]
            yellows=[j for j,g in enumerate(clPoints['grade']) if g <15 and g>10]
            greens=[j for j,g in enumerate(clPoints['grade']) if g<=10]
            redLines=self.find_consecutive_sequences(reds)
            yellowLines=self.find_consecutive_sequences(yellows)
            greenLines=self.find_consecutive_sequences(greens)

            for l1 in redLines:
                geo=[(clPoints['geometry'])[index] for index in l1]
                curve.append({  
                                'grade':2,
                                'centerline':i,
                                'geometry':LineString(geo),

                })
            for l1 in yellowLines:
                geo=[(clPoints['geometry'])[index] for index in l1]

                curve.append({  
                                'grade':1,
                                'centerline':i,
                                'geometry':LineString(geo),

                })
            for l1 in greenLines:
                geo=[(clPoints['geometry'])[index] for index in l1]

                curve.append({  
                                'grade':0,
                                'centerline':i,
                                'geometry':LineString(geo),

                })


        fienCurve=gpd.GeoDataFrame(curve)
        return fienCurve
    
    def find_consecutive_sequences(self,arr):
        if not arr:
            return []

        sorted_arr = sorted(arr)
        consecutive_sequences = []
        current_sequence = [sorted_arr[0]]

        for i in range(1, len(sorted_arr)):
            if sorted_arr[i] == sorted_arr[i - 1] + 1:
                current_sequence.append(sorted_arr[i])
            else:
                if len(current_sequence) > 1:  # Only add sequences with more than one element
                    consecutive_sequences.append(current_sequence)
                current_sequence = [sorted_arr[i]]

        if len(current_sequence) > 1:  # Add the last sequence if it has more than one element
            consecutive_sequences.append(current_sequence)

        return consecutive_sequences


                

# Usage example
# sample_tif = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\HaulRoads_DEM.tif"
# input_shapefile = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\HaulRoads_SHP.shp"
# CLDirectory = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\centrelines"
# generator = Gradient(CLDirectory,sample_tif,input_shapefile)
# generator.getLines()
