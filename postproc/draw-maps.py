#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from os.path import isfile

from optparse import OptionParser

import matplotlib.pyplot as plt
import matplotlib.colors as colors
from matplotlib import cm
from netCDF4 import Dataset as ncf
from mpl_toolkits.basemap import Basemap
import numpy as np
from netCDF4 import num2date

from pputils import get_season_name_by_month

parser = OptionParser(usage='Usage: %prog [ options ] data_file output_prefix')
parser.add_option('--bgimage', dest='bgimage', help='background image (topography)')
parser.add_option('--bzwidth', dest='bufferzone', type='int', help='buffer zone width')
parser.add_option('--domain', dest='show_domain', help='display domain')
parser.add_option('--alpha', dest='data_alpha', type='float', help='data display alpha')
parser.add_option('--gridfile', dest='gridfilename', help='grid file')
parser.add_option('--lon', dest='longitude_name', help='name of longitude variable')
parser.add_option('--lat', dest='latitude_name', help='name of latitude variable')
parser.add_option('-d','--deaccumulate', dest='deaccumulate', type='int', help='deaccumulate step (0=no deaccumulation)')
parser.add_option('-n','--normalize', dest='normalize', action='store_true', help='')
parser.add_option('-l','--lognormalize', dest='lognormalize', action='store_true', help='')
parser.add_option('--min', dest='minimum', type='float', help='min level')
parser.add_option('--max', dest='maximum', type='float', help='max level')
parser.add_option('--nmin', dest='norm_minimum', type='float', help='normalization min')
parser.add_option('--nmax', dest='norm_maximum', type='float', help='normalization max')
parser.add_option('--step', dest='step', type='float', help='level step')
parser.add_option('--levels', dest='levels', help='list of levels')
parser.add_option('-t','--type',dest='type', help='analysis type (daily, sum, ts')
parser.add_option('-s','--timestep',dest='timestep', help='timestep to show', type='int')
parser.add_option('--units', dest='units', help='units')
parser.add_option('--desc',dest='description', help='experiment description')
parser.add_option('-v','--varname',dest='varname', help='Variable name')
parser.add_option('--multiplicator',dest='multiplicator', help='Multiplicator', type='float')
parser.add_option('--zlevel',dest='zlevel', help='Z-level', type='int')
parser.add_option('','--labelbyseasons', dest='labelbyseasons', action='store_true', help='', default=False)
parser.add_option('','--labelbytime', action='store_true', help='', default=False)
parser.add_option('','--cmap', dest='cmap', help='Color Map', default='bwr')
parser.add_option('','--colorbar', dest='colorbar', help='Color bar type (vertical | horizontal | none)', default='horizontal')
parser.add_option('','--reversecmap', dest='reversecmap', action='store_true', help='', default=False)
parser.add_option('','--extend', help='Extend: min | max | both ', default='neither')
parser.add_option('','--dpi', help='DPI', type='int')
parser.add_option('','--drawfunction', help='Draw function: default %default')
parser.add_option('','--maskoceans', action='store_true', help='Mask oceans', default=False)

parser.set_defaults(
        bgimage='color_etopo1_ice_low.tif',
        bufferzone=0,
        type='ts',
        data_alpha=0.9,
        show_domain='full',
        longitude_name='lon',
        latitude_name='lat',
        minimum=20,
        maximum=300,
        norm_minimum=-200,
        norm_maximum=300,
        levels=None,
        step=20,
        normalize=False,
        lognormalize=False,
        deaccumulate=0,
        description='',
        units='mm/den',
        varname=None,
        multiplicator=1,
        timestep=None,
        zlevel=0,
        dpi=300,
        drawfunction='contourf',
        )

(options, args) = parser.parse_args()

if len(args)<2:
    parser.print_help()
    raise SystemExit

bufferzone=options.bufferzone

fh = ncf(args[0],'r')
if options.gridfilename is not None:
    gridfh = ncf(options.gridfilename,'r')
else:
    gridfh = fh

if bufferzone>0:
    mbufferzone=-bufferzone
else:
    mbufferzone=None

