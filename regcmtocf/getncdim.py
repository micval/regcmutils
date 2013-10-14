#!/usr/bin/env python

import sys

try:
    from netCDF4 import Dataset as ncf
except:
    from Scientific.IO.NetCDF import NetCDFFile as ncf

infile = ncf(sys.argv[1],'r')
print len(infile.dimensions[sys.argv[2]])
