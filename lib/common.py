#!/usr/bin/env python

'''
Contains subroutines common to running GSI, EnKF, and coldstart experiments.
'''

import shutil
from time import sleep
import os
import sys
import random 
import xml.etree.ElementTree as ET
from optparse import OptionParser
import subprocess
import time
import xml.dom.minidom
from daffy_log import DaffyLog
import uuid
from timing import TimeStruct
from obs_processing import get_matching_ob_files

class ExperimentRunner:
   '''
   This class is used to encapsulate routines needed to facilitate running
   of experiments. 
   '''
   def get_log(self):
      return self.log
   def set_log(self, log):
      self.log = log
   def get_cfg(self):
      return self.cfg
   
# 
# VARS
#

DEFAULT_ROCOTO_VERBOSITY = '3' # just shows failures
# When determining the timestamp of observation files to be used for an experiment,
# if there is a disparity greater than this value, put a value of 'varies' in the 
# database, since this is a sign the the ob files used may not be as expected
OB_FILE_TIMESTAMP_THRESHOLD = ( 5 * 24 * 3600 )


#
# Functions
#
def get_yyyy_mm_dd_hh_mm(rundate):
   return time.strftime('%Y_%m_%d_%H_%M', time.localtime(rundate))

def _get_tmp_file(cfg):
   ''' Return temp file name, which will be named according to the experiment_id and put 
       in the cfg.rocoto_state_file_temp_location '''
   return os.path.join(cfg.rocoto_state_file_temp_location, cfg.experiment_id)
 
def get_rocoto_db_file(cfg):
   ''' 
   If necessary, move file to temporary location.
   Return name of file to be used.
   ''' 
   if cfg.lustre_rocoto_hack:
      ctr = 0
      while os.path.exists( os.path.join(cfg.rocoto_state_file_temp_location, cfg.experiment_id) ):
         sleep(0.5)
         ctr += 1
         if ctr > 100:
            print 'There appears to be a stale temporary state file [%s]' %_get_tmp_file(cfg)
            sys.exit(1)
      shutil.move(cfg.rocoto_db_path, cfg.rocoto_state_file_temp_location)
      rocoto_db_file = _get_tmp_file(cfg)
   else:
      rocoto_db_file = cfg.rocoto_db_path 
   return rocoto_db_file

def commit_rocoto_state_file(cfg):
   ''' If necessary, move temporary file back to original location '''
   if cfg.lustre_rocoto_hack:
      shutil.move( _get_tmp_file(cfg), cfg.rocoto_db_path )
      

def get_member_subdir(cfg, member_number):
   '''
   Given a <cfg> object (which encapsulates various experiment settings) and a 
   member number, return the subdirectory name for a given member
   '''
   return cfg.member_dir_prefix + '-' + str(member_number).zfill(cfg.num_digits)
      
      
#
# Methods for checking if static data is present
#
def check_static_ensemble_data_exists(experiment_runner):
   '''
   Look for static Real data for the ensemble forecasts
   If it does not exist in at least one cycle, terminate with exit code 89
   '''
   cfg = experiment_runner.get_cfg()
   log = experiment_runner.get_log()
   static_data_path = os.path.join(cfg.static_model_data_path, 'horizontal_interpolation', cfg.model_config_id, cfg.metgrid_checksum)
   
   for cycleDate in range(cfg.start_date.get_epochtime() , cfg.end_date.get_epochtime() + 1 , cfg.frequency ) :
      curr_atmos_dir = 'ATMOS.' + get_yyyy_mm_dd_hh_mm(cycleDate)
      required_data_paths = []
      member_dirs = [ cfg.member_dir_prefix + str(memNum).zfill(cfg.num_digits) for memNum in range(1, cfg.num_members + 1) ]  
      ensemble_nmmReal_output_paths = [ os.path.join(static_data_path, cfg.gfs_ensemble_id, curr_atmos_dir,  memberDir) for memberDir in member_dirs ]
      required_data_paths.extend( ensemble_nmmReal_output_paths )
      for model_data_path in required_data_paths:
         if not os.path.exists(model_data_path): 
            log.error('Specified path to static model data [%s] does not exist. Check your $MODEL_CONFIG_ID, $STATIC_DATA_PATH, $GFS_FORECAST_ROOT, and $GFS_ENSEMBLE_ROOT settings' %model_data_path)
            sys.exit(88)
            
         # Look for (possibly compressed) wrfinput and wrfbdy
         for fil in [ 'wrfinput_d01', 'wrfbdy_d01' ] :
            if not ( os.path.exists( os.path.join( model_data_path, fil) ) \
               or  os.path.exists( os.path.join( model_data_path, fil+'.gz') ) ):
                 log.error('Missing static Real data file for cycle %s (reading %s)' %(get_yyyy_mm_dd_hh_mm(cycleDate), model_data_path) )
                 sys.exit(89)
        
