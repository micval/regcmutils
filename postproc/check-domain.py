#!/usr/bin/env python

import sys
from os.path import splitext
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from mpl_toolkits.basemap import Basemap
from scipy.io.netcdf import netcdf_file as ncf

points = np.array([ [335.36-360, 42.24],
           [17.60, 42.24],
           [60.28, 42.24],
           [335.36-360, -1.32],
           [17.60, -1.32],
           [60.28, -1.32],
           [335.36-360, -45.76],
           [17.60, -45.76],
           [60.28, -45.76] ])

ff = ncf(sys.argv[1],'r')

try:
    lat_0 = float(ff.latitude_of_projection_origin)
    lon_0 = float(ff.longitude_of_projection_origin)
    grdis = float(ff.grid_size_in_meters)

    nx = int(ff.dimensions['jx'])
    ny = int(ff.dimensions['iy'])

    ht = ff.variables['topo'][12:-12,12:-12]
    xlat = ff.variables['xlat'][12:-12,12:-12]
    xlon = ff.variables['xlon'][12:-12,12:-12]
    lsmask = ff.variables['mask'][12:-12,12:-12]

    m = Basemap(resolution='l', projection='merc',llcrnrlat=ff.variables['xlat'][0,0],llcrnrlon=ff.variables['xlon'][0,0],
            urcrnrlat=ff.variables['xlat'][-1,-1],urcrnrlon=ff.variables['xlon'][-1,-1],lat_ts=lat_0)

    ht = np.ma.masked_array(ht, mask = np.where(lsmask>0.0,False,True))
    ocean = np.ma.masked_array(lsmask, mask = np.where(lsmask>0.0,True,False))

    m.drawcoastlines(linewidth=0.2)
    m.drawcountries(linewidth=0.4)
    m.drawmapboundary()
    m.drawparallels(np.arange(-90., 90., 10.), labels=[1,0,0,0])
    m.drawmeridians(np.arange(-180., 180., 10.), labels=[0,0,0,1])

    x,y = m(xlon,xlat)

    cm_topo = LinearSegmentedColormap('cm_topo', {
            'green': [ (0.0, 0.75, 0.75), (0.5, 0.25, 0.25), (1.0, 1.0, 1.0) ],
            'blue': [ (0.0, 0.0, 0.0), (0.5, 0.0, 0.0), (1.0, 1.0, 1.0) ],
            'red': [ (0.0, 0.0, 0.0), (0.5, 0.5, 0.5), (1.0, 1.0, 1.0) ]
        })

    cm_ocean = LinearSegmentedColormap('cm_ocean', {
            'blue': [(0.0,0.5,0.5), (1.0,1.0,1.0)],
            'green': [(0.0,0.0,0.0), (1.0,0.0,0.0)],
            'red': [(0.0,0.0,0.0), (1.0,0.0,0.0)],
        })

    m.pcolor(x,y,lsmask,cmap=cm_ocean)

    m_topo = m.pcolor(x,y,ht,cmap=cm_topo)
    plt.colorbar(m_topo)

    points_lcc = m(points[:,0], points[:,1])
    m.plot(points_lcc[0], points_lcc[1], '.r')
    plt.savefig(splitext(sys.argv[1])[0]+'.png', dpi=600)

except NameError:
    "Incorrect definitions in domain file!"
