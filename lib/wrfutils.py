#!/usr/bin/env python
from jdutils import zeropad
import time

def get_wrf_output_file_suffix(rundate):
   '''
   Returns the date-portion of WRF output files (i.e. the '2005-08-01_00:00:00' part)
   '''
   # UPDATE : Changed from gmtime to localtime for portability on systems that use different TZs
   return time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime(rundate))

def get_wrfout_file_name(rundate, domain=1):
   # wrfout_d01_2005-08-01_00:00:00
   domain = zeropad(domain, 2)
   return 'wrfout_d'  + domain + '_' + get_wrf_output_file_suffix(rundate)

def get_wrfrst_file_name(rundate, domain=1):
   domain = zeropad(domain, 2)
   return 'wrfrst_d'  + domain + '_' + get_wrf_output_file_suffix(rundate)

def get_wrfinput_file_name(rundate, domain=1):
   domain = zeropad(domain, 2)
   return 'wrf_3dvar_input_d'  + domain + '_' + get_wrf_output_file_suffix(rundate)