def check_static_geogrid_data_exists(experiment_runner):
   ''' Look for geo_nmm files '''
   cfg = experiment_runner.get_cfg()
   log = experiment_runner.get_log()
   geogrid_output_data_path = os.path.join( cfg.static_model_data_path, 'geogrid', cfg.model_config_id, cfg.geogrid_checksum)
   if not os.path.exists( os.path.join(geogrid_output_data_path, 'geo_nmm.d01.nc') ):
      log.error('Missing geogrid data for domain  %s looking in [%s]. Check your $MODEL_CONFIG_ID and $STATIC_DATA_PATH settings' %cfg.domain_name, geogrid_output_data_path )
      sys.exit(87)
   for i in range(1, cfg.max_dom) :
      filename = 'geo_nmm_nest.l0%i.nc' %i
      if not os.path.exists( os.path.join(geogrid_output_data_path, filename) )  :
         log.error('Missing geogrid data for domain %s, grid %i' %(cfg.domain_name, i+1) )
         sys.exit(86)
   
def check_static_deterministic_data_exists(experiment_runner):
   ''' Look for Real data from the deterministic forecasts '''
   cfg = experiment_runner.get_cfg()
   log = experiment_runner.get_log()
   model_data_path = os.path.join(cfg.static_model_data_path, 'horizontal_interpolation', cfg.model_config_id, cfg.metgrid_checksum, cfg.gfs_forecast_id)
   if not os.path.exists(model_data_path): 
      log.error('Specified path to static model data [%s] does not exist. Check your $MODEL_CONFIG_ID, $STATIC_DATA_PATH, and $GFS_FORECAST_ROOT settings.' %model_data_path)
      sys.exit(88)
      
   for cycleDate in range(cfg.start_date.get_epochtime() , cfg.end_date.get_epochtime() + 1 , cfg.frequency ) :
      atmos_subdir = 'ATMOS.' + get_yyyy_mm_dd_hh_mm(cycleDate)

      # Look for (possibly compressed) wrfinput and wrfbdy
      for fil in [ 'wrfinput_d01', 'wrfbdy_d01' ] :
         curr_real_file = os.path.join( model_data_path, atmos_subdir, fil )
         curr_real_file_gz = curr_real_file  + '.gz'
         if not ( os.path.exists( curr_real_file_gz ) or os.path.exists( curr_real_file ) ):
           log.error('Missing static Real data file for cycle %s (reading %s)' %(get_yyyy_mm_dd_hh_mm(cycleDate), curr_real_file) )
           sys.exit(85)        
           
def check_static_data_exists(experiment_runner):
   '''
   Look in the location specified by STATIC_MODEL_DATA_PATH in the config files to ensure
   that static data exists for all cycles, so we can safely skip those tasks..
   Static data consists of wrfbdy, wrfinput, and geo_nmm data. (The wrfinput data is used for boundary smoothing)
   If it does not exist in at least one cycle, terminate with exit code 85-89
   '''
   check_static_geogrid_data_exists(experiment_runner)
   check_static_deterministic_data_exists(experiment_runner)
   if experiment_runner.get_cfg().da_type == 'enkf':
      check_static_ensemble_data_exists(experiment_runner)
      
#
# Methods for checking if files for warm init are present
#
def check_for_gsi_experiment_warm_start_data(experiment_runner, next_restart_file):
      ''' Check for restart/wrfinput files in ATMOS dir and satbias files in GSI dir '''
      cfg = experiment_runner.get_cfg()
      log = experiment_runner.get_log()
      next_restart_path = os.path.join( cfg.run_top_dir , 'ATMOS.' + get_yyyy_mm_dd_hh_mm(cfg.start_date.get_epochtime()) , cfg.gfs_forecast_id, next_restart_file )
      if not os.path.exists( next_restart_path ) :
         log.error('File not found: %s' %(next_restart_path) ) 
         log.error('   For warm-init, the previous-cycle WRF input file must be in the run directory.')
         sys.exit(1)
   
      # now ensure the satellite data cyling files are there
      previous_gsi_date = cfg.start_date.get_epochtime()
      previous_gsi_path = os.path.join( cfg.run_top_dir , cfg.gsi_ges_subdir + '.' + get_yyyy_mm_dd_hh_mm(previous_gsi_date) )
      for fil in ('satbias_out', 'satbias_ang.out'):
         if not os.path.exists( os.path.join(previous_gsi_path, fil) ):
            log.error('File not found: %s ' %(os.path.join(previous_gsi_path, fil) ) )
            log.error('   For warm-init, the previous-cycle GSI satellite bias files must be in the run directory.')
            sys.exit(1)   

def check_for_enkf_experiment_warm_start_data(experiment_runner, next_restart_file):
   ''' Look for Real data for each member and for satellite bias thinning data '''
   cfg = experiment_runner.get_cfg()
   log = experiment_runner.get_log()
   for i in range(1, cfg.num_members + 1):
      next_restart_path = os.path.join( cfg.run_top_dir , 
                                       'ATMOS.' + get_yyyy_mm_dd_hh_mm(cfg.start_date.get_epochtime()) , 
                                       get_member_subdir(cfg, i), 
                                       next_restart_file )
      if not os.path.exists( next_restart_path ) :
         sys.stderr.write(':O File not found: %s \n' %(next_restart_path) ) 
         sys.stderr.write('   When doing a warm-init, the previous-cycle input file needs to be in the run directory. \n')
         sys.exit(1)
         
   # sat data thinning
   previous_gsi_satbias_dir = os.path.join(cfg.run_top_dir, cfg.gsi_ges_subdir + '.' + get_yyyy_mm_dd_hh_mm(cfg.start_date.get_epochtime()), 'data-thin.decisions')
   for fil in [ 'satbias_in', 'satbias_angle' ]:
      if not os.path.exists( os.path.join(previous_gsi_satbias_dir, fil) ):
         log.error('File not found: %s ' %(os.path.join(previous_gsi_path, fil) ) )
         log.error('   For warm-init, the previous-cycle GSI satellite bias files must be in the run directory.')
         sys.exit(1)   
         
   
