import os
import rioxarray
from shapely.geometry import LineString, Point
import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
from moduleCentreLine import CenterlineGenerator
import pandas as pd

class LineProfileExtractor:
    def __init__(self, sample_tif, shapefiles_dir,):
        self.sample_tif = sample_tif
        self.shapefiles_dir = shapefiles_dir
        self.tile = rioxarray.open_rasterio(self.sample_tif).squeeze()

    def extract_along_line(self, line):
        prev_elev = self.tile.sel(x=line.coords[0][0], y=line.coords[0][1], method="nearest").data
        testPoints = []
        testPoints1 = []
        testPoints2 = []
        coords = list(line.coords)
        for i in range(1, len(coords)):
            # Compute the distance from the previous point to the current point
            segment = LineString(coords[i-1:])

            point = segment.interpolate(16, normalized=False)
            value = self.tile.sel(x=point.x, y=point.y, method="nearest").data
            gradient = abs(value - prev_elev)*100/16

            # Check gradient condition
            if gradient >=15:
                testPoints.append((value,point))
            elif 10 < gradient < 15:
                testPoints1.append((value,point))
            elif 0 < gradient <=10:
                testPoints2.append((value,point))
            

            prev_elev = self.tile.sel(x=segment.coords[1][0], y=segment.coords[1][1], method="nearest").data


        test=self.checkRoad2(testPoints)
        test1=self.checkRoad2(testPoints1)
        test2=self.checkRoad2(testPoints2)

        return test,test1,test2
        
    def checkRoad2(self,points):
            try:
                markedLine=[points[0]]
                markedLines=[markedLine]

                for i in range(1,len(points)):
                    dist=points[i-1][1].distance(points[i][1])
                    # print(dist)
                    try:
                        dist2=points[i][1].distance(points[i+1][1])
                    except IndexError:
                        pass
                    if dist<=5:
                        markedLines[-1].append(points[i])
                        
                    else:
                        if dist2<5:
                            newLine=[points[i]]
                            markedLines.append(newLine)
                        
                        else:
                            pass

                return markedLines
            except IndexError:
                pass
   
    def process_shapefiles(self):
        meshR=[]
        meshY=[]
        meshG=[]
        for filename in os.listdir(self.shapefiles_dir):
            if filename.endswith(".shp"):
                shapefile_path = os.path.join(self.shapefiles_dir, filename)
                gdf = gpd.read_file(shapefile_path)
                for line in gdf.geometry:
                    if isinstance(line, LineString):
                        test,test1,test2 = self.extract_along_line(line)
                        meshR.append(test)
                        meshY.append(test1)
                        meshG.append(test2)
        return meshR,meshY,meshG


