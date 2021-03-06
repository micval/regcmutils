#!/usr/bin/env python

import sys
from subprocess import call
from optparse import OptionParser

parser = OptionParser(usage='Usage: %prog [ options ] <input filename pattern>', version="%prog 0.9")
parser.add_option('-x','--experiment',dest='experiment', help='experiment name')
#parser.add_option('-r','--realm',dest='realm', help='realm (ATM, RAD, SRF, STS) [default: %default]')
parser.add_option('-v','--variables',dest='variables', help='variables - comma separated CF names [default: %default]')
parser.add_option('-i','--infilename_pattern',dest='infilename_pattern', help='pattern of input file names (reserve placeholders for year, month, variable!) [default: %default]')
parser.add_option('-m','--mergedfilename_pattern',dest='mergedfilename_pattern', help='pattern of merged file names (reserve placeholders for variable, year!) [default: %default]')
parser.add_option('-t','--timespan',dest='timespan', help='timespan (daily, monthly, seasonal) [default: %default]')
parser.add_option('-s','--startyear',dest='startyear', help='start year [default: %default]', type='int')
parser.add_option('-e','--endyear',dest='endyear', help='end year [default: %default]',type='int')
parser.add_option('-c','--cdo_postproc',dest='cdo_postproc', help='cdo operators to use for postprocessing')

parser.set_defaults(
        experiment=None,
#        realm='STS',
        variables = 'tas pr tasmin tasmax',
        infilename_pattern='tmp_Euro-CORDEX-CMIP5_STS.%4d%02d0100.%s.nc',
        mergedfilename_pattern = '%s_EUR-44_CNRM-CERFACS-CNRM-CM5_{EXPERIMENT}_r1i1p1_CUNI-REGCM4-2_v1_day_%4d0101-%4d1231.nc',
        timespan='daily',
        startyear=2006,
        endyear=2100,
        cdo_postproc='',
)

cdo_exec = 'cdo'

(options, args) = parser.parse_args()

if options.experiment is not None:
    options.mergedfilename_pattern = options.mergedfilename_pattern.replace('{EXPERIMENT}',options.experiment)

timeperiods = []
if options.timespan=='daily':
    startyear_dummy = options.startyear/5*5+1
    if options.startyear < startyear_dummy:
        timeperiods.append((options.startyear, startyear_dummy-1))

    for i in range(startyear_dummy, options.endyear, 5):
        if i < options.startyear:
            y1 = options.startyear
        else:
            y1 = i

        if i+5 > options.endyear:
            y2 = options.endyear
        else:
            y2 = i+5-1

        timeperiods.append((y1,y2))

for var in options.variables.split():
    for y1,y2 in timeperiods:
        #yearlist = ','.join(map(str,range(y1,y2+1)))
        #print yearlist
        filelist = []
        for y in range(y1,y2+1):
            filelist.extend([options.infilename_pattern % (y,m,var) for m in range(1,13)])

        mergedfilename = options.mergedfilename_pattern % (var,y1,y2)
        merge_command = cdo_exec + ' mergetime %s t.%s' % (" ".join(filelist), mergedfilename)
        print merge_command
        print call(merge_command, shell=True)

        if options.cdo_postproc!='':
            cdo_postproc_command = '%s %s t.%s tt.%s; mv tt.%s t.%s' % (cdo_exec, options.cdo_postproc, mergedfilename, mergedfilename, mergedfilename, mergedfilename)
            print cdo_postproc_command
            print call(cdo_postproc_command, shell=True)
            print call('rm tt.%s' % mergedfilename, shell=True)

        time_correct_command = cdo_exec + ' setreftime,1949-12-01,00:00 -settaxis,%d-01-01,12:00,1day t.%s %s' % (y1, mergedfilename, mergedfilename)
        print time_correct_command
        print call(time_correct_command, shell=True)
        print call('rm t.%s' % mergedfilename, shell=True)

        timebnds_correct_command = './correct-time-dayavg.py %s %d %d' % (mergedfilename,y1,y2)
        print timebnds_correct_command
        print call(timebnds_correct_command, shell=True)