def get_application_version(application_path):
   '''
   Attempt to read the version string of an application by reading the ".version" file in the
   given <application_path>. If it cannot be read, return 'Unknown'
   '''
   try:
      with open( os.path.join(application_path, '.version') ) as version_file:
         return version_file.readline()
   except IOError:
      return 'Unknown'


def warm_init_sanity_check(experiment_runner):
   '''
   Perform sanity check for a warm initialization (i.e. --warm-init option).
   Specifically, this routine will look for (1) ATMOS directory for the previous start date 
   (i.e. START_DATE - CYCLE_FREQUENCY) and the corresponding restart/wrfinput file
   and (2) GSI directory with satellite bias data
   '''
   cfg = experiment_runner.get_cfg()
   log = experiment_runner.get_log()
   if cfg.cold_init:
      print 'ERROR :: Must select either cold initialization OR warm initialization. Not both'
      sys.exit(1)
   # ensure that cold start date != start date
   if cfg.cold_start_date.get_epochtime() == cfg.start_date.get_epochtime():
      log.error('For warm init, cold start date should not be the same as start date. Check configuration')
      sys.exit(1)

   # Ensure restart file(s) exists
   # Note that the experiment's start_date is the actually the previous cycle's start date, since it's based on 
   # the time of the first guess
   warm_start_date = cfg.start_date.get_epochtime() + cfg.frequency 
   if cfg.da_file_type == 'wrfinput':
      next_restart_file = wrfutils.get_wrfinput_file_name(warm_start_date, domain=cfg.analysis_domain)
   elif cfg.da_file_type == 'wrfrst':
      next_restart_file = wrfutils.get_wrfrst_file_name(warm_start_date, domain=cfg.analysis_domain)
   
   if cfg.da_type == 'gsi':
      check_for_gsi_experiment_warm_start_data(experiment_runner, next_restart_file)
   elif cfg.da_type == 'enkf':
      check_for_enkf_experiment_warm_start_data(experiment_runner, next_restart_file)
   else:
      raise Exception('Unknown DA type!')

def cold_init_sanity_check(experiment_runner):
    '''
    Perform additional sanity checks for experiments that start from GFS
    '''
    cfg = experiment_runner.get_cfg()
    log = experiment_runner.get_log()
    # ensure that the start date is cold_start_date + cycle_frequency for cold init
    if cfg.cold_start_date.get_epochtime() != cfg.start_date.get_epochtime():
       log.error("For cold-start experiments, the start_date should equal the " \
                  "cold_start_date ")
       sys.exit(1)

def experiment_complete(db_file_name):
      '''
      See if experiment has completed. Currently, this implies that the 'archive' job has succeeded
      TODO: Account for workflows that do not perform archive job
      RETURNS
       True if experiment is complete, False otherwise
      '''
      import sqlite3 as sqlite
      conn = None
      try:
         conn = sqlite.connect(db_file_name)
         cursor  = conn.cursor()
         cursor.execute('SELECT  * from Jobs WHERE taskname="archive" and state="SUCCEEDED" ')
         results = cursor.fetchall()
         # Rocoto replaces previous (failed) entries corresponding to a job with the new state
         # and jobid, so we as long as we have more than one result we are good
         #print 'jza5', len(results)
         #if len(results) == 1:
         if len(results) > 0:
            return True
      except sqlite.Error, e:
         print 'SQLite error encountered:', e
         sys.exit(1)
      finally:
         if conn: conn.close()
      return False
      
def print_experiment_info(cfg, log):
   '''
   Print some information about the experiment to the user
   '''
   log.info('Generating workflow definition with the following settings:' )
   log.info('  Run Directory : %s' %cfg.run_top_dir )
   log.info('  DA Type: %s' %cfg.da_type) 
   log.info('  Boundary Conditions for Deterministic forecasts: %s' %cfg.gfs_forecast_id )
   if cfg.da_type == 'enkf':
      log.info('  Boundary Conditions for ensemble: %s' %cfg.gfs_ensemble_id )
   if cfg.da_type != 'coldstart':
      log.info('  Obs to assimilate: [%s]' %( ', '.join(map(str, cfg.gsi_data_this_experiment)) ) )
      log.info('  GSI DATA DIRECTORY %s: ' %cfg.gsi_obs_data_dir ) 
      log.info('  Output file for DA cycling : %s' %cfg.da_file_type)
   if cfg.da_file_type != 'wrfinput':
      log.warn('Selected restart for data assimilation, but this requires changes to the code if you want to spawn a nest. These changes were only made for 2012 HWRF. It is  recommended to use wrfinput') 

