#!/usr/bin/env python

import numpy as np
import pygrib
import logging as log

'''
This module contains routines that subset one of more fields and/or field:level 
pairs from a Grib file and output to another file

NOTES:
g['values'] to get the data
g['level'] to get the level

To get data and other properties belongs to one gribfile, variableName, typeOfLevel, and level  by fastest way using the file index >>> file_name = gdas1.t00z.grbanl  >>> fileidx = pygrib.index(file_name,name,typeOfLevel,level)  >>> g = fileidx.select(name = "Geopotential Height", typeOfLevel = "isobaricInhPa", level = 1000)  >>> g  [1:Geopotential Height:gpm (instant):regular_ll:isobaricInhPa:level 1000:fcst time 0:from 201005250000]  >>> g[0][values]  array([[ 289.1,  289.1,  289.1, ...,  289.1,  289.1,  289.1],         [ 300.8,  300.8,  300.8, ...,  301. ,  300.9,  300.9],               ...,              [ 233. ,  233. ,  233. , ...,  233. ,  233. ,  233. ]])  Notes: 1. Here this fileidx belongs to the file_name  = gdas1.t00z.grbanl  2. fileindex is more faster than pygrib.open() method 3. In fileindex we can set the arguments maximum only the following three options  ...  name,typeOfLevel,levelLinks
'''

def get_field_name_from_wgrib_key(key):
   '''
   Given a key corresponding to a grib field in wgrib format, return
   the grib entry key, which corresponds to the parameterName in pygrib
   '''
   if key == 'HGT': return "GH Geopotential height gpm"
   if key == 'UGRD': return "U U-component of wind m s**-1"
   if key == 'VGRD': return "V V-component of wind m s**-1"
   if key == 'ABSV': return "None Absolute vorticity s**-1"
   if key == "PRMSL": return "MSL Mean sea level pressure Pa"
   if key == 'TMP': return "T Temperature K"
   raise Exception("Unknown key: %s" %key)


def _create_gribfile_from_grib_messages(grib_messages, outfile_name):
    '''
    Create an output grib file given a set of grib messages
    '''    
    # write grib file
    outfile = open(outfile_name, 'wb')
    for entry in grib_messages:
        outfile.write(entry.tostring())
    outfile.close()
    #pygrib.open(outfile_name).readline()


def create_grid_subset(gribfile, fields_with_levs=None, 
                    fields_without_levs=None, outfile_name="output.grb"):
    '''
    Create a subset of a grib file with just the fields passed in. 
    There are two input parameters to control what the subsetted file contains:
    fields_with_levs - This is a Dictionary mapping field names to levels
    fields_without_levs - This is a List with the field names
    '''
    output_grib_messages = []
    grib_it = pygrib.open(input_file)
    for grbEntry in grib_it:
        if (grbEntry.parameterName in parameters_wanted and grbEntry.level in levels) \
            or (grbEntry.parameterName in parameters_nolevs_wanted):
            log.debug("Found %s" %grbEntry.parameterName)
            #grbEntry['forecastTime'] = 240
            #grbEntry.dataDate = 2001010101
            output_grib_messages.append(grbEntry)
    _create_gribfile_from_grib_messages(output_grib_messages, outfile_name)



def subset_for_tracker(input_file, output_file='hwrftrk.grb'):
    '''
    Subset one of more fields and/or field:level paris from a Grib file and
    output to another file
    The fields are put in the output grib file in the same order that is used
    in the operational HWRF system (pyHWRF).
    '''
    tracker_subset = [  'HGT:925', 'HGT:850', 'HGT:700', 'UGRD:850', 'UGRD:700',
                        'UGRD:500', 'VGRD:850', 'VGRD:700', 'VGRD:500',
                        'UGRD:10', 'VGRD:10', 'ABSV:850', 'ABSV:700',
                        'PRMSL', 'HGT:900', 'HGT:800', 'HGT:750', 'HGT:650',
                        'HGT:600', 'HGT:550', 'HGT:500', 'HGT:450', 'HGT:400',
                        'HGT:350', 'HGT:300', 'HGT:250', 'TMP:500', 'TMP:450',
                        'TMP:400', 'TMP:350', 'TMP:300', 'TMP:250' ]
    output_grib_messages = []
    # Populate output array in same order as TRACKER_SUBSET
    for field in tracker_subset:
        toks = field.split(":")
        key = toks[0].strip()
        if len(toks) > 1:
            #level = toks[1].strip()
            # set level, which may require translation
            # TODO : anything else we need to account for?
            #if level == '10 m':
            #    level = 1
            #else:
            #    level = int(level)
            level = int(toks[1].strip())
        else:
            level = None
        field_name = get_field_name_from_wgrib_key(key)
        grib_it = pygrib.open(input_file)
        for grbEntry in grib_it:
            if grbEntry.parameterName == field_name:
                #if level is not None: print level, grbEntry.level
                if (level is not None and level == grbEntry.level) or level is None:
                    output_grib_messages.append(grbEntry)
    _create_gribfile_from_grib_messages(output_grib_messages, output_file)


##
# MAIN
##
if __name__ == '__main__':
    
    input_file = './d01.grib'
    # set parameters that you want for a given set of levels
    parameters_wanted  = ( "GH Geopotential height gpm", "U U-component of wind m s**-1",
                        "V V-component of wind m s**-1", "T Temperature K")
    levels = (850, 700)
    
    # set parameters that do not have levels associated
    parameters_nolevs_wanted = ( "MSL Mean sea level pressure Pa", "None Absolute vorticity s**-1" )
    
    create_grid_subset(input_file, parameters_wanted, parameters_nolevs_wanted)
    subset_for_tracker(input_file)
    
    output_grib_messages = []