if len(gridfh.variables[options.longitude_name].shape)==3:
    lon = gridfh.variables[options.longitude_name][0][bufferzone:mbufferzone,bufferzone:mbufferzone]
    lat = gridfh.variables[options.latitude_name][0][bufferzone:mbufferzone,bufferzone:mbufferzone]
elif len(gridfh.variables[options.longitude_name].shape)==1:
    lon,lat = np.meshgrid(gridfh.variables[options.longitude_name][:], gridfh.variables[options.latitude_name][:])
else:
    lon = gridfh.variables[options.longitude_name][bufferzone:mbufferzone,bufferzone:mbufferzone]
    lat = gridfh.variables[options.latitude_name][bufferzone:mbufferzone,bufferzone:mbufferzone]

if options.levels is not None:
    levels_ts = [float(i) for i in options.levels.split(',')]
else:
    levels_ts = np.arange(options.minimum, options.maximum+options.step, options.step)

levels_sum = {'CR':(20,50,100,150,200,250,300,350), # (20,40,60,80,100,120,140,160),
        'CE': (0,50,100,200,300,400,500,600,700),
        'CE2': (0,1, 20, 50, 80, 120, 160, 200, 240, 300),
        'full': (0,50,100,200,300,400,500,600,700),
        'full2': (20,50,100,150,200,250,300,350),
        }
colors_sum = {'CR': ('#bbffbb','#99ff99','#00ff00','#00ffff','#00ccff','#3333ff','#0000cc','#000033'),
        'CE': ('#ffffff','#bbffbb','#99ff99','#00ff00','#00ffff','#00ccff','#3333ff','#0000cc','#000033'),
        'CE2': ('#ffffff','#fffada','#fff9ad','#ffc5c1','#a5ffa8','#01f702','#006500','#383aff','#05295b'),
        'full': ('#ffffff','#bbffbb','#99ff99','#00ff00','#00ffff','#00ccff','#3333ff','#0000cc','#000033'),
        'full2': ('#ffffff','#bbffbb','#99ff99','#00ff00','#00ffff','#00ccff','#3333ff','#0000cc','#000033'),
        }

if options.data_alpha==1.0:
    zorder=None
else:
    zorder=2

if len(fh.variables[options.varname].shape)==4:
    if options.bufferzone:
        vardata = fh.variables[options.varname][:,options.zlevel,bufferzone:-bufferzone,bufferzone:-bufferzone]
    else:
        vardata = fh.variables[options.varname][:,options.zlevel]
elif len(fh.variables[options.varname].shape)==3:
    if options.bufferzone:
        vardata = fh.variables[options.varname][:,bufferzone:-bufferzone,bufferzone:-bufferzone]
    else:
        vardata = fh.variables[options.varname][:]

vardata *= options.multiplicator

"""
try:
    if fh.variables[options.varname].units=='kg m-2 s-1' and options.multiplicator==1:
        vardata *= 86400
except:
    pass
"""

times = num2date(fh.variables['time'][:], fh.variables['time'].units, fh.variables['time'].calendar)
if options.timestep is not None:
    print "Timestep requested: %d" % options.timestep
    time1 = options.timestep
    time2 = time1+1
else:
    time1 = 0
    time2 = times.shape[0]

