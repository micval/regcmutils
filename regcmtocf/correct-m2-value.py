#!/usr/bin/env python

import sys
from netCDF4 import Dataset as ncf

ff = ncf(sys.argv[1],'a')
ff.variables['m2'][:] = 2
ff.sync()
ff.close()
