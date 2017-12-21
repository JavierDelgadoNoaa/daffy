#!/usr/bin/env python

import os
import sys
import numpy
import pygrib

##
# Get the lat and lon extents of a grib file from its 10-meter UGRD grib message,
# accounting for scanning order of latitude points and for negative values (the
# output will always show positive values)
#
# OUTPUT: minLat minLon maxLat maxLon. 
#
# USAGE: get_grid_extents.py <file name>
#
# Javier.Delgado@noaa.gov
##

if len(sys.argv) > 1:
   file_name = sys.argv[1]
else:
   print 'USAGE: %s file' %sys.argv[0]
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

# Print the extents. Use the extents in the grim message fields if avaiable, 
# otherwise, estimate from latlons()
use_latlons = False
for k in ('latitudeOfFirstGridPointInDegrees', 'longitudeOfFirstGridPointInDegrees',
          'latitudeOfLastGridPointInDegrees', 'longitudeOfLastGridPointInDegrees'):
   if not grbmsg.has_key(k):
      sys.stderr.write('Grib message does not contain necessary extent key. Using latlons()')
      use_latlons = True
if not use_latlons:
   loLat = float(grbmsg['latitudeOfFirstGridPointInDegrees'])
   loLon = float(grbmsg['longitudeOfFirstGridPointInDegrees'])
   hiLat = float(grbmsg['latitudeOfLastGridPointInDegrees'])
   hiLon = float(grbmsg['longitudeOfLastGridPointInDegrees'])
   if int(grbmsg['jScansPositively']) == 0:
      tmp = loLat ; loLat = hiLat ; hiLat = tmp
else:
    (lats,lons) = grbmsg.latlons() # latlons is [ 411 x [ 705 ] ] 
    loLat = numpy.amin(lats) # min(lats[-1])
    loLon = numpy.amin(lons) # max(lons[-1])
    hiLat = numpy.amax(lats) # max(lats[0]) 
    hiLon = numpy.amax(lons) # min(lons[-1])
for attr in ('hiLat', 'hiLon', 'loLat', 'loLon'):
    if globals()[attr] < 0: globals()[attr] = 360 + globals()[attr]
print loLat, loLon, hiLat, hiLon

