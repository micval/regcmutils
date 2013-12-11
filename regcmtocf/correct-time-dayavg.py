#!/usr/bin/env python

#from Scientific.IO.NetCDF import NetCDFFile as ncf
from netCDF4 import Dataset as ncf
import sys
from datetime import date
from calendar import monthrange
import re

inputfilename=sys.argv[1]

refdate = date(1949,12,1)
try:
    yearsre = re.compile('_([0-9]+)-([0-9]+)_')
    m = yearsre.search(inputfilename)
    if m:
        year1=m.group(1)
        year2=m.group(2)

        if len(year1)>4:
            year1=year1[:4]

        if len(year2)>4:
            year2=year2[:4]
except:
    year1=int(sys.argv[2])
    year2=int(sys.argv[3])

print year1, year2

ff = ncf(inputfilename,'a')
ff.createDimension('bnds',2)
tb = ff.createVariable('time_bnds','d',('time','bnds'))
t = ff.variables['time']
tb.units=t.units
tb.calendar=t.calendar
t.bounds="time_bnds"
t.axis="T"
t.long_name="time"

tbdata = []
tdata = []

for y in range(year1,year2+1):
    for m in range(1,13):
        daysinmonth=monthrange(y,m)[1]
        for d in range(1,daysinmonth+1):
            mp = m
            yp = y
            dp = d+1
            if dp>daysinmonth:
                dp = 1
                mp += 1

            if mp == 13:
                mp = 1
                yp += 1

            _date1 = date(y,m,d)
            _date2 = date(yp,mp,dp)

            tbdata.append([(_date1-refdate).days, (_date2-refdate).days])
            tdata.append((_date1-refdate).days+(_date2-_date1).days/2.)

tb[:] = tbdata
t[:] = tdata

#ff.flush()
ff.sync()
ff.close()