def parse_options(experiment_runner):
   '''
   Parse command line options. The values will be stored in the cfg option
   of the given <experiment_runner>, which is an ExperimentRunner
   
   '''
   parser = OptionParser()
   parser.add_option("-f", "--force", dest="force_execution", action='store_true', default=False,
      help='Force execution of experiment, even if directories exist' )
   parser.add_option("-r", "--reuse-cold", dest="reuse_static_data", default=False,
      help='Reuse existing data in LOCATION that does not change for different experiments.', action="store_true")
   parser.add_option("-m", "--monitor", action="store_true", dest="monitor_mode", default=False,
      help='Monitor mode: Do not add entry for Cron job, just monitor the experiment until SIGTERM is received.' )
   parser.add_option("-c", "--cold-init", action="store_true", dest="cold_init", default=False,
      help="Cold-start run. Generates workflow definition that starts with a cold start run that  initializes from GFS for the given start date." )
   parser.add_option("-w", "--warm-init", action="store_true", dest="warm_init", default=False,
      help="Warm Initialization. Generates workflow definition that skips the cold-start run. Looks in 'RUN_TOP_DIR' for the previous DA cycle's wrfin/wrfrst in the corresponding ATMOS directory." )
   parser.add_option("-v", "--rocoto-verbosity", dest="rocoto_verbosity", default=DEFAULT_ROCOTO_VERBOSITY,
      help="Value passed to Rocoto's -v option. Larger numbers will have more output. (e.g. 11 will show submission commands). Default=3, which just shows failures",
      metavar="ROCOTO_VERBOSITY")
   parser.add_option("-d", "--debug", dest="debug_mode", action="store_true", default=False,
      help="Enable debug mode. Currently, this sets the log level to 'debug' and enables 'set -x' in job scripts")

   (options, args) = parser.parse_args()
   cfg = experiment_runner.get_cfg()
   cfg.force_execution = options.force_execution
   cfg.reuse_static_data = options.reuse_static_data
   cfg.monitor_mode = options.monitor_mode
   cfg.cold_init = options.cold_init 
   cfg.warm_init = options.warm_init # This will skip the wrf_cold task in the namelist
   cfg.rocoto_verbosity = options.rocoto_verbosity
   cfg.debug_mode = options.debug_mode
   if cfg.warm_init : 
       warm_init_sanity_check(experiment_runner)
   elif cfg.cold_init:
       cold_init_sanity_check(experiment_runner)
   if cfg.reuse_static_data : 
      for i in range(1 , cfg.num_members + 1):
         #check_static_data_exists(cfg, get_member_subdir(cfg, i) )
         check_static_data_exists(experiment_runner)
   
   if cfg.debug_mode :
      experiment_runner.get_log().set_level(DaffyLog.DEBUG)
      cfg.debug_mode_str = 'TRUE'
   else:
      cfg.debug_mode_str = 'FALSE'
  
   # other sanity check
   if cfg.tcv_evaluation_domain > cfg.max_dom :
      experiment_runner.get_log().error('The TC Vitals evaluation domain ($TCV_DOMAIN) is bigger than the number of domains used in the forecast ($MAX_DOM)')
      sys.exit(13)

