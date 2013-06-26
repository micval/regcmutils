#!/usr/bin/env python

from subprocess import call

experiment='Euro-CORDEX'
realm='STS'
variables = ('tas','pr')
infilename_pattern='%s_%s.%%4d%%02d0100.%%s.nc' % (experiment, realm)
mergedfilename_pattern = '%s_EUR-44_CNRM-CM5_historical_r1i1p1_CUNI-RegCM4-2_day_%4d010100_%4d123100.nc'
dosplitvar=True
timespan='daily'
startyear=1989
endyear=2008
cdo_exec = 'cdo'

timeperiods = []
if timespan=='daily':
    startyear_dummy = startyear/5*5+1
    for i in range(startyear_dummy, endyear, 5):
        if i < startyear:
            y1 = startyear
        else:
            y1 = i

        if i+5 > endyear:
            y2 = endyear
        else:
            y2 = i+5-1

        timeperiods.append((y1,y2))

for var in variables:
    for y1,y2 in timeperiods:
        #yearlist = ','.join(map(str,range(y1,y2+1)))
        #print yearlist
        filelist = []
        for y in range(y1,y2+1):
            filelist.extend([infilename_pattern % (y,m,var) for m in range(1,13)])

        mergedfilename = mergedfilename_pattern % (var,y1,y2)
        merge_command = cdo_exec + ' mergetime %s %s' % (" ".join(filelist), mergedfilename)
        print merge_command
#        print call(merge_command, shell=True)
