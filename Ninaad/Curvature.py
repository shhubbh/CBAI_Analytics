import geopandas as gpd
from shapely.geometry import LineString,Point
import numpy as np
import matplotlib.pyplot as plt
import os
import rioxarray

class ROC:
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
        coords = list(line.coords)
        Curvature=[]
        for i,(coord) in enumerate(coords):
            elevation = self.tile.sel(x=coord[0], y=coord[1], method="nearest").data
            point=Point(coord[0],coord[1],elevation)
            Curvature.append({
                        'RoadNo':j,
                        'Radius of curvature':self.radius_of_curvature(line,i),
                        'geometry':Point(point)
            })
        return Curvature

   

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
            Curvature=self.extract_along_line(i,centerline)

            clPoints = gpd.GeoDataFrame(Curvature)
            Irad=[j for j,R in enumerate(clPoints['Radius of curvature']) if R <15]
            greens=[element for element in range(len(clPoints['Radius of curvature'])) if element not in Irad]
            colorLines=self.find_consecutive_sequences(Irad)
            safe=self.find_consecutive_sequences(greens)

            for l1 in colorLines:
                geo=[(clPoints['geometry'])[index] for index in l1]
                rad=[(clPoints['Radius of curvature'])[index] for index in l1]
                curve.append({  
                                'feasible':0,
                                'centerline':i,
                                'geometry':LineString(geo),
                                'radius':rad
                })
            for l1 in safe:
                geo=[(clPoints['geometry'])[index] for index in l1]
                rad=[(clPoints['Radius of curvature'])[index] for index in l1]
                curve.append({  
                                'feasible':1,
                                'centerline':i,
                                'geometry':LineString(geo),
                                'radius':rad
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
# generator = ROC(CLDirectory,sample_tif,input_shapefile)
# generator.getLines()
