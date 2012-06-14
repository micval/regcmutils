#!/usr/bin/env python

import sys
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import rc
import numpy as np
from Scientific.IO.NetCDF import NetCDFFile as ncf
from mpl_toolkits.basemap import Basemap

rc('font',size=9)
rc('text',usetex=True)

ncvars=('t2avg','t2min','t2max','pcpavg')
inprefix='Euro-CORDEX_STS-EOBS6'
year1=1990
year2=2008
timespan='yseasavg'
seasons = ('DJF','MAM','JJA','SON')
levels={
        'eur': {'t2avg':np.arange(-5,6,0.5), 't2max':np.arange(-5,6,0.5), 't2min':np.arange(-5,6,0.5),'pcpavg':np.arange(-5,6,0.5)},
#        'eur': {'t2avg':np.arange(-2.5,2.6,0.5), 't2max':np.arange(-2.5,2.6,0.5), 't2min':np.arange(-2.5,2.6,0.5),'pcpavg':np.arange(-5,6,0.5)},
        'ce': {'t2avg':np.arange(-5,6,0.5), 't2max':np.arange(-5,6,0.5), 't2min':np.arange(-5,6,0.5),'pcpavg':np.arange(-5,6,0.5)}
        }[sys.argv[1]]
bufferzonewidth={'ce':55,'eur':20}[sys.argv[1]]
outpostfix=sys.argv[1]
parallelsdis={'ce':5.,'eur':10}[sys.argv[1]]
meridiansdis={'ce':5.,'eur':10}[sys.argv[1]]

if year1==year2:
    headerfilename='%s.%d.%s.%s.nc' % (inprefix, year1, ncvars[0], timespan)
else:
    headerfilename='%s.%d-%d.%s.%s.nc' % (inprefix, year1, year2, ncvars[0], timespan)

ff = ncf(headerfilename,'r')

"""
xlon = headerfile.variables['longitude'].getValue()
xlat = headerfile.variables['latitude'].getValue()

m = Basemap(projection='cyl',llcrnrlat=xlat[0], urcrnrlat=xlat[-1], llcrnrlon=xlon[0], urcrnrlon=xlon[-1], resolution='l')
"""

lat_0 = float(ff.latitude_of_projection_origin)
lon_0 = float(ff.longitude_of_projection_origin)
lat_1 = float(ff.standard_parallel[0])
lat_2 = float(ff.standard_parallel[1])
grdis = float(ff.grid_size_in_meters)

nx = int(ff.dimensions['x'])
ny = int(ff.dimensions['y'])

xlat = ff.variables['xlat'][:,:]
xlon = ff.variables['xlon'][:,:]
#lsmask = ff.variables['mask'][12:-12,12:-12]

m = Basemap(width=(nx-bufferzonewidth*2)*grdis, height=(ny-bufferzonewidth*2)*grdis, resolution='l', projection='lcc', lat_0=lat_0, lon_0=lon_0, lat_1=lat_1, lat_2=lat_2)

x,y = m(xlon,xlat)

for v in ncvars:
    if year1==year2:
        infilename='%s.%d.%s.%s' % (inprefix, year1, v, timespan)
    else:
        infilename='%s.%d-%d.%s.%s' % (inprefix, year1, year2, v, timespan)
    if v == 'RT':
        infilename += '.perc.nc'
    else:
        infilename += '.nc'

    try:
        infile=ncf(infilename,'r')
        vardata=infile.variables[v]
    except:
        print >>sys.stderr, "Error opening %s file..." % (infilename,)
        raise

    fig = plt.figure()
    fig.subplots_adjust(wspace=0.001,hspace=0.15)

    for _t in range(4):
        plt.subplot(2,2,_t+1)
        m.drawcoastlines(linewidth=0.2)
        m.drawcountries(linewidth=0.2)
        m.drawmapboundary()
        m.drawparallels(np.arange(-90., 90., parallelsdis), labels=[1,0,0,0], linewidth=0.2)
        m.drawmeridians(np.arange(-180., 180., meridiansdis), labels=[0,0,0,1], linewidth=0.2)

#        mask = np.ma.mask_or(np.where(land>0,False,True),np.where(vardata[_t]<=-999.,True,False))
        mask = np.ma.masked_array(np.where(vardata[_t]<=-999.,True,False))

        if len(vardata[_t].shape)==2:
            _data = np.ma.masked_array(vardata[_t], mask=mask)
        elif len(vardata[_t].shape)==3:
            _data = np.ma.masked_array(vardata[_t,0], mask=mask)

        if v in ('tpr','pcpavg'):
            cmap = cm.RdBu
#            _data *= 100
        else:
            cmap = cm.RdBu_r

        image = plt.contourf(x,y,_data, levels=levels[v], extend='both', cmap=cmap)
#        plt.contourf(xlon,xlat,_data, levels=levels[v], extend='both', cmap=cmap)
        _datavg = np.mean(_data[bufferzonewidth:-bufferzonewidth,bufferzonewidth:-bufferzonewidth])

        plt.title(u'%s ($\phi = %.2f$)' % (seasons[_t], _datavg))

    cax = fig.add_axes([0.2, 0.0, 0.6, 0.03])
    cb = fig.colorbar(image,cax,orientation='horizontal', extend='both')

    if year1==year2:
        timedef = '%d' % (year1,)
    else:
        timedef = '%d-%d' % (year1,year2)

    plt.suptitle('%s %s %s' % (inprefix.replace('_','-'),v,timedef))
    if year1==year2:
        outfilename = '%s-%d.%s.%s.%s.png' % (inprefix, year1, timespan, v, outpostfix)
    else:
        outfilename = '%s-%d-%d.%s.%s.%s.png' % (inprefix, year1, year2, timespan, v, outpostfix)

    plt.savefig(outfilename, dpi=200, bbox_inches='tight', pad_inches=0.5)