def get_daffy_revision():
   ''' 
   Determine the daffy revision. Try using svn command, if available.
   Otherwise, try getting from the .svn/entries file
   If that fails, return 'Unknown'
   '''
   try:
      p = subprocess.Popen("svnversion", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      (stdout, stderr) = p.communicate()
      daffy_revision = stdout[:-2] # remove 'M' at end
   except OSError:
      if os.path.exists('.svn/entries'):
         v1 = int( open('.svn/entries').readlines()[3].strip() )
         v2 = int( open('.svn/entries').readlines()[10].strip() )
         if v1 != v2:
            print 'unrecognized SVN entries file'
            sys.exit(13)
         daffy_revision = str(v1)
      else:
         log.error('Unable to determine SVN version. Will set to Unknown')
         daffy_revision = 'Unknown'
      # if there are modifications, SVN will return "rev:(rev+1)", but we may need to 
      # treat this value as a string, so instead convert to (rev+0.5)
      if daffy_revision.find(":") > -1: daffy_revision = daffy_revision[0:daffy_revision.find(":")] + '.5'
   return daffy_revision
      
def get_gsi_version(cfg):
   ''' 
   Determine the version of GSI used
   '''
   # First, look for a '.version' in the directory with a dirname
   if os.path.exists( os.path.join(cfg.gsi_root_dir, '.version') ):
      return open( os.path.join(cfg.gsi_root_dir, '.version') ).readline().strip()
   log.warn('No version string found in $GSI_ROOT/.version. Attempting to guess')
   # for comGSI, I name the directories such that the dirname is the version number
   if cfg.gsi_root_dir.contains('comgsi'):
      gsi_version = os.dirname(cfg.gsi_root_dir)

def get_enkf_version(cfg):
   '''
   Determine version of the EnKF package being used, by reading the ".version" file
   in the ENKF_ROOT (passed in as cfg.enkf_root)
   '''
   if os.path.exists( os.path.join(cfg.enkf_root, '.version') ):
      return open( os.path.join(cfg.enkf_root, '.version') ).readline().strip()
   log.warn('No version string found in $ENKF_ROOT/.version. Will set to "Unknown"')
   return "Unknown"
   
   
def add_node_with_text(parent_node, child_node_name, child_node_value):
   '''
   Add a child node with given name and value to <parent_node>.
   If <child_node_value> is not a string, try converting it to one
   '''
   if not isinstance(child_node_value, basestring): child_node_value = str(child_node_value)
   
   child_node = ET.SubElement(parent_node, child_node_name)
   child_node.text = child_node_value

def get_gsi_bkgerr_hzscl(gsi_namelist_path):
   ''' Get the hzscl parameter set in the GSI template '''
   for line in open(gsi_namelist_path).readlines():
      toks = line.split('=')
      if toks[0].strip() == 'hzscl':
         return toks[1].strip()
   raise Exception('Did not find hzscl entry in namelist')
   
def get_first_da_ymdhm(cfg):
   '''
   Determine the date of first data assimilation as a YYYYMMDDhhmm string.
   ASSUMPTION: The first DA is Start_date  + cycle_frequency
   '''
   first_da_date = cfg.start_date.get_epochtime() + cfg.frequency 
   #log.warn('In creating config.xml, assuming first_da_date == start_date + cycle_frequency')
   return TimeStruct(first_da_date).get_ymdhm()

def get_obfile_modification_date(data_path, file_pattern, start_date, end_date, cycle_frequency, logger=None, sporadic=False):
   '''
   Determine the modification date of observation files in <data_path> matching <data_pattern> in the
   range of dates specified by <start_date> and <end_date>. The latter two should be YYYYMMDDhhmm 
   RETURN the average of the time stamps in YYYYMMDDhhmm form. However, if the modification time stamp
   differs by more than OB_FILE_TIMESTAMP_THRESHOLD, return the string "varies". The idea that data should not take more than
   5 days to generate, and we do not want to have data that was generated too far apart as that is a red
   flag as far as the version of the data.
   Optional Args:
      logger - A log-like object to use to display warnings (If not passed in, print to stdout)
      sporadic - If a matching file is not found and this is False, issue a warning
   
   '''
   if len(start_date) != 12 or len(end_date) != 12:
      raise Exception("<start_date> and <end_date> should be in YYYYMMDDhhmm format. Values given are %s and %s" %(start_date, end_date) )
   sum = 0
   ctr = 0
   most_recent_timestamp = 0
   oldest_timestamp = 999999999999
   startEpoch = int( time.mktime( time.strptime(start_date, '%Y%m%d%H%M') ) )
   endEpoch = int( time.mktime( time.strptime(end_date, '%Y%m%d%H%M') ) )
   for currCycle in range(startEpoch, endEpoch, cycle_frequency):
      matching_files = get_matching_ob_files(data_path, file_pattern, time.localtime(currCycle), logger)
      for filename in matching_files:
         if not os.path.exists( os.path.join(data_path, filename) ) and not sporadic:
            if logger:
               logger.warn_once( 'Observation file does not exist [%s]. Is this expected?' % os.path.join(data_path, filename) )
            else:
               print 'Observation file ile does not exist [%s]. Is this expected?' % os.path.join(data_path, filename)
         else:
            mod_time = os.stat( os.path.join(data_path, filename) ).st_mtime
            if mod_time > most_recent_timestamp:
               most_recent_timestamp = mod_time
            if mod_time < oldest_timestamp:
               oldest_timestamp = mod_time
            sum += mod_time
            ctr += 1
   avg = sum / ctr
   #if abs( time.mktime(time.strptime(start_date, '%Y%m%d%H%M')) - time.mktime(time.localtime(avg)) ) > (5 * 24 * 3600 ) :
   if most_recent_timestamp - oldest_timestamp > OB_FILE_TIMESTAMP_THRESHOLD:
      if logger:
         #pretty_time = lambda  t : time.strftime('%Y-%m-%d %H:%M', time.gmtime(t))
         pretty_time = lambda  t : time.strftime('%m/%d/%Y', time.gmtime(t))
         logger.warn_once('Disparity in modification date for obs matching ' \
                          'pattern "%s". Ensure that you are using the ob ' \
                          'files you intend to. Oldest: %s, Newest: %s' 
                          %(file_pattern, 
                            pretty_time(oldest_timestamp), 
                            pretty_time(most_recent_timestamp)))
      return 'varies'
   else:
      return time.strftime('%Y%m%d%H%M', time.localtime(avg))


def add_observations_to_xml(experiment_runner, parent_node):
   '''
   Determine observations assimilated (in `cfg`) and add XML nodes for each one.
   This method will add an <observation_configuration> tag for each element in 
   cfg.gsi_data_this_experiment, which corresponds to the value entered in 
   experiment.cfg.sh. For each <observation_configuration>, add <observation>
   nodes containing the elements in the corresponding observation_configuration's
   cfg file in gsi_ob_mappings
   '''
   cfg = experiment_runner.get_cfg()
   logger = experiment_runner.get_log()
   for obCfg in cfg.gsi_data_this_experiment:
      obs_cfg_node = ET.SubElement(parent_node, 'observations_configuration')
      obs_cfg_node.set('name', obCfg)
      try:
         ob_cfg_file = open( os.path.join(cfg.gsi_obs_cfg_topdir, obCfg + '.cfg'), 'r')
      except:
         logger.error('Unable to open observation configuration file: %s' %ob_cfg_file.name)
         sys.exit(13)
      for line in ob_cfg_file.readlines():
         data = line.split()
         if line.startswith('#') or len(data) == 0: continue
         ob_node = ET.SubElement(obs_cfg_node, 'observation')
         if len(data) != 4:
            sys.stderr.write('Unsupported line:\n\n%s\n\nAn entry is required for each of the 4 columns and not additional whitespace is allowed\n' %line )
            sys.exit(2)
         ob_node.set('gsi_target_file', data[0] )
         ob_node.set('tag', data[1])
         ob_node.set('data_path', data[2])
         ob_node.set('file_pattern' , data[3])
         if data[1] in cfg.sporadic_datasets: sporadic = True
         else: sporadic = False
         ob_node.set('obfile_modification_date', get_obfile_modification_date(data[2].replace('[GSI_DATA_TOPDIR]', cfg.gsi_obs_data_dir) , data[3], cfg.start_date.get_ymdhm(), cfg.end_date.get_ymdhm(), cfg.frequency, logger, sporadic ) )
      ob_cfg_file.close()
     

def get_experiment_uuid():
   # TODO: This should be a persistent field of the ExperimentRunner object
    expt_id = open( '.experiment_id').readline().strip()
    if len(expt_id) < 10:
       log.error('Found experiment ID file (.experiment_id), but it appears to be invalid. You may want to simply delete it')
       sys.exit(1)
    return expt_id

def commit_to_local_database(experiment_runner):
  
   log = experiment_runner.get_log()
   cfg = experiment_runner.get_cfg()

   if not os.path.exists('.experiment_id'):
      expt_id =  str(uuid.uuid1().int)
      open('.experiment_id', 'w').write( expt_id )
   else:
      expt_id = get_experiment_uuid()
      log.info_once("Found existing experiment ID %s" %expt_id)
      
   root = ET.Element('experiment')
   root.set('da_type', cfg.da_type)
   root.set('id', cfg.experiment_id)
   root.set('uuid', expt_id)
   # add basic data
   #node = ET.SubElement(root, 'start_date') node.text = cfg.start_date
   add_node_with_text(root, 'spinup_date', cfg.start_date.get_date_str() )
   add_node_with_text(root, 'first_data_assimilation_date', get_first_da_ymdhm(cfg) ) 
   add_node_with_text(root, 'end_date', cfg.end_date.get_date_str() )
   add_node_with_text(root, 'cycle_frequency', cfg.frequency)
   add_node_with_text(root, 'forecast_frequency', cfg.forecast_frequency) 
   add_node_with_text(root, 'forecast_duration', cfg.forecast_duration)
   add_node_with_text(root, 'user', os.environ['USER'])
   add_node_with_text(root, 'daffy_revision', get_daffy_revision() )
   add_node_with_text(root, 'supercomputer', cfg.supercomputer)
   add_node_with_text(root, 'experiment_execution_directory', cfg.top_dir)
   add_node_with_text(root, 'experiment_run_directory', cfg.run_top_dir)
   if cfg.perform_archive and os.path.exists( os.path.join(cfg.run_top_dir, 'mss_directory.txt')) :
      with open( os.path.join(cfg.run_top_dir, 'mss_directory.txt'), 'r' ) as mssFile:
         add_node_with_text(root, 'experiment_archive_directory', mssFile.readline() )
   # add subelement with model data
   model_node = ET.SubElement(root, 'model')
   wrf_version = open( os.path.join(cfg.wrf_dir, 'README')).readline().split()[3]
   add_node_with_text(model_node, 'hwrf_version', wrf_version)
   add_node_with_text(model_node, 'gfs_data_root', cfg.gfs_data_root)
   add_node_with_text(model_node, 'deterministic_forecast_gfs_data_id', cfg.gfs_forecast_id)
   add_node_with_text(model_node, 'ensemble_forecast_gfs_data_id', cfg.gfs_ensemble_id)
   add_node_with_text(model_node, 'hwrf_namelist_template', cfg.wrf_namelist_template)
   
   # add subelement with postproc data
   postproc_node = ET.SubElement(root, 'postprocessing')
   add_node_with_text(postproc_node, 'unipost_version', get_application_version(cfg.upp_root) )
   add_node_with_text(postproc_node, 'diapost_version', get_application_version(cfg.diapost_root) )

   # add subelement with domain data
   domain_node = ET.SubElement(root, 'domain')
   domain_node.set('name', cfg.domain_name)
   gesFcst_node = ET.SubElement(domain_node, 'firstguess_configuration')
   add_node_with_text(gesFcst_node, 'time_step', cfg.time_step)
   # TODO: config.xml assumes that the ges will not use a nest (and detFcst will use max_dom in conf)
   for domIdx in range(1):
     grid_node = ET.SubElement(gesFcst_node, 'grid')
     add_node_with_text(grid_node, 'dx', '%.2f' %cfg.dx[domIdx] )
     add_node_with_text(grid_node, 'dy', '%.2f' %cfg.dy[domIdx] )
     add_node_with_text(grid_node, 'grid_size_we', cfg.e_we[domIdx])
     add_node_with_text(grid_node, 'grid_size_sn', cfg.e_sn[domIdx])
     add_node_with_text(grid_node, 'num_vertical_levels', cfg.num_vertical_levels[domIdx])
   
   detFcst_node = ET.SubElement(domain_node, 'deterministic_forecast_configuration')
   add_node_with_text(detFcst_node, 'tcvitals_for_nest_path', cfg.tc_vitals_for_model)
   add_node_with_text(detFcst_node, 'time_step', cfg.time_step)
   for domIdx in range(cfg.max_dom):
      grid_node = ET.SubElement(detFcst_node, 'grid')
      add_node_with_text(grid_node, 'dx', '%.2f' %cfg.dx[domIdx] )
      add_node_with_text(grid_node, 'dy', '%.2f' %cfg.dy[domIdx] )
      add_node_with_text(grid_node, 'grid_size_we', cfg.e_we[domIdx])
      add_node_with_text(grid_node, 'grid_size_sn', cfg.e_sn[domIdx])
      add_node_with_text(grid_node, 'num_vertical_levels', cfg.num_vertical_levels[domIdx])
      
   # add data assimilation information
   if cfg.da_type in ('enkf', 'gsi', 'hybrid'):
         
      da_node = ET.SubElement(root, 'data_assimilation')
      # ... put general data assimilation information
      add_node_with_text(da_node, 'gsi_version', get_gsi_version(cfg) )
      add_node_with_text(da_node, 'gsi_namelist_template', cfg.gsi_namelist_template) # we can cross reference with DAFFY-version
      add_node_with_text(da_node, 'analysis_domain', cfg.analysis_domain)
      add_node_with_text(da_node, 'multi_time_level_analysis', cfg.multi_time_level_analysis)
      add_node_with_text(da_node, 'satinfo_file', cfg.satinfo_file)
      add_node_with_text(da_node, 'convinfo_file', cfg.convinfo_file)
      if cfg.multi_time_level_analysis:
         add_node_with_text(da_node, 'number_of_time_levels', cfg.num_time_levels)
      add_node_with_text(da_node, 'perform_satellite_thinning', cfg.perform_satellite_thinning)   
      # ... then information about the observations used
      add_node_with_text(da_node, 'observations_data_root', cfg.gsi_obs_data_dir)
      obs_node = ET.SubElement(da_node, 'observations')
      add_observations_to_xml(experiment_runner, obs_node)
      
      # ... then information specific to the data assimilation type used
      if cfg.da_type == 'gsi':
         # since GSI is also used with EnKF, only put GSI _analysis_ related things here
         gsi_node = ET.SubElement(da_node, 'gsi_analysis_configuration')
         add_node_with_text(gsi_node, 'background_error_horizontal_scale', get_gsi_bkgerr_hzscl(cfg.gsi_namelist_template) )
         add_node_with_text(gsi_node, 'assimilation_time_window', cfg.assimilation_time_window)
         add_node_with_text(gsi_node, 'background_error_stats_file', cfg.background_error_stats_file)
      elif cfg.da_type == 'enkf':
         enkf_node = ET.SubElement(da_node, 'enkf_configuration')
         add_node_with_text(enkf_node, 'enkf_version', get_enkf_version(cfg))
         add_node_with_text(enkf_node, 'enkf_path', cfg.enkf_root)
         add_node_with_text(enkf_node, 'namelist_template', cfg.enkf_namelist_template)
         add_node_with_text(enkf_node, 'adaptive_posterior_inflation_nh', cfg.adaptive_posterior_inflation_nh)
         add_node_with_text(enkf_node, 'adaptive_posterior_inflation_sh', cfg.adaptive_posterior_inflation_sh)
         add_node_with_text(enkf_node, 'adaptive_posterior_inflation_tropics', cfg.adaptive_posterior_inflation_tropics)
         add_node_with_text(enkf_node, 'min_inflation', cfg.min_inflation)
         add_node_with_text(enkf_node, 'max_inflation', cfg.max_inflation)
         add_node_with_text(enkf_node, 'horizontal_localization_nh', cfg.horizontal_localization_nh)
         add_node_with_text(enkf_node, 'horizontal_localization_sh', cfg.horizontal_localization_sh)
         add_node_with_text(enkf_node, 'horizontal_localization_tropics', cfg.horizontal_localization_tropics)
         add_node_with_text(enkf_node, 'observation_time_localization', cfg.observation_time_localization)
         add_node_with_text(enkf_node, 'vertical_localization_nh_convobs', cfg.vertical_localization_nh_convobs)
         add_node_with_text(enkf_node, 'vertical_localization_sh_convobs', cfg.vertical_localization_sh_convobs)
         add_node_with_text(enkf_node, 'vertical_localization_tropics_convobs', cfg.vertical_localization_tropics_convobs)
         add_node_with_text(enkf_node, 'vertical_localization_nh_satobs', cfg.vertical_localization_nh_satobs)
         add_node_with_text(enkf_node, 'vertical_localization_sh_satobs', cfg.vertical_localization_sh_satobs)
         add_node_with_text(enkf_node, 'vertical_localization_tropics_satobs', cfg.vertical_localization_tropics_satobs)
         add_node_with_text(enkf_node, 'vertical_localization_nh_psobs', cfg.vertical_localization_nh_psobs)
         add_node_with_text(enkf_node, 'vertical_localization_sh_psobs', cfg.vertical_localization_sh_psobs)
         add_node_with_text(enkf_node, 'vertical_localization_tropics_psobs', cfg.vertical_localization_tropics_psobs)
         add_node_with_text(enkf_node, 'inflation_smoothing_parameter', cfg.inflation_smoothing_parameter)
         add_node_with_text(enkf_node, 'enkf_satbias_iterations', cfg.enkf_satbias_iterations)
         add_node_with_text(enkf_node, 'posterior_prior_threshold', cfg.posterior_prior_threshold)
         add_node_with_text(enkf_node, 'use_ensrf', cfg.use_ensrf)
         if cfg.perform_enkf_additive_inflation:
            add_node_with_text(enkf_node, 'additive_inflation_coefficient', cfg.additive_inflation_coeff)
         # TODO  gotta add ENKF_ADDITIVE_INFLATION_COEFF if PERFORM_ENKF_ADDITIVE_INFLATION=TRUE^C(INFO) 
   # TODO: This should be set on the first invocation only
   # -> It's not really necessary though; since there is no trail of config changes the completion time is sufficient
   #t = time.localtime()
   #add_node_with_text(root, 'experiment_init', '%s/%s/%s' %(t.tm_mon, t.tm_mday, t.tm_year) )
   
   # Output to file. Condense subdirectories of top_dir or run_top_dir
   out = ET.tostring(root)
   xmlOut = xml.dom.minidom.parseString(out)
   xmlText = xmlOut.toprettyxml()
   with open(cfg.local_database_file_name, 'w') as xmlFile:
      for line in xmlText.splitlines():
         if line.strip() != cfg.top_dir: 
            line = line.replace(cfg.top_dir, '[EXPERIMENT_TOPDIR]')
         if line.strip() != cfg.run_top_dir: 
            line = line.replace(cfg.run_top_dir, '[EXPERIMENT_RUNDIR]')
         line = line.replace(cfg.static_data_root, '[STATIC_DATA_ROOT]')
         line = line.replace(cfg.apps_root, '[APPS_ROOT]')
         xmlFile.write(line + '\n')

   # "ugly" output
   #tree = ET.ElementTree(root)
   #tree.write("experiment.xml")

def get_global_database_file(cfg):
   '''
   Determine and return the path to the global database file. The scheme for this is to 
   find the oldest file in the `cfg.global_database_path` based on file name and return it.
   If the cfg.global_database_path is empty, create a file called 'experiments.xml' with just
   the outter tags.
   '''
   if not os.path.exists(cfg.global_database_path):
      print 'Path to global database does not exist: %s' %cfg.global_database_path
      sys.exit(1)
   contents = os.listdir(cfg.global_database_path)
   if len(contents) == 0: 
      # create new database file if none exists
      with open( os.path.join(cfg.global_database_path, 'experiments.xml'), 'w') as global_db:
         global_db.write('<daffy_experiments>\n</daffy_experiments>\n')
         return os.path.join(cfg.global_database_path, 'experiments.xml')
   else:
      # return most recent one
      contents.sort()
      idx = -1
      if contents[idx] == 'experiments.xml': idx = -2
      return os.path.join(cfg.global_database_path, contents[idx])


def add_to_global_database(cfg):
  '''
  Merge this experiment into the global experiment database. The current scheme
  will create a copy of the latest global database (based on timestamp in filename)
  and name it with the current timestamp. The current experiment's local XML file
  will be merged into this new file. 
  The new file will be written to the `cfg.global_database_path`. 
  The merge will be skipped if the UUID is found in the global database. This 
  can occur if you copy the exec folder to run a new experiment. 
  '''
  # get root of local db and add the <experiment_completion> tag
  local_db_root = ET.parse(cfg.local_database_file_name).getroot()
  t = time.localtime()
  add_node_with_text(local_db_root, 'experiment_completion', '%s%s%s%s%s' %(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min) )

  # check for duplicate experiment UUID in global database
  global_experiment_database = get_global_database_file(cfg)
  for exptNode in ET.parse(global_experiment_database).findall(".//experiment"):
    if 'uuid' in exptNode.attrib:
      if exptNode.attrib['uuid'] == get_experiment_uuid():
        print 'Experiment ID already exists in database! Another one must be generated to merge' \
              'this experiment in the global database. You can regenerate one by removing the .experiment_id file'
        sys.exit(13)
    else:
      print 'WARN :: "uuid" attribute not found for an entry in the global database'

  # Append experiment node from local experiment XML file to the global XML file    
  globalRoot = ET.parse(global_experiment_database).getroot()
  globalRoot.append(local_db_root)

  # Write to global database  
  out = ET.tostring(globalRoot)
  xmlOut = xml.dom.minidom.parseString(out)
  xmlText = xmlOut.toprettyxml()
  new_global_root = os.path.join(cfg.global_database_path, 'experiments-' + str(int(time.time())) + '.xml')
  with open(new_global_root, 'w') as xmlFile:
    out = ET.tostring(globalRoot)
    xmlOut = xml.dom.minidom.parseString(out)
    xmlText = xmlOut.toprettyxml()
    for line in xmlText.splitlines():
      if not line.isspace():  xmlFile.write(line + '\n')

