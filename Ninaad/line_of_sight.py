import geopandas as gpd
from shapely.geometry import LineString,Point,Polygon
import numpy as np
import matplotlib.pyplot as plt
import os
import rioxarray

class LOSight:
    def __init__(self,shapefiles_dir,sample_tif, input_shapefile, resolution=1, smoothing_factor=3, interval=10):
        self.shapefiles_dir=shapefiles_dir
        self.input_shapefile = input_shapefile
        self.sample_tif = sample_tif
        self.resolution = resolution
        self.interval = interval
        self.gdf = gpd.read_file(input_shapefile)
        self.tile = rioxarray.open_rasterio(self.sample_tif).squeeze()

    def plotLines(self):
     
        fig, ax = plt.subplots(figsize=(10, 10))
        fcl=[]
        for filename in os.listdir(self.shapefiles_dir):
            if filename.endswith(".shp"):
                shapefile_path = os.path.join(self.shapefiles_dir, filename)
                mygdf = gpd.read_file(shapefile_path)
                for line in mygdf.geometry:
                    fcl.append(line)
        for i,(centerline, poly) in enumerate(zip(fcl, self.gdf.geometry)):
            gpd.GeoSeries([poly.exterior]).plot(ax=ax, linewidth=1, color='black')
            gpd.GeoSeries([centerline]).plot(ax=ax, linewidth=1, color='blue')
            obstruction,sightLines=self.lineOfSight(poly,centerline,20)
            for los in obstruction:
                gpd.GeoSeries([los]).plot(ax=ax, linewidth=0.6, color='red')
            for los in sightLines:
                gpd.GeoSeries([los]).plot(ax=ax, linewidth=0.6, color='green')
 


        plt.title("Polygons and Generated Centerlines")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")
        plt.show()

    def lineOfSight(self,polygon,centerline,ssd):
        coords = list(centerline.coords)
        sightLines=[]
        obstruction=[]
        for i in range(1, len(coords)):
            try:
                # Compute the distance from the previous point to the current point
                segment = LineString(coords[3*i:])

                point = segment.interpolate(ssd, normalized=False)
                los=LineString([Point(list(segment.coords)[0]),point])
                if los.intersects(polygon.boundary):
                    obstruction.append(self.losLoss(polygon,segment,ssd,los))
                else:
                    sightLines.append(los)
            except IndexError:
                pass

        return obstruction,sightLines

    def losLoss(self,polygon,segment,ssd,los):
        if los.intersects(polygon.boundary):
            ssd-=0.1
            point = segment.interpolate(ssd, normalized=False)
            los=LineString([Point(list(segment.coords)[0]),point])
            return self.losLoss(polygon,segment,ssd,los)
        else:
            return los

    def extractElevation(self,line):
        ithNormalPoints = []
        coords = list(line.coords)

        for i,(coord) in enumerate(coords):
            elevation = self.tile.sel(x=coord[0], y=coord[1], method="nearest").data
            point=Point(coord[0],coord[1],elevation)
            ithNormalPoints.append(point)

        return LineString(ithNormalPoints)

    def toPyvista(self):
        fcl=[]
        for filename in os.listdir(self.shapefiles_dir):
            if filename.endswith(".shp"):
                shapefile_path = os.path.join(self.shapefiles_dir, filename)
                mygdf = gpd.read_file(shapefile_path)
                for line in mygdf.geometry:
                    fcl.append(self.extractElevation(line))
        return fcl
    


# Usage example
sample_tif = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\HaulRoads_DEM.tif"
input_shapefile = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\HaulRoads_SHP.shp"
CLDirectory = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\centrelines"
generator = LOSight(CLDirectory,sample_tif,input_shapefile)
generator.plotLines()
# generator.toPyvista()
