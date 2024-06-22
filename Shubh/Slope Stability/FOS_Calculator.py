import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from DEM_Loader import dataset
 
x = dataset.read(1)
y = dataset.read(1)
x, y = np.meshgrid(x, y)
z = np.sin(x / 2) * np.cos(y / 2) * 10 

# Step 2: Define slip surface geometry (e.g., ellipsoid)
L1 = 8  # Major axis length
L2 = 6  # Minor axis length
L3 = L1  # Vertical axis length
xc = 0  # Center x-coordinate
yc = 0  # Center y-coordinate
zc = 8  # Center z-coordinate
 
def z_el(x, y):
    return np.array([-1, 1])[:, None, None] * (L3 * np.sqrt(1 - ((x - xc) ** 2 / L1 ** 2) - ((y - yc) ** 2 / L2 ** 2))) + zc
 
# Step 3: Determine intersection with topography
zTopography = griddata((x.flatten(), y.flatten()), z.flatten(), (x, y), method='linear')
zEllipsoid = z_el(x, y)
intersection = (zTopography >= np.min(zEllipsoid)) & (zTopography <= np.max(zEllipsoid))
 
# Step 4: Define soil parameters
c = 25  # Cohesion (kPa)
phi = 30  # Internal friction angle (degrees)
gamma = 18  # Unit weight (kN/m^3)
 
# Step 5: Slope stability analysis (simplified)
slopeAngle = np.degrees(np.arctan(np.gradient(zTopography)[0] / np.gradient(x)[0]))  # Slope angle calculation
tanPhi = np.tan(np.radians(phi))
 
FoS = np.full_like(zTopography, np.nan)
