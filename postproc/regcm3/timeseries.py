#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Scientific.IO.NetCDF import NetCDFFile as ncf
import sys
import numpy.ma as ma
import matplotlib.pyplot as plt
import re

varname=sys.argv[1]
prefix=sys.argv[2]
timespec=sys.argv[3]
doplot=1
doprintvalues=1
omitcru=0

if prefix.endswith('masked'):
    domask = True
else:
    domask = False

(dom,m) = prefix.split('-')

ylabel = {'TA': u'Temperature [°C]', 'RT': u'Precipitation [mm/day]', 'TAMAX': u'Max. temp [°C]', 'TAMIN': u'Min. temp [°C]'}
if timespec=='ymonavg':
    xlabel='Month'
elif timespec=='ydaymean':
    xlabel='Day'
else:
    xlabel = 'Year'

xticks = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')

domains = {'inner':'AF', 'itcz':'ITCZ', 'sahara':'SAHARA','CA':'Central Africa','WA':'West Africa'}

data = []
labels = []
rcmre = re.compile('^SRF-(.*)-(\d+)-(\d+).')
CRUnum = -1
for fnum in range(len(sys.argv[4:])):
    fname = sys.argv[4+fnum]
    m = rcmre.search(fname)
    if m:
        label = m.group(1)
        year0 = int(m.group(2))
        year1 = int(m.group(3))
    elif fname.startswith('ERAINT'):
        label = 'ERAINT'
    else:
        label = 'CRU'
        CRUnum = fnum

    if not omitcru or label != 'CRU':
        labels.append(label)

    file = ncf(fname,'r')
    var = file.variables[varname]
    vardata = var.getValue()
    if label == 'regcm411' and varname!='RT':
        vardata = var[:,0]
    else:
        vardata = var.getValue()

    if hasattr(var,'missing_value'):
        fillval = var.missing_value
        maskeddata = ma.masked_where(vardata==fillval,vardata)
    elif hasattr(var,'_FillValue'):
        fillval = var._FillValue
        maskeddata = ma.masked_where(vardata==fillval,vardata)
        if label == 'CRU':
            globalmask = maskeddata.mask
        elif domask:
            maskeddata.mask = globalmask
    else:
        if domask:
            maskeddata = ma.MaskedArray(vardata,globalmask)
        else:
            maskeddata = vardata

    if hasattr(var,'scale_factor'):
        maskeddata *= var.scale_factor

    if hasattr(var,'add_offset'):
        maskeddata += var.add_offset

    if varname.startswith('TA') and maskeddata.mean()>100:
        maskeddata -= 273.15

    if not omitcru or label != 'CRU':
        print fname,maskeddata.shape,vardata.shape
        if (len(maskeddata.shape)) == 3:
            monmeans = maskeddata.mean(axis=2).mean(axis=1)
        elif (len(maskeddata.shape)) == 2:
            monmeans = maskeddata.mean(axis=1)
        data.append(monmeans)

    file.close()

if doplot:
    plt.figure(figsize=(10,6))
    plt.axes([0.075, 0.10, 0.70, 0.78])
    lines = []
    for i in range(len(data)):
        if i == CRUnum:
            lw = 2
        else:
            lw = 1

        lines.append(plt.plot(range(len(data[i])),data[i], lw=lw))

    plt.xlabel(xlabel, size='large')
    plt.ylabel(ylabel[varname], size='large')

    if timespec=='monavg':
        plt.xticks(range(6,len(data[i])+6,12),range(year0,year1+1)) # monavg
    elif timespec=='ymonavg':
        plt.xticks(range(0,len(data[i])+0),xticks) # ymonavg
        plt.xlim(0,11)
    elif timespec=='yearavg':
        plt.xticks(range(0,len(data[i])), range(year0,year1+1)) # yearavg
        plt.xlim(0,len(data[i])-1)
    elif timespec=='ydaymean':
        plt.xticks(range(0,len(data[i])), range(1,len(data[i])+1))
        plt.xlim(0,len(data[i])-1)

    if varname == 'RT':
        plt.ylim(ymin=0)

    plt.title(domains[dom],size='x-large')
    plt.figlegend(lines, labels, 'right')
    plt.savefig('%s-%s-%s-%s-%s.png'%(varname,prefix,year0,year1,timespec))

if doprintvalues:
    expnum = len(data)
    valnum = len(data[0])

    for j in range(expnum):
        print "%8s" % labels[j],

    print

    for i in range(valnum):
        for j in range(expnum):
            print "%8.2f" % data[j][i] ,

        print
