import geopandas as gpd
import pyvista as pv
import numpy as np
import rasterio
from inputToVisual import LineProfileExtractor
from moduleCentreLine import CenterlineGenerator
# from pyvista.utilities import lines_from_points

sample_tif = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\HaulRoads_DEM.tif"
shapefiles_dir = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\centrelines"
input_shapefile = r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\HaulRoads_SHP.shp"

extractor = LineProfileExtractor(sample_tif, shapefiles_dir)
generator = CenterlineGenerator(input_shapefile)
red,yellow,green=extractor.process_shapefiles()

def lines_from_points(points):
    """Given an array of points, make a line set"""
    poly = pv.PolyData()
    poly.points = points
    cells = np.full((len(points)-1, 3), 2)
    cells[:, 1] = np.arange(0, len(points)-1)
    cells[:, 2] = np.arange(1, len(points))
    poly.lines = cells
    return poly

def compilePts(grade):
    grades=[]
    for line in grade:
        if line==None:
            pass
        else:
            for segment in line:
                seg=[]
                for i in range(len(segment)):
                    point=[segment[i][1].x,segment[i][1].y,segment[i][0]]
                    seg.append(point)
                lines=lines_from_points(np.vstack(seg))
                # tube = lines.tube(1).elevation()
                grades.append(lines)


    return grades
     
Red=compilePts(red)
Yellow=compilePts(yellow)
Green=compilePts(green)

plotter = pv.Plotter()

# Path to your .ply file
ply_file_path = r'C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\3d_ortho.ply'

# Read the .ply file
mesh = pv.read(ply_file_path)

# Check if the mesh has RGB colors
if 'RGB' in mesh.point_data:
    mesh.point_data['RGB'] = mesh.point_data['RGB'] / 255.0  # Normalize RGB to [0, 1]

# Smooth the mesh
# smoothed_mesh = mesh.smooth(n_iter=5000, relaxation_factor=0.1)
# smoothed_mesh = mesh.plot(smooth_shading=True, scalars='RGB', rgb=True)
edges = mesh.extract_feature_edges(
    boundary_edges=False, non_manifold_edges=False, feature_angle=30, manifold_edges=False
)

plotter.add_mesh(mesh=mesh, cmap='gist_earth')
for r in Red:
    plotter.add_mesh(mesh=r,line_width=8, color='red')
for y in Yellow:
    plotter.add_mesh(mesh=y,line_width=8, color='yellow')
for g in Green:
    plotter.add_mesh(mesh=g,line_width=8, color='blue')


# plotter.camera_position =[(900000.285811675846, 240000.1397046051004, 1155.542325449192),
#                     (577.9371599370799, 495.3480261506809, 381.7124055285182),
#                     (0.17313457304419916, 0.27814381639313923, 0.9448070898437746)]

plotter.set_background('white')
plotter.show_grid(color='gray')
plotter.show()