counter = 0
for t in range(time1,time2):
    (Y,mon,d) = times[t].year,times[t].month,times[t].day
    (hh,mm,ss) = times[t].hour, times[t].minute, times[t].second
    print "Processing timestep %d, %4d-%02d-%02d %02d:%02d" % (t, Y, mon, d, hh, mm)
    plt.figure(figsize=(10.24,7.68), dpi=options.dpi)
    if options.show_domain=='CR':
        m = Basemap(width=500000, height=300000, resolution='i', projection='lcc', lat_0=49.8, lon_0=15.5, lat_1=46., lat_2=52., ax=plt.gca())
    elif options.show_domain in ('CE', 'CE2'):
        m = Basemap(width=1600000, height=1400000, resolution='i', projection='lcc', lat_0=49.0, lon_0=15.8, lat_1=46., lat_2=52., ax=plt.gca())
    elif options.show_domain.lower() in ('europe',):
        m = Basemap(projection='laea', width= 4300000,height=4000000, resolution='i', lat_ts=55.00,lat_0=55.00,lon_0=15.00)
        m.drawparallels(np.arange(-90.,91.,10.), labels=[0,0,0,0],linewidth=0.5)
        m.drawmeridians(np.arange(-180.,181.,10.), labels=[0,0,0,0],linewidth=0.5)
        m.drawmapboundary(fill_color='white')
    elif options.show_domain.lower()=='world':
        m = Basemap(projection='moll',resolution='c',lon_0=0.)
        m.drawparallels(np.arange(-90.,91.,10.), labels=[0,0,0,0],linewidth=0.5)
        m.drawmeridians(np.arange(-180.,181.,10.), labels=[0,0,0,0],linewidth=0.5)
        m.drawmapboundary(fill_color='white')
    else:
        grdis = gridfh.grid_size_in_meters

        m = Basemap(width=(len(gridfh.dimensions['x'])-bufferzone*2-2)*grdis, height=(len(gridfh.dimensions['y'])-bufferzone*2-2)*grdis, resolution='i', projection='lcc', lat_0=gridfh.latitude_of_projection_origin, lon_0=gridfh.longitude_of_projection_origin, lat_1=gridfh.standard_parallel[0], lat_2=gridfh.standard_parallel[1], ax=plt.gca())

    if isfile(options.bgimage):
        m.warpimage(image=options.bgimage)

    if options.normalize:
        vardatanorm = colors.Normalize(vmin=options.norm_minimum,vmax=options.norm_maximum)
    elif options.lognormalize:
        vardatanorm = colors.SymLogNorm(linthresh=20.,linscale=1.0,vmin=options.norm_minimum,vmax=options.norm_maximum)
    else:
        vardatanorm = None

    x,y = m(lon,lat)
    if options.deaccumulate>0 and t>time1 and counter%options.deaccumulate>0:
        print "*** Deaccumulating time %d " % t
        data = vardata[t]-vardata[t-1]
    else:
        data = vardata[t]

    if options.maskoceans:
        from mpl_toolkits.basemap import maskoceans
        data = maskoceans(lon,lat,data)

    if options.type=='sum':
        levels = levels_sum[options.show_domain]
        colors = colors_sum[options.show_domain]
        CS = m.contourf(x,y,data, alpha=options.data_alpha, levels=levels, colors=colors, zorder=zorder, extend=options.extend, norm=vardatanorm)
    else:
        if options.cmap != '':
            cmap = options.cmap
        else:
            cmap=cm.bwr

        if options.reversecmap:
            cmap=cm.bwr_r

        if options.drawfunction=='contour':
            drawfunction = m.contour
        else:
            drawfunction = m.contourf

        CS = drawfunction(x,y,data, alpha=options.data_alpha,
                cmap=cmap,
                zorder=zorder, extend=options.extend,
                norm=vardatanorm,
                levels=levels_ts,
            )

    m.drawcoastlines(linewidth=0.2)
    m.drawcountries(linewidth=0.4)
    m.drawmapboundary()

    if options.colorbar!='none':
        plt.colorbar(CS, orientation=options.colorbar,shrink=0.8)

    if options.labelbyseasons:
        season = get_season_name_by_month(mon)
        plt.title(u'%s %s [%s]' % (options.description.decode('utf-8'), season, options.units.decode('utf-8')), fontsize='small')
        plt.savefig("%s-%s-%s.png" % (args[1], season,options.show_domain), bbox_inches='tight')
    elif options.labelbytime:
        plt.title(u'%s [%s] %s.%s.%s %s:%s' % (options.description.decode('utf-8'), options.units.decode('utf-8'),d,mon,Y,hh,mm), fontsize='small')
        plt.savefig("%s-%04d-%02d-%02d-%02d.%02d.%s.png" % (args[1], Y,mon,d,hh,mm,options.show_domain), bbox_inches='tight', dpi=options.dpi)
    else:
        plt.title(u'%s [%s]' % (options.description.decode('utf-8'), options.units.decode('utf-8')), fontsize='small')
        plt.savefig("%s.%s.png" % (args[1], options.show_domain), bbox_inches='tight', dpi=options.dpi)


    counter += 1
