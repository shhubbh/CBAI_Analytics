import pyvista as pv
import geopandas as gpd
from Normals import NormalPlotter
from Curvature import ROC
from grade import Gradient
import numpy as np
import os

def lines_from_points(points):
    """Given an array of points, make a line set"""
    poly = pv.PolyData()
    poly.points = points
    cells = np.full((len(points)-1, 3), 2)
    cells[:, 1] = np.arange(0, len(points)-1)
    cells[:, 2] = np.arange(1, len(points))
    poly.lines = cells
    return poly

currentWorkingDir="analytics" #directory of your choice

# Path to your .ply file
ply_file_path = os.path.join(currentWorkingDir,f"3d_ortho.ply")
# directory=r"C:\Users\NinaadKotasthane\Documents\Python Scripts\analytics\demdem"


def switch(key):
    dem = os.path.join(currentWorkingDir,f"HaulRoads_DEM.tif")
    haulRoads = os.path.join(currentWorkingDir,f"HaulRoads_SHP.shp")
    CLDirectory = os.path.join(currentWorkingDir,f"centrelines")
    keys={"normals":NormalPlotter(CLDirectory,dem,haulRoads),"radii":ROC(CLDirectory,dem,haulRoads),
          "grade":Gradient(CLDirectory,dem,haulRoads)}
    path=os.path.join(currentWorkingDir,f"{key}")
    try:
        lines=gpd.read_file(path)
    except:
        lines = keys[key].getLines()

        keys["normals"].saveLines(path,key,lines)
    if key=="normals":
        red,yellow,green=Normalseperator(lines,0.05,0.1,2)
    if key=="radii":
        red,yellow,green=ROCSeperator(lines)
    if key=="grade":
        red,yellow,green=gradeSeperator(lines)
    return red,yellow,green


def Normalseperator(normals,red,green,widthLimit):
    NormalData=normals[(normals['widths']>=widthLimit)]
    RedNormals=NormalData[(NormalData['slope']<green) & (NormalData['slope']>red)]
    yellowNormals=NormalData[(NormalData['slope']>0.00) & (NormalData['slope']<=red)]
    greenNormals=NormalData[(NormalData['slope']>green)]
    return RedNormals,yellowNormals,greenNormals

def ROCSeperator(lines):
    red=lines[(lines['feasible']==0)]
    safe=lines[(lines['feasible']==1)]
    return red,None,safe
    
def gradeSeperator(lines):
    green=lines[(lines['grade']==0)]
    yellow=lines[(lines['grade']==1)]
    red=lines[(lines['grade']==2)]
    return red,yellow,green

def MeshLines(lineString):
    lines=[]
    for i in range(len(lineString)):
        plot=list(lineString['geometry'].iloc[i].coords)
        lines.append(lines_from_points(np.vstack(plot)))
    return lines

red,yellow,green=switch("radii")  #change key  normals,grade,radii
redMesh=MeshLines(red)
greenMesh=MeshLines(green)
# yellowMesh=MeshLines(yellow)

mesh = pv.read(ply_file_path)
# Check if the mesh has RGB colors
if 'RGB' in mesh.point_data:
    mesh.point_data['RGB'] = mesh.point_data['RGB'] / 255.0  # Normalize RGB to [0, 1]


edges = mesh.extract_feature_edges(
    boundary_edges=False, non_manifold_edges=False, feature_angle=30, manifold_edges=False
)

pl=pv.Plotter()
pl.add_mesh(mesh, smooth_shading=True, scalars='RGB', rgb=True)
for i,cl in enumerate(redMesh):
    pl.add_mesh(mesh=cl,line_width=5, color='red')
# for i,cl in enumerate(yellowMesh):
#     pl.add_mesh(mesh=cl,line_width=5, color='yellow')
for i,cl in enumerate(greenMesh):
    pl.add_mesh(mesh=cl,line_width=5, color='green')
pl.show()

