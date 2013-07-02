#!/usr/bin/env python

from Scientific.IO.NetCDF import NetCDFFile as ncf
import sys
from datetime import date
from calendar import monthrange

refdate = date(1949,12,1)
year1=int(sys.argv[2])
year2=int(sys.argv[3])
#print year1, year2

ff = ncf(sys.argv[1],'a')
ff.createDimension('bnds',2)
tb = ff.createVariable('time_bnds','d',('time','bnds'))
t = ff.variables['time']

tbdata = []
tdata = []

for y in range(year1,year2+1):
    for m in range(1,13):
        mp = m
        yp = y

        daysinmonth=monthrange(y,m)[1]
        for d in range(1,daysinmonth+1):
            dp = d+1
            if dp>daysinmonth:
                dp = 1
                mp = (m+1)%12

            if mp == 0:
                mp = 12

            if mp == 1:
                yp += 1

            _date1 = date(y,m,1)
            _date2 = date(yp,mp,dp)

            tbdata.append([(_date1-refdate).days, (_date2-refdate).days])
            tdata.append((_date1-refdate).days+(_date2-_date1).days/2.)

tb.assignValue(tbdata)
t.assignValue(tdata)

ff.flush()
ff.close()
