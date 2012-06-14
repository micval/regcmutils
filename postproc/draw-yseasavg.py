#!/usr/bin/env python

import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from Scientific.IO.NetCDF import NetCDFFile as ncf
from mpl_toolkits.basemap import Basemap

mpl.rcParams['font.size'] = 6.

ncvars=('t2avg','t2min','t2max','pcpavg')
inprefix='CORDEX-Africa-sec-noemiss-CRU-af'
year1=1990
year2=1990
timespan='yseasavg'
seasons = ('DJF','MAM','JJA','SON')
levels={
        'eur': {'t2avg':range(-10,11), 't2max':range(-10,11), 't2min':range(-10,11),'pcpavg':range(-10,10)},
#        'eur': {'t2avg':np.arange(-2.5,2.6,0.5), 't2max':np.arange(-2.5,2.6,0.5), 't2min':np.arange(-2.5,2.6,0.5),'pcpavg':np.arange(-5,6,0.5)},
        'ce': {'t2avg':range(-5,6), 't2max':range(-8,9), 't2min':range(-5,6),'pcpavg':range(-3,4)}
        }[sys.argv[1]]
bufferzonewidth={'ce':55,'eur':12}[sys.argv[1]]
outpostfix=sys.argv[1]
parallelsdis={'ce':5.,'eur':10}[sys.argv[1]]
meridiansdis={'ce':5.,'eur':10}[sys.argv[1]]

headerfile = ncf(sys.argv[2],'r')
xlon = headerfile.variables['lon'].getValue()
xlat = headerfile.variables['lat'].getValue()

m = Basemap(projection='cyl',llcrnrlat=xlat[0], urcrnrlat=xlat[-1], llcrnrlon=xlon[0], urcrnrlon=xlon[-1], resolution='l')
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
    fig.subplots_adjust(wspace=0.1,hspace=0.2)

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
            cmap = cm.jet_r
#            _data *= 100
        else:
            cmap = cm.jet

        plt.contourf(x,y,_data, levels=levels[v], extend='both', cmap=cmap)
#        plt.contourf(xlon,xlat,_data, levels=levels[v], extend='both', cmap=cmap)
        plt.colorbar()
        plt.title(seasons[_t])

    if year1==year2:
        timedef = '%d' % (year1,)
    else:
        timedef = '%d-%d' % (year1,year2)

    plt.suptitle('%s %s %s' % (inprefix,v,timedef))
    plt.savefig('%s-%d-%d.%s.%s.%s.png' % (inprefix, year1, year2, timespan, v, outpostfix),dpi=200, bbox_inches='tight', pad_inches=0.5)
