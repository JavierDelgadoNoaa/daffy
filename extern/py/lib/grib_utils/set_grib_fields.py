#!/usr/bin/env python

import numpy as np
import pygrib
import logging as log
import sys

'''
Set/Modify one or more fields in all messages contained in a grib file.
Output  will be written to the same file
USAGE:
  set_grib_fields.py filename f1=value1 [f2 = value2 [f3=value3 [ ... ] ] ]
'''

def set_field(grbmsg, field_name, value):
    '''
    Set the `field_name` field of `grbmsg` to `value`.
    First try setting as string, then as float, then as int
    '''
    try:
        grbmsg[field_name] = value
    except TypeError:
        try:
            grbmsg[field_name] = float(value)
        except TypeError:
            grbmsg[field_name] = int(value)

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


##
# MAIN
##
if __name__ == '__main__':
    
    input_file = sys.argv[1]
    kv_pairs = sys.argv[2:]
    keys = [ x.split('=')[0] for x in kv_pairs ]
    values = [ x.split('=')[1] for x in kv_pairs ]
    grib_messages = []
    grbs = pygrib.open(input_file)
    grbs.seek(0)
    for grbmsg in grbs:
        for i in range(len(keys)):
            set_field(grbmsg, keys[i], values[i])
        grib_messages.append(grbmsg) 
    grbs.close()
    _create_gribfile_from_grib_messages(grib_messages, input_file)

