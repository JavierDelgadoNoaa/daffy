#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
The main purpose of this library is to create Python variables from the configuration settings.
'''

import os
from os import system as shell
from os import popen as pipe
from threading import Thread
import sys
import logging as log
import time
import subprocess
from common import get_yyyy_mm_dd_hh_mm 
from timing import TimeStruct

CONFIG_FILE_BASENAME = 'experiment.cfg.sh'
CONFIG_FILE = os.path.join ( os.getcwd(), CONFIG_FILE_BASENAME )
CONFIG_FILE_WRAPPER = os.path.join ( os.getcwd(), './_sourceit.sh' )
log.basicConfig(level=log.DEBUG)

class Config:
   pass

class TimeStruct:
   '''
   Class to encapsulate the time parameters year, month, day, hour, minute.
   Note that the state is individually held by these parameters, not by the 
   epochtime, although you can instantiate it using the epoch_time as an 
   optional parameter to the constructor
   '''
   def __init__(self, *args):
      self.year = ''
      self.month = ''
      self.day = ''
      self.hour = ''
      self.minute = ''
      self.seconds = '' 
      if len(args) > 0 :
         self._epoch_time = args[0]
         self.set_date_params_from_epoch_time()

   def set_date_params_from_epoch_time(self):
     self.year = time.strftime('%Y', time.localtime(self._epoch_time)) 
     self.month = time.strftime('%m', time.localtime(self._epoch_time)) 
     self.day = time.strftime('%d', time.localtime(self._epoch_time)) 
     self.hour = time.strftime('%H', time.localtime(self._epoch_time)) 
     self.minute = time.strftime('%M', time.localtime(self._epoch_time)) 

   def get_date_str(self):
      return '%s%s%s%s%s' %(self.year, self.month, self.day, self.hour, self.minute)

   def get_epochtime(self):
      elDay = '%s/%s/%s %s%s' %(self.month, self.day, self.year, self.hour, self.minute)
      return int( time.mktime( time.strptime(elDay, '%m/%d/%Y %H%M') ) )
   
   def get_yyyy_mm_dd_hh_mm(self):
      return get_yyyy_mm_dd_hh_mm(self.get_epochtime())

   def get_ymdhm(self):
      return self.get_date_str()


def sanity_check(cfg):
   '''
   Perform some routine sanity checks on the given configuration values, to
   help avoid common errors.
   '''
   # ensure restart interval is multiple of wrfout interval
   intervals = [ int(x.strip())*60 for x in cfg.wrfout_interval.split(',') ]
   for interval in intervals:
      if interval % cfg.frequency != 0  :
         if cfg.da_type != 'coldstart':
            print 'History interval [%i] is not a multiple of cycle frequency [%i]' %(interval, cfg.frequency)
            sys.exit(1)

   interval_seconds = int(cfg.interval_seconds)
   wps_interval = int(cfg.wps_interval)
   if (interval_seconds < wps_interval) or (wps_interval % interval_seconds) != 0 : 
      print 'Interval_seconds [%i] is either less then WPS_INTERVAL [%i] or not a multiple of it' %(interval_seconds, wps_interval)
      sys.exit(1)
   #"For nested domains, e_we must be one greater than an integer multiple of the nest's parent_grid_ratio (i.e., e_ew = n*parent_grid_ratio+1 for some positive integer n)"
   
   # ensure we have enough BC's for the forecast 
   if ( cfg.forecast_duration > cfg.wps_gfs_fcst_duration ):
      print ':( GFS forecast duration < Requested forecast duration)'
      sys.exit(1)
   if ( (cfg.forecast_duration + cfg.wps_gfs_frequency - cfg.frequency) > cfg.wps_gfs_fcst_duration ):
      print ':( Selected cycling frequency will not allow a forecast duration of %f (seconds)' %cfg.forecast_duration
      sys.exit(1)

   # ensure the forecast is at least the duration needed for the guess. 
   # In particular, for multi-time level analysis, we need to ensure this
   # holds, since WPS and Real scripts will use the forecast duration when
   # creating the boundary condition files
   ges_duration = cfg.frequency
   if cfg.multi_time_level_analysis :
      ges_duration += cfg.time_level_period * ( cfg.num_time_levels -1 ) / 2
   if ges_duration > cfg.forecast_duration:
      print "Forecast duration must greater than or equal to Guess duration (%f)" %ges_duration
      sys.exit(1)
   if (ges_duration % interval_seconds) != 0:
      print "Duration of guess forecast is not a multiple of interval_seconds!"
      sys.exit(1)

   # TODO (maybe, I don't know if we need to use auxhist_interval)
#  if  cfg.time_level_period % cfg.auxhist_interval != 0:
#     print "Chosen period between DA inout files (\$TIME_LEVEL_PERIOD) is not a multiple of AUXHIST_INTERVAL
#     sys.exit(1)

   if cfg.start_date.get_epochtime() < cfg.gfs_start_date :
      print 'START_DATE needs to be after WPS_GFS_START_DATE'
      sys.exit(1)
   if cfg.end_date.get_epochtime() > cfg.gfs_end_date:
      print 'END_DATE is after WPS_GFS_END_DATE'
      sys.exit(1)
      
   # TODO (lo priority since unlikely): Ensure num_gsi_tasks >= (NUM_MEMBERS+1) (precondition for gsi ensmean)
   
   # ensure num_members is set
   if cfg.num_members < 1 :
      print 'Set NUM_MEMBERS in configuration'
      sys.exit(1)

   # ensure log level is a valid value
   if not cfg.log_level in ( 'DEBUG', 'INFO', 'WARN', 'ERROR' ):
      print "Invalid LOG_LEVEL specified. Should be 'DEBUG', 'INFO', 'WARN', or 'ERROR'"
      sys.exit(1)

   # to keep the workflow dependency code simple, and since we usually want both of these
   # to be done, require perform_postproc_experiment to be set.
   if cfg.perform_archive and not cfg.perform_postproc_experiment:
      print "If PERFORM_ARCHIVE is set, PERFORM_EXPERIMENT_POSTPROC must also be set. Tip: remove the post/*.expt.zsh files if you don't want to do anything."

def get_bool_from_config(elstring):
   '''
   Given a string, return (logical) True if it's value, converted to lowercase,
   is 'true'. False if it is 'false'. Otherwise, raise an Error
   '''
   if elstring.lower() == 'true': return True
   elif elstring.lower() == 'false': return False
   else:
      raise Exception

def space_delimited_str_to_list(elstring):
   '''
   Given a string consisting of values separated by whitespace, return a list
   of the strings
   '''
   return elstring.split()

def read_config(cfg_file=CONFIG_FILE):
   ''' 
   Since a large portion of this application consists of shells scripts, we
   use shell scripts as config files for the user to configure experiments.
   In this routine, we source the main CONFIG file/script (CONFIG_FILE)
   to obtain the values of these variables and then populate the <cfg> object 
   with them. 
   **Dev Note: To add a configuration variable, add it to the list of parameters 
     to the cfg object and add an "elif" condition for it**
   '''

   cfg = Config()
   cfg.config_file_path = cfg_file 
   cfg.start_date  = TimeStruct()
   cfg.next_cycle_date = TimeStruct()
   cfg.end_date = TimeStruct()
   cfg.cold_start_date = TimeStruct()

   cmd = 'source ' + cfg_file + '&& env'
   if shell(cmd + '> /dev/null') != 0: # Make sure there are no problems with the script
      print ':( There is a problem with the config file %s ' %cfg_file
      sys.exit(1)
   else: 
      env = pipe ( cmd )
      contents = env.readlines()
      #print contents
   if True:
      for line in contents:
         
         #print line

         if line.startswith('YEAR='):
            cfg.start_date.year = line.strip()[ len('YEAR='):]
         elif line.startswith('MONTH='):
            cfg.start_date.month = line.strip()[ len('MONTH='):]
         elif line.startswith('START_DAY='):
            cfg.start_date.day = line.strip()[ len('START_DAY='):]
         elif line.startswith('START_HOUR='):
            cfg.start_date.hour = line.strip()[ len('START_HOUR='):]
         elif line.startswith('START_MINUTE='):
            cfg.start_date.minute = line.strip()[ len('START_MINUTE='):]
         elif line.startswith('DOMAIN='):
            cfg.domain_name = line.strip()[ len('DOMAIN='):]
         #elif line.startswith('MOD='):
            #cfg.MOD = line.strip()[ len('MOD='):]
         elif line.startswith('NUM_CYCLES='):
            cfg.num_cycles = int ( line.strip()[ len('NUM_CYCLES='):] )
         elif line.startswith('CYCLE_FREQUENCY='):
            cfg.frequency = int ( line.strip()[ len('CYCLE_FREQUENCY='):] )
         elif line.startswith('FORECAST_FREQUENCY='):
            cfg.forecast_frequency = int ( line.strip()[ len('FORECAST_FREQUENCY='):] )
         elif line.startswith('RUN_LENGTH='):
            cfg.run_length = int ( line.strip()[ len('RUN_LENGTH='):] )
            cfg.forecast_duration = cfg.run_length
         elif line.startswith('TOP_DIR='):
            cfg.top_dir = line.strip()[ len('TOP_DIR='):]
         elif line.startswith('RUN_TOP_DIR='):
            cfg.run_top_dir = line.strip()[ len('RUN_TOP_DIR='):]
         elif line.startswith('DIRNAME='):
            cfg.run_dir = line.strip()[ len('DIRNAME='):]
         elif line.startswith('MEMBER_DIR_PREFIX='):
            cfg.member_dir_prefix = line.strip()[ len('MEMBER_DIR_PREFIX='):]
         elif line.startswith('MAX_DOM='):
            cfg.max_dom = int ( line.strip()[ len('MAX_DOM='):] )
         #elif line.startswith('REF_LON='):
            #cfg.REF_LON = line.strip()[ len('REF_LON='):]
         #elif line.startswith('REF_LAT='):
            #cfg.REF_LAT = line.strip()[ len('REF_LAT='):]
         elif line.startswith('E_WE='):
            x = line.strip()[ len('E_WE='):]
            if x.endswith(','): x = x[:-1]
            cfg.e_we = [ int(xx) for xx in x.strip().split(',') ]
         elif line.startswith('E_SN='):
            x = line.strip()[ len('E_SN='):]
            if x.endswith(','): x = x[:-1]
            cfg.e_sn = [ int(xx) for xx in x.strip().split(',') ]
         elif line.startswith('DX='):
            x = line.strip()[ len('DX='):]
            if x.endswith(','): x = x[:-1]
            cfg.dx = [ float(xx) for xx in x.strip().split(',') ]
         elif line.startswith('DY='):
            x = line.strip()[ len('DY='):]
            if x.endswith(','): x = x[:-1]
            cfg.dy = [ float(xx) for xx in x.strip().split(',') ]
         elif line.startswith('GFS_ROOT='):
            cfg.gfs_data_root = line.strip()[ len('GFS_ROOT='):]
         #elif line.startswith('GFS_SOURCE='):
            #cfg.GFS_SOURCE = line.strip()[ len('GFS_SOURCE='):]
         #elif line.startswith('MESSAGE_FILES='):
            #cfg.MESSAGE_FILES = line.strip()[ len('MESSAGE_FILES='):]
         #elif line.startswith('GRIB_FILES='):
            #cfg.GRIB_FILES = line.strip()[ len('GRIB_FILES='):]
         #elif line.startswith('GRIB_FILE_PREFIX='):
            #cfg.GRIB_FILE_PREFIX = line.strip()[ len('GRIB_FILE_PREFIX='):]
         elif line.startswith('WPS_ROOT='):
            cfg.wps_dir = line.strip()[ len('WPS_ROOT='):]
         #elif line.startswith('WPS_UNGRIB_PREFIX='):
            #cfg.WPS_UNGRIB_PREFIX = line.strip()[ len('WPS_UNGRIB_PREFIX='):]
         elif line.startswith('WRFOUT_INTERVAL='):
            cfg.wrfout_interval = line.strip()[ len('WRFOUT_INTERVAL='):]
         #elif line.startswith('PARAM_ROOT='):
            #cfg.PARAM_ROOT = line.strip()[ len('PARAM_ROOT='):]
         #elif line.startswith('EXEC_ROOT='):
            #cfg.EXEC_ROOT = line.strip()[ len('EXEC_ROOT='):]
         elif line.startswith('WRF_ROOT='):
            cfg.wrf_dir = line.strip()[ len('WRF_ROOT='):]
         elif line.startswith('RUN_CYCLE='):
            print line.strip()[ len('RUN_CYCLE='):]
            cfg.run_cycle = get_bool_from_config( line.strip()[ len('RUN_CYCLE='):] )
            #print cfg.run_cycle
         elif line.startswith('CREATE_PERTS='):
            cfg.create_perts = get_bool_from_config( line.strip()[ len('CREATE_PERTS='):] )
         elif line.startswith('GENERATED_PERT_DIR='):
            cfg.generated_pert_dir = line.strip()[ len('GENERATED_PERT_DIR='):]
         elif line.startswith('RUN_WPS='):
            cfg.run_wps = get_bool_from_config( line.strip()[ len('RUN_WPS='):] )
         elif line.startswith('RUN_REAL='):
            cfg.run_real = get_bool_from_config( line.strip()[ len('RUN_REAL='):] )
         elif line.startswith('RUN_WRF='):
            cfg.run_wrf = get_bool_from_config( line.strip()[ len('RUN_WRF='):] )
         elif line.startswith('RUN_GSI='):
            cfg.run_gsi = get_bool_from_config(  line.strip()[ len('RUN_GSI='):] )
         elif line.startswith('NUM_MEMBERS='):
            cfg.num_members = int ( line.strip()[ len('NUM_MEMBERS='):] )
         #elif line.startswith('NUM_ZEROES='):
            #cfg.num_zeroes = int ( line.strip()[ len('NUM_ZEROES='):] )
         elif line.startswith('WPS_OUTPUT_SUBDIR='):
            cfg.wps_output_subdir = line.strip()[ len('WPS_OUTPUT_SUBDIR='):]
         elif line.startswith('MEMBER_DIR_PREFIX='):
            cfg.MEMBER_DIR_PREFIX = line.strip()[ len('MEMBER_DIR_PREFIX='):]
         elif line.startswith('GSI_OUT_BASEDIR='):
            cfg.gsi_out_basedir = line.strip()[ len('GSI_OUT_BASEDIR='):]
         elif line.startswith('JOB_SCRIPTS_DIR='):
            cfg.job_scripts_dir = line.strip()[ len('JOB_SCRIPTS_DIR='):]
         elif line.startswith('RUN_CYCLE_SCRIPT='):
            cfg.run_cycle_script = line.strip()[ len('RUN_CYCLE_SCRIPT='):]
         elif line.startswith('WPS_JOB_FILE='):
            cfg.wps_job_file = line.strip()[ len('WPS_JOB_FILE='):]
         elif line.startswith('HWRF_JOB_FILE='):
            cfg.hwrf_job_file = line.strip()[ len('HWRF_JOB_FILE='):]
         elif line.startswith('REAL_JOB_FILE='):
            cfg.real_job_file = line.strip()[ len('REAL_JOB_FILE='):]
         elif line.startswith('GSI_JOB_FILE='):
            cfg.gsi_job_file = line.strip()[ len('GSI_JOB_FILE='):]
         elif line.startswith('POLL_INTERVAL='):
            cfg.poll_interval = int ( line.strip()[ len('POLL_INTERVAL='):] )
         elif line.startswith('START_SECONDS='):
            cfg.start_date.seconds = line.strip()[ len('START_SECONDS='):]
            cfg.next_cycle_date.seconds = cfg.start_date.seconds
            cfg.end_date.seconds = cfg.start_date.seconds
         elif line.startswith('RESTART_FILE_PREFIX='):
            cfg.restart_file_prefix = line.strip()[ len('RESTART_FILE_PREFIX='):]
         elif line.startswith('RESTART_FILE_SUFFIX='):
            cfg.restart_file_suffix = line.strip()[ len('RESTART_FILE_SUFFIX='):]
         elif line.startswith('DA_TYPE='):
            cfg.da_type = line.strip()[ len('DA_TYPE='):]
         elif line.startswith('WPS_FILE_PREFIX='):
            cfg.wps_file_prefix = line.strip()[ len('WPS_FILE_PREFIX='):]
         elif line.startswith('WPS_FILE_SUFFIX_SUFFIX='):
            cfg.wps_file_suffix_suffix = line.strip()[ len('WPS_FILE_SUFFIX_SUFFIX='):]
         elif line.startswith('NUM_DIGITS='):
            cfg.num_digits = int ( line.strip()[ len('NUM_DIGITS='):] )
         elif line.startswith('END_YEAR='):
            cfg.end_date.year = line.strip()[ len('END_YEAR='):]
         elif line.startswith('END_MONTH='):
            cfg.end_date.month = line.strip()[ len('END_MONTH='):]
         elif line.startswith('END_DAY='):
            cfg.end_date.day = line.strip()[ len('END_DAY='):]
         elif line.startswith('END_HOUR='):
            cfg.end_date.hour = line.strip()[ len('END_HOUR='):]
         elif line.startswith('END_MINUTE='):
            cfg.end_date.minute = line.strip()[ len('END_MINUTE='):]
         elif line.startswith('INTERVAL_SECONDS='):
            cfg.interval_seconds = int ( line.strip()[len('INTERVAL_SECONDS='):] )
         elif line.startswith('WPS_INTERVAL='):
            cfg.wps_interval = line.strip()[ len('WPS_INTERVAL='): ]
         elif line.startswith('GSI_GES_DIR='):
            cfg.gsi_ges_subdir = line.strip()[ len('GSI_GES_DIR='):]
         elif line.startswith('GSI_ANALYSIS_DIR='):
            cfg.gsi_analysis_subdir = line.strip()[ len('GSI_ANALYSIS_DIR='):]
         elif line.startswith('EXPERIMENT_ID='):
            cfg.experiment_id = line.strip()[ len('EXPERIMENT_ID='):]
         elif line.startswith('WPS_OUTPUT_SUBDIR='):
            cfg.wps_subdir = line.strip()[ len('WPS_OUTPUT_SUBDIR='):]
         elif line.startswith('DA_FILE_TYPE='):
            cfg.da_file_type = line.strip()[ len('DA_FILE_TYPE='):]
         elif line.startswith('WRF_INPUT_FILE_PREFIX='):
            cfg.wrfinout_file_prefix =  line.strip()[ len('WRF_INPUT_FILE_PREFIX='):]
         elif line.startswith('WPS_GFS_FCST_DURATION='):
            cfg.wps_gfs_fcst_duration = int( line.strip()[ len('WPS_GFS_FCST_DURATION='):] )
         elif line.startswith('WPS_GFS_FREQUENCY='):
            cfg.wps_gfs_frequency = int( line.strip()[ len('WPS_GFS_FREQUENCY='):] )
         elif line.startswith('ANALYSIS_DOMAIN='):
            cfg.analysis_domain = line.strip()[ len('ANALYSIS_DOMAIN='):]
         elif line.startswith('FIRST_FORECAST='):
            cfg.first_forecast = int( line.strip()[ len('FIRST_FORECAST='):] )
         elif line.startswith('ACCOUNT='):
            cfg.batch_system_account = line.strip()[ len('ACCOUNT='):]
         elif line.startswith('BATCH_SYSTEM_PARTITION='):
            cfg.batch_system_partition = line.strip()[ len('BATCH_SYSTEM_PARTITION='):]
         elif line.startswith('BATCH_SYSTEM_NAME='):
            cfg.batch_system_name = line.strip()[ len('BATCH_SYSTEM_NAME='):]
         elif line.startswith('ROCOTO_DB_PATH='):
            cfg.rocoto_db_path = line.strip()[ len('ROCOTO_DB_PATH='):]
         elif line.startswith('COLDSTART_DATA_DIR='):
            cfg.coldstart_data_dir = line.strip()[ len('COLDSTART_DATA_DIR='):]
         elif line.startswith('COLDSTART_RUN_PREFIX='):
           cfg.coldstart_run_prefix = line.strip()[ len('COLDSTART_RUN_PREFIX='):]
         elif line.startswith('COLDSTART_DATA_SUBDIR='):
           cfg.coldstart_data_subdir = line.strip()[ len('COLDSTART_DATA_SUBDIR='):]
         elif line.startswith('NATURE_STATS_FILE='):
            cfg.nature_stats_file = line.strip()[ len('NATURE_STATS_FILE='):]
         elif line.startswith('ROCOTO_PATH='):
            cfg.rocoto_path = line.strip()[ len('ROCOTO_PATH='):]
         elif line.startswith('SPORADIC_DATASETS='):
            cfg.sporadic_datasets = space_delimited_str_to_list( line.strip()[ len('SPORADIC_DATASETS='):] )
         elif line.startswith('GSI_FAILS_IF_OBS_MISSING='):
            cfg.gsi_fails_if_obs_missing = get_bool_from_config( line.strip()[ len('GSI_FAILS_IF_OBS_MISSING='):] )
         elif line.startswith('DEFAULT_QUEUE='):
            cfg.default_queue = line.strip()[ len('DEFAULT_QUEUE='):]
         elif line.startswith('STATIC_MODEL_DATA_PATH='):
            cfg.static_model_data_path = line.strip()[ len('STATIC_MODEL_DATA_PATH='):]
         elif line.startswith('METGRID_CHECKSUM='):
            cfg.metgrid_checksum = line.strip()[ len('METGRID_CHECKSUM='):]
         elif line.startswith('GEOGRID_CHECKSUM='):
            cfg.geogrid_checksum = line.strip()[ len('GEOGRID_CHECKSUM='):]
         #elif line.startswith('ENSEMBLE_METGRID_DATA_SOURCE='):
         #   cfg.ensemble_metgrid_data_source = line.strip()[ len('ENSEMBLE_METGRID_DATA_SOURCE='):]
         elif line.startswith('CONV_CONTROL_DATA_DIR='):
            cfg.conv_control_data_dir = line.strip()[ len('CONV_CONTROL_DATA_DIR='):]
         elif line.startswith('MULTI_TIME_LEVEL_ANALYSIS='):
            cfg.multi_time_level_analysis = get_bool_from_config( line.strip()[ len('MULTI_TIME_LEVEL_ANALYSIS='):] )
         elif line.startswith('PERFORM_ENKF_ADDITIVE_INFLATION='):
            cfg.perform_enkf_additive_inflation = get_bool_from_config( line.strip()[ len('PERFORM_ENKF_ADDITIVE_INFLATION='):] )
         elif line.startswith('ENKF_ADDITIVE_INFLATION_COEFF='):
            cfg.additive_inflation_coeff = line.strip()[ len('ENKF_ADDITIVE_INFLATION_COEFF='):]
         elif line.startswith('TIME_LEVEL_PERIOD='):
            cfg.time_level_period = int( line.strip()[ len('TIME_LEVEL_PERIOD='):] )
         elif line.startswith('NUM_TIME_LEVELS='):
            cfg.num_time_levels = int( line.strip()[ len('NUM_TIME_LEVELS='):] )
         elif line.startswith('GFS_FCST_ID='):
            cfg.gfs_forecast_id = line.strip()[ len('GFS_FCST_ID='):]
         elif line.startswith('GFS_ENSEMBLE_ID='):
            cfg.gfs_ensemble_id = line.strip()[ len('GFS_ENSEMBLE_ID='):]
         elif line.startswith('GFS_ENSEMBLE_FORECAST_DURATION='):
            cfg.gfs_ensemble_forecast_duration = line.strip()[ len('GFS_ENSEMBLE_FORECAST_DURATION='):]
         elif line.startswith('ANALYSIS_FILE_PREFIX='):
            cfg.auxhist_file_prefix = line.strip()[ len('ANALYSIS_FILE_PREFIX='):]
         elif line.startswith('WPS_GFS_START_DATE='):
            cfg.gfs_start_date = long( line.strip()[ len('WPS_GFS_START_DATE='):] )
         elif line.startswith('WPS_GFS_END_DATE='):
            cfg.gfs_end_date = long( line.strip()[ len('WPS_GFS_END_DATE='):] )
         elif line.startswith('PERFORM_POSTPROC_FCST='):
            cfg.perform_postproc_fcst =  get_bool_from_config( line.strip()[ len('PERFORM_POSTPROC_FCST='):] )
         elif line.startswith('PERFORM_POSTPROC_CYCLE='):
            cfg.perform_postproc_cycle = get_bool_from_config (line.strip()[ len('PERFORM_POSTPROC_CYCLE='):] )
         elif line.startswith('COLD_START_YEAR='):
            cfg.cold_start_date.year = line.strip()[ len('COLD_START_YEAR='):]
         elif line.startswith('COLD_START_MONTH='):
            cfg.cold_start_date.month = line.strip()[ len('COLD_START_MONTH='):]
         elif line.startswith('COLD_START_DAY='):
            cfg.cold_start_date.day = line.strip()[ len('COLD_START_DAY='):]
         elif line.startswith('COLD_START_HOUR='):
            cfg.cold_start_date.hour = line.strip()[ len('COLD_START_HOUR='):]
         elif line.startswith('COLD_START_MINUTE='):
            cfg.cold_start_date.minute = line.strip()[ len('COLD_START_MINUTE='):]
         elif line.startswith('GSI_DATA_THIS_EXPERIMENT='):
            cfg.gsi_data_this_experiment = space_delimited_str_to_list( line.strip()[ len('GSI_DATA_THIS_EXPERIMENT='):] )
         elif line.startswith('GSI_OBS_DATA_TOPDIR='):
            cfg.gsi_obs_data_dir = line.strip()[ len('GSI_OBS_DATA_TOPDIR='):]
         elif line.startswith('LOG_LEVEL='):
            cfg.log_level = line.strip()[ len('LOG_LEVEL='):]
         elif line.startswith('ROCOTO_STATE_FILE_TEMP_LOCATION='):
            cfg.rocoto_state_file_temp_location = line.strip()[len('ROCOTO_STATE_FILE_TEMP_LOCATION='):]
         elif line.startswith('LUSTRE_ROCOTO_HACK=') :
            cfg.lustre_rocoto_hack = get_bool_from_config( line.strip()[len('LUSTRE_ROCOTO_HACK='):] )   
         elif line.startswith('SUPERCOMPUTER='):
            cfg.supercomputer = line.strip()[ len('SUPERCOMPUTER='):]
         elif line.startswith('GSI_ROOT='):
            cfg.gsi_root_dir = line.strip()[ len('GSI_ROOT='):]
         elif line.startswith('GSI_NL_TEMPLATE='):
            cfg.gsi_namelist_template = line.strip()[ len('GSI_NL_TEMPLATE='):]
         elif line.startswith('WRF_NAMELIST_TEMPLATE='):
            cfg.wrf_namelist_template = line.strip()[ len('WRF_NAMELIST_TEMPLATE='):]
         elif line.startswith('PERFORM_UPP_ENSEMBLE_ANALYSIS='):
            cfg.perform_ensemble_analysis_upp = get_bool_from_config( line.strip()[ len('PERFORM_UPP_ENSEMBLE_ANALYSIS='):] )
         elif line.startswith('PERFORM_UPP_ENSEMBLE_GES='):
            cfg.perform_ensemble_ges_upp = get_bool_from_config( line.strip()[ len('PERFORM_UPP_ENSEMBLE_GES='):] )
         elif line.startswith('MODEL_CONFIG_ID='):
            cfg.model_config_id = line.strip()[ len('MODEL_CONFIG_ID='):]
         elif line.startswith('PERFORM_EXPERIMENT_POSTPROC='):
            cfg.perform_postproc_experiment = get_bool_from_config( line.strip()[ len('PERFORM_EXPERIMENT_POSTPROC='):] )
         elif line.startswith('PERFORM_ARCHIVE='):
            cfg.perform_archive = get_bool_from_config( line.strip()[ len('PERFORM_ARCHIVE='):] )
         elif line.startswith('GSI_OBS_CFG_TOPDIR='):
            cfg.gsi_obs_cfg_topdir = line.strip()[ len('GSI_OBS_CFG_TOPDIR='):]
         elif line.startswith('NHR_ASSIMILATION='):
            cfg.assimilation_time_window = line.strip()[ len('NHR_ASSIMILATION='):]
         elif line.startswith('SAT_DATA_THINNING='):
            cfg.perform_satellite_thinning = get_bool_from_config( line.strip()[ len('SAT_DATA_THINNING='):] )
         elif line.startswith('BERROR_STATS='):
            cfg.background_error_stats_file = line.strip()[ len('BERROR_STATS='):]
         elif line.startswith('SATINFO='):
            cfg.satinfo_file = line.strip()[ len('SATINFO='):]
         elif line.startswith('CONVINFO='):
            cfg.convinfo_file = line.strip()[ len('CONVINFO='):]
         elif line.startswith('ENKF_ROOT='):
            cfg.enkf_root = line.strip()[ len('ENKF_ROOT='):]
         elif line.startswith('ENKF_NAMELIST_TEMPLATE='):
            cfg.enkf_namelist_template = line.strip()[ len('ENKF_NAMELIST_TEMPLATE='):]
         elif line.startswith('LOCAL_DATABASE_FILE_NAME='):
            cfg.local_database_file_name = line.strip()[ len('LOCAL_DATABASE_FILE_NAME='):]
         elif line.startswith('GLOBAL_DATABASE_PATH='):
            cfg.global_database_path = line.strip()[ len('GLOBAL_DATABASE_PATH='):]
         elif line.startswith('E_VERT='):
            x = line.strip()[ len('E_VERT='):] 
            if x.endswith(','): x = x[:-1]
            cfg.num_vertical_levels = [ int(xx) for xx in x.strip().split(',') ]
         elif line.startswith('TIME_STEP='):
            cfg.time_step = float( line.strip()[ len('TIME_STEP='):] )
         elif line.startswith('TCVITALS_DIR='):
            cfg.tc_vitals_for_model = line.strip()[ len('TCVITALS_DIR='):]
         elif line.startswith('STATIC_DATA_ROOT='):
            cfg.static_data_root = line.strip()[ len('STATIC_DATA_ROOT='):]
         elif line.startswith('APPS_ROOT='):
            cfg.apps_root = line.strip()[ len('APPS_ROOT='):]
         elif line.startswith('UPP_HOME='):
            cfg.upp_root = line.strip()[ len('UPP_HOME='):]
         elif line.startswith('DIAPOST_DIST='):
            cfg.diapost_root = line.strip()[ len('DIAPOST_DIST='):]
         elif line.startswith('TCV_DOMAIN='):
            cfg.tcv_evaluation_domain = int(line.strip()[ len('TCV_DOMAIN='):])
         # enkf settings
         elif line.startswith('ADAPTIVE_POSTERIOR_INFLATION_NORTHERN_HEMISPHERE='):
            cfg.adaptive_posterior_inflation_nh = float( line.strip()[ len('ADAPTIVE_POSTERIOR_INFLATION_NORTHERN_HEMISPHERE='):] )
         elif line.startswith('ADAPTIVE_POSTERIOR_INFLATION_SOUTHERN_HEMISPHERE='):
            cfg.adaptive_posterior_inflation_sh = float( line.strip()[ len('ADAPTIVE_POSTERIOR_INFLATION_SOUTHERN_HEMISPHERE='):] )
         elif line.startswith('ADAPTIVE_POSTERIOR_INFLATION_TROPICS='):
            cfg.adaptive_posterior_inflation_tropics = float( line.strip()[ len('ADAPTIVE_POSTERIOR_INFLATION_TROPICS='):] )
         elif line.startswith('MIN_INFLATION='):
            cfg.min_inflation = float( line.strip()[ len('MIN_INFLATION='):] )
         elif line.startswith('MAX_INFLATION='):
            cfg.max_inflation = float( line.strip()[ len('MAX_INFLATION='):] )
         elif line.startswith('HORIZONTAL_LOCALIZATION_NORTHERN_HEMISPHERE='):
            cfg.horizontal_localization_nh = float( line.strip()[ len('HORIZONTAL_LOCALIZATION_NORTHERN_HEMISPHERE='):] )
         elif line.startswith('HORIZONTAL_LOCALIZATION_SOUTHERN_HEMISPHERE='):
            cfg.horizontal_localization_sh = float( line.strip()[ len('HORIZONTAL_LOCALIZATION_SOUTHERN_HEMISPHERE='):] )
         elif line.startswith('HORIZONTAL_LOCALIZATION_TROPICS='):
            cfg.horizontal_localization_tropics = float( line.strip()[ len('HORIZONTAL_LOCALIZATION_TROPICS='):] )
         elif line.startswith('OBSERVATION_TIME_LOCALIZATION='):
            cfg.observation_time_localization = float( line.strip()[ len('OBSERVATION_TIME_LOCALIZATION='):] )
         elif line.startswith('VERTICAL_LOCALIZATION_NORTHERN_HEMISPHERE_CONVOBS='):
            cfg.vertical_localization_nh_convobs = float( line.strip()[ len('VERTICAL_LOCALIZATION_NORTHERN_HEMISPHERE_CONVOBS='):] )
         elif line.startswith('VERTICAL_LOCALIZATION_SOUTHERN_HEMISPHERE_CONVOBS='):
            cfg.vertical_localization_sh_convobs = float( line.strip()[ len('VERTICAL_LOCALIZATION_SOUTHERN_HEMISPHERE_CONVOBS='):] )
         elif line.startswith('VERTICAL_LOCALIZATION_TROPICS_CONVOBS='):
            cfg.vertical_localization_tropics_convobs = float( line.strip()[ len('VERTICAL_LOCALIZATION_TROPICS_CONVOBS='):] )
         elif line.startswith('VERTICAL_LOCALIZATION_NORTHERN_HEMISPHERE_SATOBS='):
            cfg.vertical_localization_nh_satobs = float( line.strip()[ len('VERTICAL_LOCALIZATION_NORTHERN_HEMISPHERE_SATOBS='):] )
         elif line.startswith('VERTICAL_LOCALIZATION_SOUTHERN_HEMISPHERE_SATOBS='):
            cfg.vertical_localization_sh_satobs = float( line.strip()[ len('VERTICAL_LOCALIZATION_SOUTHERN_HEMISPHERE_SATOBS='):] )
         elif line.startswith('VERTICAL_LOCALIZATION_TROPICS_SATOBS='):
            cfg.vertical_localization_tropics_satobs = float( line.strip()[ len('VERTICAL_LOCALIZATION_TROPICS_SATOBS='):] )
         elif line.startswith('VERTICAL_LOCALIZATION_NORTHERN_HEMISPHERE_PSOBS='):
            cfg.vertical_localization_nh_psobs = float( line.strip()[ len('VERTICAL_LOCALIZATION_NORTHERN_HEMISPHERE_PSOBS='):] )
         elif line.startswith('VERTICAL_LOCALIZATION_SOUTHERN_HEMISPHERE_PSOBS='):
            cfg.vertical_localization_sh_psobs = float( line.strip()[ len('VERTICAL_LOCALIZATION_SOUTHERN_HEMISPHERE_PSOBS='):] )
         elif line.startswith('VERTICAL_LOCALIZATION_TROPICS_PSOBS='):
            cfg.vertical_localization_tropics_psobs = float( line.strip()[ len('VERTICAL_LOCALIZATION_TROPICS_PSOBS='):] )
         elif line.startswith('INFLATION_SMOOTHING_PARAMETER='):
            cfg.inflation_smoothing_parameter = float( line.strip()[ len('INFLATION_SMOOTHING_PARAMETER='):] )
         elif line.startswith('ENKF_SATBIAS_ITERATIONS='):
            cfg.enkf_satbias_iterations = int( line.strip()[ len('ENKF_SATBIAS_ITERATIONS='):] )
         elif line.startswith('POSTERIOR_PRIOR_THRESHOLD='):
            cfg.posterior_prior_threshold = float( line.strip()[ len('POSTERIOR_PRIOR_THRESHOLD='):] )
         elif line.startswith('USE_ENSRF='):
            cfg.use_ensrf = get_bool_from_config( line.strip()[ len('USE_ENSRF='):] )
         elif line.startswith('PERFORM_ARCHIVE='):
            cfg.perform_archive = get_bool_from_config( line.strip()[ len('PERFORM_ARCHIVE='):] )

   #TODO : If warm_initialization, iterate thru run_top_dir to see which cycles can be skipped (and if cold start wrf can be skipped)
   
   cfg.start_date_str = cfg.start_date.get_date_str()
   cfg.end_date_str = cfg.end_date.get_date_str()
   sanity_check(cfg)
   return cfg

#### MAIN ###
def main():  
  cfg = read_config()
  print cfg.start_date.get_date_str()
  sanity_check(cfg)
  #strRunDate = '%s %s %s %s %s' %(cfg.run_date_tuple[0], cfg.run_date_tuple[1], 
  #                                cfg.run_date_tuple[2], cfg.run_date_tuple[3],  
  #                                cfg.run_date_tuple[4] )
  #cfg.run_date_tuple = time.strptime(strRunDate, "%d %m %Y %H %M")
  cfg.run_duration = cfg.run_length
  #create_or_verify_perts(cfg.start_date)
  
  #for pert in range(1, cfg.num_members+1):
    

if __name__ == '__main__':
   main()
