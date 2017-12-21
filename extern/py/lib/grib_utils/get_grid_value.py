#!/usr/bin/env python

import os
import sys
import pygrib

##
# Get the value of a given set of grib parameters from the 10-meter UGRD 
# grib message of a given grib file
#
# OUTPUT: List of values for the requested parameters, separated by space
#
# USAGE: get_grid_extents.py <file name> <list of parameters requested>
#
# Javier.Delgado@noaa.gov
##

if len(sys.argv) > 2:
   file_name = sys.argv[1]
   params_requested = sys.argv[2:]
else:
   print 'USAGE: %s file params' %sys.argv[0]
   sys.exit(1)
if not os.path.exists(file_name):
   print 'File not found: ', file_name
   sys.exit(1)

grbindx = pygrib.index(file_name, 'shortName', 'typeOfLevel', 'level')
selected_grbs = grbindx.select(shortName='10u', typeOfLevel='heightAboveGround', level=10)
if len(selected_grbs) == 0:
   print 'Did not find a u10 field in the given file'
   sys.exit(1)
if len(selected_grbs) > 1:
   print 'More than one match, this is unexpected'
   sys.exit(1)
grbmsg = selected_grbs[0]
for param in params_requested:
   sys.stdout.write("%s " %grbmsg[param])
