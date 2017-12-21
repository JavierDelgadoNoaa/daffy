#!/usr/bin/env python
'''
This module contains routines related to observation processing

Javier.Delgado@noaa.gov
'''

import sys
import os
import shutil
import time
import fnmatch
import logging as log

def get_matching_ob_files(data_path, filename_pattern, analysis_date, logger=None):
   ''' 
   Find files in <data_path> matching the <filename_pattern> for the <analysis_date>. The following
    special characters will be translated:
        @Y - 4-digit year of analysis date
        @y - 2-digit year (as of DAFFY 1.0.3.3)
        @m - 2-digit month of analysis date
        @H - 2-digit hour of anlysis date
        @M - 2-digit minute of analysis date
        *  - arbitrary-length string of numbers or letters (NOTE : Only one of these can exist)

   <analysis_date> should be a time tupple

   if logger is not passed in,  create a new one
   '''

   if logger is None: 
      import logging as logger
      logger.basicConfig(level=log.DEBUG)
     
   filename = filename_pattern
   filename = filename.replace('@Y', str(analysis_date.tm_year) )
   filename = filename.replace('@y', str(analysis_date.tm_year)[2:4] )
   filename = filename.replace('@m', time.strftime( '%m' , analysis_date) )
   filename = filename.replace('@d', time.strftime( '%d' , analysis_date) )
   filename = filename.replace('@H', time.strftime( '%H' , analysis_date) )
   filename = filename.replace('@M', time.strftime( '%M' , analysis_date) )
   
   # process wildcard (*). Note that a max of one * is allowed, since that should be sufficient
   # and makes the code much simpler (otherwise we'd need an extra for loop) 
   if filename.count('*') > 1:
      logger.error('File pattern may only contain one asterisk!')
      sys.exit(13)
   asteriskIdx = filename.find('*')

   if asteriskIdx > -1 :
      #wildcards to process, so we may have multiple files
      prefix = filename[ : asteriskIdx ]
      suffix = filename[ asteriskIdx + 1 : ]
      matching_files = []
      for fil in os.listdir(data_path):
         if fnmatch.fnmatch(fil, '%s*%s' %(prefix,suffix) ) : 
            matching_files.append(fil)
      if len(matching_files) == 0:
         # if logger has the warn_once() method, use it. otherwise just use warn()
         msg = 'No file matching the pattern "%s*%s" was found in [%s]' \
               %(prefix, suffix, data_path)
         warn_once = getattr(logger, 'warn_once', None)
         if callable(warn_once):
            logger.warn_once(msg)
         else:
            logger.warn(msg)
      return matching_files

   else:
      return [filename]



