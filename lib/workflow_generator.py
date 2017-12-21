#!/usr/bin/env python
##
# Contains routines for generating XML files that can be used to run workflows
# using the Rocoto workflow engine.
# The main routines we use are
#  generate_gsi_workflow - to generate an XML workflow file for a GSI experiment
#  generate_ens_workflow - to genreate an XML workflow file for an ensemble-based experiment
# For EnKF runs, the metatask name will be the equivalent GSI task name. The individual
# members' task names will be the equivalent GSI task name plus a suffix of "_m#member#"
##

import xml.etree.ElementTree as ET
import os
import xml.dom.minidom
import time
from cfg import read_config , TimeStruct 
from optparse import OptionParser
import sys

g_wps_job_script_name = '&SCRIPTS_DIR;/wps.zsh'
g_real_job_script_name = '&SCRIPTS_DIR;/real.zsh'
g_wrf_job_script_name = '&SCRIPTS_DIR;/wrf.zsh'
g_gsi_job_script_name = '&SCRIPTS_DIR;/gsi.zsh'
g_postproc_job_script_name = '&SCRIPTS_DIR;/postproc_cycle.zsh'
g_diapost_fcst_job_script_name = '&SCRIPTS_DIR;/diapost_fcst.zsh'
g_upp_fcst_job_script_name = '&SCRIPTS_DIR;/upp_fcst.zsh'
g_postproc_fcst_job_script_name = '&SCRIPTS_DIR;/postproc_fcst.zsh'
g_dummy_gsi_dep_script_name = '&SCRIPTS_DIR;/dummy.sh'
g_additive_inflation_job_script_name = '&SCRIPTS_DIR;/additive_inflation.zsh'
g_enkf_job_script_name = '&SCRIPTS_DIR;/enkf.zsh'
g_enkf_analysis_upp_job_script = '&SCRIPTS_DIR;/post/unipost_enkf_analysis.zsh'
g_enkf_prior_upp_job_script = '&SCRIPTS_DIR;/post/unipost.enkf.prior.zsh'
g_cleanup_job_script = '&SCRIPTS_DIR;/cleanup_cycle.zsh'
g_archive_job_script = '&SCRIPTS_DIR;/archive.zsh'
g_expt_postproc_job_script_name = '&SCRIPTS_DIR;/postproc_experiment.zsh'
g_gfdl_tracker_job_script_name = '&SCRIPTS_DIR;/gfdl_tracker.zsh'

g_log_dir = '&RUN_DIR;/log' # os.path.join(g_run_top_dir , 'log')
g_rocoto_log_basedir = '&LOGS;'
# suffix used for log files
LOG_FILE_SUFFIX = '@Y@m@d@H@M.log'

#g_gfs_fcst_frequency = 6 * 3600 # seconds

#g_real_frequency = g_gfs_fcst_frequency # may need to change for bdy smoothing

#g_forecast_frequency = 3 * 3600

WPS_CYCLEDEF_NAME = 'gfs_boundaries'
REAL_CYCLEDEF_NAME = 'real'
WRFGSI_CYCLEDEF_NAME = 'steady_state'
SPINUP_CYCLEDEF_NAME = 'spinup'
# Don't necessarily want to run forecat every cycle
FORECAST_CYCLEDEF_NAME = 'forecast'
LAST_CYCLE_CYCLEDEF_NAME = 'last_cycle'

HWRF_SPINUP_TASK_NAME = 'hwrf_ges_spinup'
WPS_TASK_NAME = 'wps'
WPS_ENSEMBLE_METATASK_NAME = 'wps_ensemble'
WPS_TASK_NAME = 'wps'
REAL_TASK_NAME = 'real'
REAL_ENSEMBLE_METATASK_NAME = 'real_ensemble'
REAL_TASK_NAME = 'real'
HWRF_DETERMINISTIC_FCST_TASK_NAME = 'hwrf_fcst'
HWRF_GES_TASK_NAME = 'hwrf_ges'
GSI_TASK_NAME = 'gsi'
ENKF_TASK_NAME = 'enkf'
# script that runs UPP on ensemble posteriors
ENSEMBLE_ANALYSIS_UPP_TASK_NAME = 'enkf_anl_upp'
# script that runs UPP on ensemble priors
ENSEMBLE_PRIOR_UPP_TASK_NAME = 'enkf_ges_upp'
# task that runs additive inflation after EnKF
ADDITIVE_INFLATION_TASK_NAME = 'additive_inflation'
# This is the post-processing that is done after each cycle
POSTPROC_CYCLE_TASK_NAME = 'post_cycle'
# This is the post-procesisng that is done after forecasts
POSTPROC_FCST_TASK_NAME = 'post_fcst'
# This is the Diapost task that postprocesses deterministic forecast output
DIAPOST_FCST_TASK_NAME = 'diapost_fcst'
# This is the UPP task that postprocesses deterministic forecast output
UPP_FCST_TASK_NAME = 'upp_fcst'
# Dummy task to satisfy "cold start" GSI dependency if starting from a warm start
DUMMY_GSI_DEP_NAME = 'dummy'
GSI_ENSMEAN_TASK_NAME = 'gsi_ensmean'
# Script to remove data that cannot be removed during other jobs due to parallel dependencies
CLEANUP_TASK_NAME = 'cleanup' # TODO : add to service queue
# Script that archives the experiment after everything else has completed
ARCHIVE_TASK_NAME = 'archive'
# Script that does the final postprocessing
EXPERIMENT_POSTPROC_TASK_NAME = 'post_expt'
# Script that runs the GFDL vortex tracker
GFDL_TRACKER_TASK_NAME = 'gfdltrk'

# max number of concurrent cycles 
#NOTE: for ensemble experiments, can't keep this to high. 7 is fine for 30 members)
CYCLE_THROTTLE = '2'
# Number of tries before considering a job failed
MAXTRIES = '3' # ET doesn't autoconvert to string!

# TODO : put these into some kind of config file
RESERVATION_ACCOUNT_NAME = 'rthur-aoml'
RESERVATION_QUEUE_NAME = 'rttjet'
RESERVATION_PARTITION_NAME = '-l partition=tjet'
SERVICE_QUEUE_NAME = 'service'
BIGMEM_QUEUE_NAME = 'bigmem'

# Set mappings of tasks to accounts. If a task does not have a mapping here, use the DEFAULT_ACCOUNT_NAME
g_task_account_mappings = {} # { HWRF_DETERMINISTIC_FCST_TASK_NAME : RESERVATION_ACCOUNT_NAME }
# Set mappings of tasks to queues. If a task does not have a mapping, use the queue specified in the config
g_task_queue_mappings = { ARCHIVE_TASK_NAME : SERVICE_QUEUE_NAME } # { HWRF_DETERMINISTIC_FCST_TASK_NAME : RESERVATION_QUEUE_NAME }
# Set mappings of tasks to queues. If a task does not have a mapping, use the mapping specified in the config if it exists
g_task_partition_mappings = {} # { HWRF_DETERMINISTIC_FCST_TASK_NAME : RESERVATION_PARTITION_NAME }

def zeropad(number, num_digits):
   ''' Pad <number> so that it is a string of length <num_digits> '''
   if number > pow(10, num_digits): raise Error
   currLen = len( str(number) )
   num_zeros = num_digits - currLen
   padding = ''
   for i in range(num_zeros): padding += '0'
   return padding + str(number)

# TODO : Get these from config file
def get_wrf_num_cores():
   return str(196) # with nest, ask for 196

def get_wrf_walltime(fcst_time=3600):
   '''
   TODO: More sophisticated execution time prediction
   PARAMS
     fcst_time : time in seconds of forecast
   '''
   # with current THECUT, non-nested domain, it takes about 1.5 minutes per hour of output
   # (i.e. 90 secs computation time per 3600 secs simulation time, but we'll use 120 to be safe)
   # updated for tJet/uJet
   est = cfg.max_dom * int( ( 70.0/3600) * fcst_time ) + 600 # add 10 minutes  for bdy update/warmup/data transfer/slowness
   return est

def get_wps_num_cores():
   return str(8)

def get_wps_walltime():
   return str(1500)

def get_real_num_cores():
   return str(16)

def get_real_walltime():
   return str(3600)

def get_gsi_num_cores():
   # !! Mingjing's GSI does not work with more than 96 cores on Pegasus !!
   return str(96)

def get_additive_inflation_num_cores():
   return str( cfg.num_members + 1 )

def get_enkf_num_cores():
   #return str(cfg.num_members * 5) # TODO: Optimize
   return 196 # works much better for 30 members

def get_gsi_walltime():
   return str(1000)

def get_postproc_num_cores():
   return str(8)

def get_postproc_walltime():
   return str(1800)

def get_additive_inflation_walltime():
   return str(1700)

def get_enkf_walltime():
   return str( 3600 + (cfg.num_members * 10 * 60) ) # TODO: Optimize

def get_archive_task_duration():
   # TODO : MAKE this smarter
   return 4 * 60 * 60

def get_diapost_fcst_walltime():
   # TODO: Optimize. Setting to the max for 3km run
   return str(8 * 3600)
def get_diapost_fcst_num_cores():
   return str(2)

def get_upp_fcst_walltime():
   return str(2 * 3600)
def get_upp_fcst_num_cores():
   return str(2)

def get_postproc_fcst_walltime():
   # TODO: estimate walltime. Currently, it's taking 50-60 seconds per output
   # KIM: we can parallize the generation of outputs
   return str(3 * 3600) # Update : Increased for HEDAS Diapost (TODO: Optimize)

def get_gfdl_tracker_walltime():
   return str(3 * 3600)

def get_gfdl_tracker_num_cores():
   return str(2)

def get_expt_postproc_task_duration():
   # TODO: fIGURE THIS out
   return str(1500)


def get_wps_workdir():
   #return '&RUN_DIR;' + cfg.wps_subdir + '.@Y@m@d@H@M'
   return '&RUN_DIR;/' + 'WPSV3' + '.@Y@m@d@H@M'

def get_atmos_dir():
   return '&RUN_DIR;/' + 'ATMOS' + get_wrf_dir_suffix_cyclestr()

def seconds2dhms(input_seconds):
   ''' Convert a value from seconds to the DD:HH:MM:SS format expected by Rocoto '''
   secs = input_seconds % 60
   mins = (input_seconds / 60) % 60
   hours = input_seconds / 3600
   if hours >= 24:
      days = hours / 24
      hours = hours % 24
   else:
      days = 0
   [d,h,m,s] = [ zeropad(x,2) for x in [days, hours, mins, secs] ]
   return '%s:%s:%s:%s' %(d, h, m, s)


def entity(varname, value):
   return '<!ENTITY %s "%s" >' %(varname, value)

def cyclestr(text, offset=None):
   ''' 
   Wrap given text around <cyclestr> tags. Add and offset attribute if passed in.
   This was needed since we can't wrap XML tags inside the text portion of an
   element iwth ElementTree
   '''
   xmlstr = '<cyclestr'
   if offset !=None: xmlstr += ' offset="' + offset + '"'
   xmlstr += '>' + text + '</cyclestr>'
   return xmlstr

def add_entities(outfile):
   outfile.write("<!DOCTYPE workflow\n[\n")
   outfile.write( entity('TOP_DIR', cfg.top_dir) + '\n')
   outfile.write( entity('RUN_DIR', cfg.run_top_dir) + '\n')
   outfile.write( entity('LOG_DIR', g_log_dir) + '\n')
   outfile.write( entity('SCRIPTS_DIR', cfg.job_scripts_dir) + '\n' )
   outfile.write( entity('WPS_GFS_FCST_DURATION', cfg.wps_gfs_fcst_duration) + '\n')
   outfile.write( entity('FCST_DURATION', cfg.forecast_duration) + '\n')
   outfile.write( entity('CYCLE_FREQUENCY', cfg.frequency) + '\n' )
   outfile.write( entity('ACCOUNT', cfg.batch_system_account) + '\n')
   outfile.write( entity('PARTITION', cfg.batch_system_partition) + '\n')
   outfile.write( entity('CFG_FILE_PATH', cfg.config_file_path) + '\n')
   outfile.write( entity('GFS_ENSEMBLE_FORECAST_DURATION', cfg.gfs_ensemble_forecast_duration) + '\n')
   outfile.write("]>\n")


def add_wf_log(rootnode, subdir):
   ''' Add a <log><cyclestr> tag to rootnode with the parameter [g_rocoto_log_basedir]/subdir '''
   #<log><cyclestr>/home/Javier.Delgado/rocoto/basic4_@Y@m@d@H@M.log</cyclestr></log>
   log = ET.SubElement(rootnode, 'log')
   cyclestr = ET.SubElement(log, 'cyclestr')
   log_file = '&LOG_DIR;' + '/' + subdir
   cyclestr.text = log_file # os.path.join(g_log_dir, log_file)

def add_task_log(parent_node, task_name, log_suffix, ensemble=False):
   ''' 
   Add a <join><cyclestr> tag to node with the parameter [g_rocoto_log_basedir]/<task_name>
   If <ensemble> is True AND DA_TYPE is 'enkf', append "_m#member#_" to the 
    file name (s. that there is a log file for each member.
   The <log_suffix> will be added to each filename as a suffix   
   '''
   log = ET.SubElement(parent_node, 'join')
   cyclestr = ET.SubElement(log, 'cyclestr')
   if ensemble and cfg.da_type == 'enkf':
      file_name = task_name + "_m#member#_" + log_suffix
   else: # assume either GSI or non-ensemble task
      file_name = task_name + "_" + log_suffix
   log_file = '&LOG_DIR;' + '/' + task_name + '/' + file_name
   cyclestr.text = log_file 


def get_wrf_dir_suffix_cyclestr():
   return '.@Y_@m_@d_@H_@M'

def get_wrf_dir_suffix(ts):
   ''' Return the wrf_dir suffix corresponding to the date encapsulated
       in <ts>, which is a TimeStruct (see cfg.py) '''
   return '%s_%s_%s_%s_%s' %(ts.year, ts.month, ts.day, ts.hour, ts.minute)
   

def add_job_params_to_task(tasknode, num_cores, taskname, jobname, walltime, account='&ACCOUNT;', queue='') :
   ''' Add the <account>, <cores>, <queue>, and <walltime> attributes to the passed in
       task node.
       PARAMS
        - tasknode - the task Element we're appending to
        - cores - the number of cores to use
        - walltime (integer) - wall clock time in seconds 
        - taskname - Internal name for the task. (This name is the same regardless of experiment type)
        - jobname - the name of the job (passed to the scheduler; will automatically be wrapped in <cyclestr>; this name may be different depnding on whether its an ensemble or not)
        - (optional) account - the <account> 
        - (optional) queue - the <queue> (if queue==debug and walltime>1800, it won't be used)
   '''

   # Override the account name if it is passed in. Otherwise, check if a mapping 
   # exists for this taskname in g_task_account_mappings. Otherwise, use default
   if len(account) == 0:
      if taskname in g_task_account_mappings:
         account = g_task_account_mappings[taskname]
      else:
         account = DEFAULT_ACCOUNT_NAME

   if queue != '' and queue != None and  queue == 'debug' and int(walltime) > 1800:
      print 'Debug queue cannot exceed 1800 seconds on Jet. Ignoring queue parameter'
      queue = cfg.default_queue 

   # Override the queue name if it is passed in. Otherwise, check if a mapping 
   # exists for this taskname in g_task_queue_mappings. Otherwise, use default
   if queue == '' or queue == None :
      if taskname in g_task_queue_mappings:
         queue = g_task_queue_mappings[taskname]
      else:
         queue = cfg.default_queue

   # Override the partition entry if a mapping 
   # exists for this taskname in g_task_partition_mappings. Otherwise, use the default
   # if it is passed in. Otherwise, do nothing (i.e. no need for the partition)
   if taskname in g_task_partition_mappings:
      native_node = ET.SubElement(tasknode, 'native')
      native_node.text = g_task_partition_mappings[taskname]
   elif len(cfg.batch_system_partition) > 0 :
      native_node = ET.SubElement(tasknode, 'native')
      native_node.text = '&PARTITION;'

   queue_node = ET.SubElement(tasknode, 'queue')
   queue_node.text = queue
   # TODO : This is hackish, need something more elegant 
   #     (e.g. have a ResourceRequest type or something)
   if str(num_cores).find("ppn") > 0:
      nodes_node  = ET.SubElement(tasknode, 'nodes')
      nodes_node.text = num_cores
   else:
      cores_node = ET.SubElement(tasknode, 'cores')
      cores_node.text = str(num_cores)
   
   walltime_node = ET.SubElement(tasknode, 'walltime')
   # attempt to convert walltime to ddhhmmss for readibility
   try:
      walltime = int(walltime)
   except Exception:
      print 'walltime is not an integer!'
      sys.exit(2)
   if walltime >= (8 * 3600):
      #TODO
      #log.warn('estimated walltime %i is greater than 8 hours, forcing to 8 hours' %(walltime) )
      print 'Estimated walltime %s is greater than 8 hours, forcing to 8 hours' %(seconds2dhms(walltime) )
      walltime = (8 * 3600) - 1
   walltime = seconds2dhms(walltime)[3:] # convert from DD:HH:MM:SS to HH:MM:SS
   #walltime = seconds2dhms(walltime)
   walltime_node.text = walltime
   
   if len(account) > 0 :
      account_node = ET.SubElement(tasknode, 'account')
      account_node.text = account 
  
   jobname_node = ET.SubElement(tasknode, 'jobname')
   # add date suffix to job name (<date><hour> if cycling every hour or more, <hour><min> owise)
   jn_cyclestr_node = ET.SubElement(jobname_node, 'cyclestr')
   if cfg.frequency >= 3600:
      jn_cyclestr_node.text = '%s_@d@H' %jobname
   else:
      jn_cyclestr_node.text = '%s_@H@M' %jobname

   return tasknode
   
   
def add_cycle_defs(root):

   # for the spinup
   first_cycledef = ET.SubElement(root, 'cycledef')
   first_cycledef.set('group', SPINUP_CYCLEDEF_NAME)
   first_cycledef.text = '%s %s %s %s %s *' %(cfg.start_date.minute, cfg.start_date.hour, cfg.start_date.day, cfg.start_date.month, cfg.start_date.year)
   
   # for the last cycle
   last_cycledef = ET.SubElement(root, 'cycledef')
   last_cycledef.set('group', LAST_CYCLE_CYCLEDEF_NAME)
   last_cycledef.text = '%s %s %s %s %s *' %(cfg.end_date.minute, cfg.end_date.hour, cfg.end_date.day, cfg.end_date.month, cfg.end_date.year)
   
   # WPS cycledef - Runs every time a new GFS forecast is available
   wps_cycledef = ET.SubElement(root, 'cycledef')
   wps_cycledef.set('group', WPS_CYCLEDEF_NAME)
   wps_frequency = seconds2dhms(cfg.wps_gfs_frequency)
   wps_cycledef.text = '%s %s %s' %(cfg.start_date_str, cfg.end_date_str, wps_frequency)

   # Real cycledef - For data assimilation, we update the boundaries every iteration,
   #  so Real needs to run every iteration & hence doesn't need a separate cycledef
   #real_cycledef = ET.SubElement(root, 'cycledef')
   #real_cycledef.set('group', REAL_CYCLEDEF_NAME)
   #real_frequency = seconds2dhms(g_real_frequency)
   #real_cycledef.text =  '%s %s %s' %(cfg.start_date_str, cfg.end_date_str, real_frequency)

   # WRF/GSI Cycledef - These run according to g_frequncy
   wrfgsi_cycledef = ET.SubElement(root, 'cycledef')
   wrfgsi_cycledef.set('group', WRFGSI_CYCLEDEF_NAME)
   wrfgsi_frequency = seconds2dhms(cfg.frequency)
   # this cycle starts "frequency" seconds after the start time of the experiment
   warm_start_time = g_start_time + cfg.frequency
   tm = time.localtime(warm_start_time)
   warm_start_date = '%s%s%s%s%s' %(tm.tm_year, zeropad(tm.tm_mon,2), zeropad(tm.tm_mday,2),
                                    zeropad(tm.tm_hour,2), zeropad(tm.tm_min,2) )
   wrfgsi_cycledef.text =  '%s %s %s' %(warm_start_date, cfg.end_date_str, wrfgsi_frequency)

   fcst_cycledef = ET.SubElement(root, 'cycledef')
   fcst_cycledef.set('group', FORECAST_CYCLEDEF_NAME)
   first_fcst = cfg.start_date.get_epochtime() + cfg.first_forecast
   tm = time.localtime(first_fcst) 
   first_fcst_str =  '%s%s%s%s%s' %(tm.tm_year, zeropad(tm.tm_mon,2), zeropad(tm.tm_mday,2),
                                    zeropad(tm.tm_hour,2), zeropad(tm.tm_min,2) )
   fcst_cycledef.text = '%s %s %s' %(first_fcst_str, cfg.end_date_str, seconds2dhms(cfg.forecast_frequency) )

def add_member_var_node(parent_node):
   '''
   Adds a <var> entry for a metatask whose value is a string containing the member ID's
   '''
   var_node = ET.SubElement(parent_node, "var")
   var_node.set("name", "member")
   var_node.text = ' '.join([ str(x).zfill(cfg.num_digits) for x in range(1,cfg.num_members+1) ])


def get_task_name(basename, ensemble=False):
   '''
   RETURNS the 'name' attribute of a task element. 
   If <ensemble> is True, the following behavior applies:
      If DA_TYPE is gsi, it returns the basename. 
      If DA_TYPE is enkf: it returns basename + '_m#member# (e.g. taskname_#member#)
   
   '''
   if ensemble and cfg.da_type == 'enkf':
      #return basename + '_m' + g_member_str
      return basename + '_m#member#'
   else:
      return basename
   if not cfg.da_type in ('enkf', 'gsi', 'coldstart'):
      raise Exception('Invalid/Unspecified $DA_TYPE in configuration')
   
def get_job_name(jobname, ensemble=False):
   '''
   RETURN job name string, which is simply <jobname> for non-ensemble runs
          and <jobname>_m#member# for ensemble runs.
          If the optional <ensemble> parameter is False, return <jobname>
   '''
   if ensemble and cfg.da_type == 'enkf':
      return jobname + '_m#member#'
   else: 
      return jobname
   if not cfg.da_type in ('enkf', 'gsi', 'coldstart'): 
      raise Exception('Invalid/Unspecified $DA_TYPE in configuration')

def add_taskdep_node(dependency_node, cfg, task_name, use_metatask, cycle_offset=None):
   '''
   Adds a dependency child node to a given <dependency_node>. 
   If <use_metatask> is True and the <cfg> object reflects an EnKF run,
   create a metatask dependency. Otherwise create a task dependency. In either
   case, it will use <task_name> as the name.
   If <cycle_offset> is given, set it.
   '''
   if use_metatask and cfg.da_type == 'enkf':
      task_dep = ET.SubElement(dependency_node, 'metataskdep')
      task_dep.set('metatask', task_name)
   else : # i.e. gsi or metatask not applicable
      task_dep = ET.SubElement(dependency_node, 'taskdep')
      task_dep.set('task', task_name)
   # sanity check 
   if not cfg.da_type in ('gsi', 'enkf', 'coldstart'):
      log.error('Unknown DA_TYPE')
      sys.exit(1)
   if cycle_offset != None:
      task_dep.set('cycle_offset', cycle_offset)


def add_ensemble_wps_task(root):
   '''
   This method adds the WPS ensemble task
   '''
   metatask = ET.SubElement(root, 'metatask')
   metatask.set('name', WPS_ENSEMBLE_METATASK_NAME)
   add_member_var_node(metatask)
   wps_task = ET.SubElement(metatask, 'task')
   wps_task.set('name', get_task_name(WPS_TASK_NAME, True) )
   wps_task.set('cycledefs', WPS_CYCLEDEF_NAME)
   wps_task.set('maxtries', MAXTRIES)
   
   add_task_log(wps_task, WPS_TASK_NAME, LOG_FILE_SUFFIX, True)
   
   command = ET.SubElement(wps_task, 'command')
   
   cyclestr = ET.SubElement(command, 'cyclestr')
   # args to WPS: <member#> <job name> <working directory> <start_date> <duration>
   # wps working directory will have date appended to it
   cyclestr.text = '%s %s %s %s %s %s %s %s %s' %(g_wps_job_script_name, cfg.gfs_ensemble_id, g_member_str,
        '@s', '&GFS_ENSEMBLE_FORECAST_DURATION;', get_wps_workdir(), '&CFG_FILE_PATH;', cfg.reuse_static_data, cfg.debug_mode)
   wps_task = add_job_params_to_task(wps_task, get_wps_num_cores(), WPS_TASK_NAME, get_job_name('wps', True), get_wps_walltime())
   return root
   

def add_wps_task(root):
   '''
   This method adds the WPS task. This one does not have dependencies.
   This task applies to both GSI and EnKF experiments, but for the latter
   it is only used for the forecasts, not necessarily for all cycles.
   '''
   
   wps_task = ET.SubElement(root, 'task')
   wps_task.set('name', get_task_name(WPS_TASK_NAME, False) )
   
   # If this is an EnKF run, the WPS with GFS background is only used for forecasts,
   # for GSI experiments, its used for cycling as well
   if cfg.da_type in ( 'gsi' , 'coldstart'):
      wps_task.set('cycledefs', WPS_CYCLEDEF_NAME)
   elif cfg.da_type == 'enkf':
      wps_task.set('cycledefs', FORECAST_CYCLEDEF_NAME)
   else:
      raise Exception('Unknown DA_TYPE')
   
   wps_task.set('maxtries', MAXTRIES)
   
   add_task_log(wps_task, WPS_TASK_NAME, LOG_FILE_SUFFIX, False)
   
   command = ET.SubElement(wps_task, 'command')
   
   cyclestr = ET.SubElement(command, 'cyclestr')
   # args to WPS: <member#> <job name> <working directory> <start_date> <duration>
   # wps working directory will have date appended to it
   cyclestr.text = '%s %s %s %s %s %s %s %s %s' %(g_wps_job_script_name, cfg.gfs_forecast_id, 'NA',
        '@s', '&WPS_GFS_FCST_DURATION;', get_wps_workdir(), '&CFG_FILE_PATH;', cfg.reuse_static_data, cfg.debug_mode)
   wps_task = add_job_params_to_task(wps_task, get_wps_num_cores(), WPS_TASK_NAME, get_job_name('wps', False), get_wps_walltime())
   return root


def add_real_task(root):
   '''
   Add the Real task to the workflow. This is for the Real task that runs for the forecast 
   and for GSI experiments.
   A seperate task is added for the ensemble in <add_ensemble_real_task>.
   '''
   
   # Add task node. If it's EnKF, it's a child of a metatask. Otherwise, it's a child of root 
   # Note: Real needs to run at each cycle, not at the WPS cycles, since the fresh wrfinput is
   # needed for the boundary update step
   real_task = ET.SubElement(root, 'task')
   real_task.set('name', get_task_name(REAL_TASK_NAME, False) )
   if cfg.da_type in ( 'gsi', 'coldstart' ):
      real_task.set('cycledefs', WRFGSI_CYCLEDEF_NAME+","+SPINUP_CYCLEDEF_NAME)
   elif cfg.da_type == 'enkf':
      real_task.set('cycledefs', FORECAST_CYCLEDEF_NAME+","+SPINUP_CYCLEDEF_NAME)
   else:
      raise Exception('Uknown DA_TYPE')

   real_task.set('maxtries', MAXTRIES)
   
   add_task_log(real_task, REAL_TASK_NAME, LOG_FILE_SUFFIX, False)

   # Real depends on the WPS from the last set of boundary conditions having been run,
   # but Rocoto does dependency checks based on the time corresponding to the current
   # cycle, so we need to use an 'or' containing all the timestamps, relative to the
   # current cycle, leading down to the last WPS cycle.
   dep = ET.SubElement(real_task, 'dependency')
   taskdep_or = ET.SubElement(dep, 'or')
   if cfg.da_type in ('gsi', 'coldstart'):
      for i in range( 0 , cfg.wps_gfs_frequency , cfg.frequency) :
         add_taskdep_node(taskdep_or, cfg, WPS_TASK_NAME, False, '-' + seconds2dhms(i) )
   elif cfg.da_type == 'enkf':
      # For EnkF, this task only runs at forecast intervals
      add_taskdep_node(taskdep_or, cfg, WPS_TASK_NAME, False)
   else:
      raise Exception("Uknown DA_Type")
      
   real_task = add_job_params_to_task(real_task, get_real_num_cores(), REAL_TASK_NAME, get_job_name('real', False), get_real_walltime())
   
   command = ET.SubElement(real_task, 'command')
   cyclestr = ET.SubElement(command, 'cyclestr')
   # args to Real: <member#> <start_date> <duration>
   # wps working directory will have date appended to it
   cyclestr.text = '%s %s %s %s %s %s %s %s %s' %(g_real_job_script_name, cfg.gfs_forecast_id, 'NA', '@s', '&FCST_DURATION;', get_atmos_dir(), '&CFG_FILE_PATH;', cfg.reuse_static_data, cfg.debug_mode )

   return root

def add_ensemble_real_task(root):
   '''
   Add the Real ensemble task to the workflow. 
   '''
   metatask = ET.SubElement(root, 'metatask')
   metatask.set('name', REAL_ENSEMBLE_METATASK_NAME)
   add_member_var_node(metatask)
   real_task = ET.SubElement(metatask, 'task')
   real_task.set('name', get_task_name(REAL_TASK_NAME, True) )
   real_task.set('cycledefs', '%s,%s' %(SPINUP_CYCLEDEF_NAME,WRFGSI_CYCLEDEF_NAME) )
   real_task.set('maxtries', MAXTRIES)
   
   add_task_log(real_task, REAL_TASK_NAME, LOG_FILE_SUFFIX, True)

   # Real depends on the WPS from the last set of boundary conditions having been run,
   # but Rocoto does dependency checks based on the time corresponding to the current
   # cycle, so we need to use an 'or' containing all the timestamps, relative to the
   # current cycle, leading down to the last WPS cycle.
   dep = ET.SubElement(real_task, 'dependency')
   taskdep_or = ET.SubElement(dep, 'or')
   for i in range( 0 , cfg.wps_gfs_frequency , cfg.frequency) :
      add_taskdep_node(taskdep_or, cfg, get_job_name(WPS_TASK_NAME, True), False, '-' + seconds2dhms(i) )
      
   real_task = add_job_params_to_task(real_task, get_real_num_cores(), REAL_TASK_NAME, get_job_name('real', False), get_real_walltime())
   
   command = ET.SubElement(real_task, 'command')
   cyclestr = ET.SubElement(command, 'cyclestr')
   # args to Real: <member#> <start_date> <duration>
   # wps working directory will have date appended to it
   cyclestr.text = '%s %s %s %s %s %s %s %s %s' %(g_real_job_script_name, cfg.gfs_ensemble_id, g_member_str, '@s', '&GFS_ENSEMBLE_FORECAST_DURATION;', get_atmos_dir(), '&CFG_FILE_PATH;', cfg.reuse_static_data, cfg.debug_mode )

   return root
   
def add_additive_inflation_task(root):
   '''
   Add additive inflation task to the workflow definition
   '''
   infl_task = ET.SubElement(root, 'task')
   infl_task.set('name', ADDITIVE_INFLATION_TASK_NAME)
   infl_task.set('cycledefs', '%s' %(WRFGSI_CYCLEDEF_NAME) )
   infl_task.set('maxtries', MAXTRIES)
   
   # Additive inflation uses the outputs generated by the previous cycle's EnKF task 
   # and the wrfinput files. If using previously-generated Real data, we only depend
   # on the previous EnKF.  
   dep = ET.SubElement(infl_task, 'dependency')
   dep_and = ET.SubElement(dep, 'and')
   add_taskdep_node(dep_and, cfg, ENKF_TASK_NAME, False) #,  '-' + seconds2dhms(cfg.frequency) )
   if not cfg.reuse_static_data:
      add_taskdep_node(dep_and, cfg, REAL_TASK_NAME, False)
   
   add_task_log(infl_task, ADDITIVE_INFLATION_TASK_NAME, LOG_FILE_SUFFIX, False)
   infl_task = add_job_params_to_task(infl_task, get_additive_inflation_num_cores(), ADDITIVE_INFLATION_TASK_NAME, 'inflation_', get_additive_inflation_walltime())
   command = ET.SubElement(infl_task, 'command')
   cyclestr = ET.SubElement(command, 'cyclestr')
   # args to Additive inflation: <start_date> <top-level model directory> 
   #                             <cfg file path> <debug mode?>
   cyclestr.text = '%s %s %s %s %s %s' %(g_additive_inflation_job_script_name, '@s', get_atmos_dir(), '&CFG_FILE_PATH;', cfg.reuse_static_data, cfg.debug_mode )
   

def add_cleanup_task(root):
   '''
   Add task that cleans up data that cannot be deleted during other scripts due to parallel dependencies
   '''
   cleanup_task = ET.SubElement(root, 'task')
   cleanup_task.set('name', CLEANUP_TASK_NAME)
   cleanup_task.set('cycledefs', '%s' %(WRFGSI_CYCLEDEF_NAME) )
   cleanup_task.set('maxtries', MAXTRIES)
   
   dep = ET.SubElement(cleanup_task, 'dependency')
   dep_and = ET.SubElement(dep, 'and')
   if cfg.perform_enkf_additive_inflation:
      add_taskdep_node(dep_and, cfg, ADDITIVE_INFLATION_TASK_NAME, False) 
   else:
      add_taskdep_node(dep_and, cfg, ENKF_TASK_NAME, False)
      add_taskdep_node(dep_and, cfg, REAL_TASK_NAME, False)
      add_taskdep_node(dep_and, cfg, HWRF_GES_TASK_NAME, True)
   if cfg.perform_ensemble_analysis_upp:
      add_taskdep_node(dep_and, cfg, ENSEMBLE_ANALYSIS_UPP_TASK_NAME, False) 
   
   add_task_log(cleanup_task, CLEANUP_TASK_NAME, LOG_FILE_SUFFIX, False)
   cleanup_task = add_job_params_to_task(cleanup_task, 1, CLEANUP_TASK_NAME, 'cleanup_', 600)
   command = ET.SubElement(cleanup_task, 'command')
   cyclestr = ET.SubElement(command, 'cyclestr')
   # args to Additive inflation: <start_date> <cfg file path> <debug mode?>
   cyclestr.text = '%s %s %s %s' %(g_cleanup_job_script, '@s', '&CFG_FILE_PATH;', cfg.debug_mode )


def add_archive_task(root):
   '''
   Add task that archives the expeirment
   '''
   archive_task = ET.SubElement(root, 'task')
   archive_task.set('name', ARCHIVE_TASK_NAME)
   archive_task.set('cycledefs', '%s' %(LAST_CYCLE_CYCLEDEF_NAME) )
   archive_task.set('maxtries', MAXTRIES)
   
   dep = ET.SubElement(archive_task, 'dependency')
   # TODO Add if conditions in case no postproc_expt task
   #if cfg.perform_postproc_fcst:
   #   add_taskdep_node(dep, cfg, POSTPROC_FCST_TASK_NAME, False) #TODO : change this to final_postproc when that's implemented
   #else:
   #   add_taskdep_node(dep, cfg, HWRF_DETERMINISTIC_FCST_TASK_NAME, False) #TODO : there may not be a forecast on the final cycle!
   add_taskdep_node(dep, cfg, EXPERIMENT_POSTPROC_TASK_NAME, False) #TODO : there may not be a forecast on the final cycle!
   
   add_task_log(archive_task, ARCHIVE_TASK_NAME, LOG_FILE_SUFFIX, False)
   archive_task = add_job_params_to_task(archive_task, 1, ARCHIVE_TASK_NAME, ARCHIVE_TASK_NAME, get_archive_task_duration())
   
   command = ET.SubElement(archive_task, 'command')
   command.text = '%s %s %s' %(g_archive_job_script, '&CFG_FILE_PATH;', cfg.debug_mode)


def add_postproc_experiment_task(root):
   '''
   Add task that does post-processing that occurs after experiment is complete
   '''
   expt_postproc_task = ET.SubElement(root, 'task')
   expt_postproc_task.set('name', EXPERIMENT_POSTPROC_TASK_NAME)
   expt_postproc_task.set('cycledefs', '%s' %(LAST_CYCLE_CYCLEDEF_NAME) )
   expt_postproc_task.set('maxtries', MAXTRIES)
   
   dep = ET.SubElement(expt_postproc_task, 'dependency')
   if cfg.perform_postproc_fcst:
      #add_taskdep_node(dep, cfg, POSTPROC_FCST_TASK_NAME, False) #TODO : change this to final_postproc when that's implemented
      taskdep_and = ET.SubElement(dep, 'and')
      #for i in range( cfg.first_forecast ,(cfg.end_date.get_epochtime() - cfg.start_date.get_epochtime() ) + cfg.first_forecast + cfg.forecast_frequency + 1 , cfg.forecast_frequency  ) :
      for i in range( 0 ,((cfg.end_date.get_epochtime() - cfg.start_date.get_epochtime() ) - cfg.first_forecast) + 1 , cfg.forecast_frequency  ) :
         # TODO : Assuming all postproc tasks will be run
         add_taskdep_node(taskdep_and, cfg, POSTPROC_FCST_TASK_NAME, False, '-' + seconds2dhms(i) )
         add_taskdep_node(taskdep_and, cfg, DIAPOST_FCST_TASK_NAME, False, "-" + seconds2dhms(i) )
         add_taskdep_node(taskdep_and, cfg, UPP_FCST_TASK_NAME, False, "-" + seconds2dhms(i) )
         add_taskdep_node(taskdep_and, cfg, GFDL_TRACKER_TASK_NAME, False, "-" + seconds2dhms(i) )
   else:
      add_taskdep_node(dep, cfg, HWRF_DETERMINISTIC_FCST_TASK_NAME, False) #TODO : there may not be a forecast on the final cycle!
   
   add_task_log(expt_postproc_task, EXPERIMENT_POSTPROC_TASK_NAME, LOG_FILE_SUFFIX, False)
   expt_postproc_task = add_job_params_to_task(expt_postproc_task, 1, EXPERIMENT_POSTPROC_TASK_NAME, EXPERIMENT_POSTPROC_TASK_NAME, get_expt_postproc_task_duration())
   
   command = ET.SubElement(expt_postproc_task, 'command')
   cyclestr = ET.SubElement(command, 'cyclestr')
   cyclestr.text = '%s %s %s %s' %(g_expt_postproc_job_script_name, '@s', '&CFG_FILE_PATH;', cfg.debug_mode)


def add_dummy_task(root):
   '''
   Add a dummy task. This is used when starting from a warm start, since the GSI task needs to have
   a dependency in order to start. If starting warm, the dependency is already met when starting, but
   there is no way of conveying this in the workflow definition.
   '''
   dummy_task = ET.SubElement(root, 'task')
   dummy_task.set('name', DUMMY_GSI_DEP_NAME)
   dummy_task.set('cycledefs', SPINUP_CYCLEDEF_NAME)
   add_task_log(dummy_task, DUMMY_GSI_DEP_NAME, LOG_FILE_SUFFIX, False)
   dummy_task = add_job_params_to_task(dummy_task, 1, DUMMY_TASK_NAME, get_job_name(DUMMY_GSI_DEP_NAME, False), 30)
   command = ET.SubElement(dummy_task, 'command')
   command.text = g_dummy_gsi_dep_script_name
   return root


def add_wrf_spinup_task(root):
   '''
   Add the cold/spinup HWRF task, which only depends on Real
   '''
   
   # Add task node. If it's EnKF, it's a child of a metatask. Otherwise, it's a child of root 
   if cfg.da_type == 'enkf':
      metatask = ET.SubElement(root, 'metatask')
      metatask.set('name', HWRF_SPINUP_TASK_NAME)
      add_member_var_node(metatask)
      hwrf_cold_task = ET.SubElement(metatask, 'task')
      expt_id = cfg.gfs_ensemble_id
   elif cfg.da_type == 'gsi':
      hwrf_cold_task = ET.SubElement(root, 'task')
      expt_id = cfg.gfs_forecast_id
   else:
      raise Exception("Uknown/Invalid DA_TYPE for wrf_spinup task")
   
   hwrf_cold_task.set('name', get_task_name(HWRF_SPINUP_TASK_NAME, True) )
   hwrf_cold_task.set('cycledefs', SPINUP_CYCLEDEF_NAME)
   hwrf_cold_task.set('maxtries', MAXTRIES)
   
   add_task_log(hwrf_cold_task, HWRF_SPINUP_TASK_NAME, LOG_FILE_SUFFIX, True)
   
   # add dependencies
   if not cfg.reuse_static_data:
      taskdep = ET.SubElement(hwrf_cold_task, 'dependency')
      if cfg.da_type == 'enkf':
         add_taskdep_node(taskdep, cfg, REAL_ENSEMBLE_METATASK_NAME, True)
      elif cfg.da_type == 'gsi':
         add_taskdep_node(taskdep, cfg, REAL_TASK_NAME, False)
         
   hwrf_cold_task = add_job_params_to_task(hwrf_cold_task, get_wrf_num_cores(), HWRF_SPINUP_TASK_NAME, get_job_name(HWRF_SPINUP_TASK_NAME, True), get_wrf_walltime())
   command = ET.SubElement(hwrf_cold_task, 'command')
   cyclestr = ET.SubElement(command, 'cyclestr')
   cyclestr.text = '%s %s %s %s %s %s %s %s %s %s %s %s' %(g_wrf_job_script_name, expt_id, g_member_str, get_atmos_dir(), '@s', '&CYCLE_FREQUENCY;', 
      '&FCST_DURATION;', '&CFG_FILE_PATH;', 'COLD', 'TRUE', cfg.reuse_static_data, cfg.debug_mode )
# TODO: need the cold forecast : either add cold_notrg (since this one is actually rg) or change the scheme so that the standard wrf jobs take the actual start time from the cycledef

   return root

def add_wrf_ges_task(root):
   '''
   Add the HWRF 'restartgen' task, which depends on Real (which depends on gsi)
   Note that there is a separate "spinup" task for the first first-guess
   '''
   
   # Add task node. If it's EnKF, it's a child of a metatask. Otherwise, it's a child of root 
   if cfg.da_type == 'enkf':
      metatask = ET.SubElement(root, 'metatask')
      metatask.set('name', HWRF_GES_TASK_NAME)
      add_member_var_node(metatask)
      hwrf_task = ET.SubElement(metatask, 'task')
      expt_id = cfg.gfs_ensemble_id
   elif cfg.da_type == 'gsi':
      hwrf_task = ET.SubElement(root, 'task')
      expt_id = cfg.gfs_forecast_id

   hwrf_task.set('name', get_task_name(HWRF_GES_TASK_NAME, True) )
   hwrf_task.set('cycledefs', WRFGSI_CYCLEDEF_NAME)
   hwrf_task.set('maxtries', MAXTRIES)

   add_task_log(hwrf_task, HWRF_GES_TASK_NAME, LOG_FILE_SUFFIX, True)

   #dep = ET.SubElement(hwrf_task, 'dependency')
   #TODO : Should also depend on Real for current cycle
   #taskdep_or = ET.SubElement(dep, 'or')
   #taskdep1 = ET.SubElement(taskdep_or, 'taskdep')
   #taskdep1.set('task', HWRF_SPINUP_TASK_NAME)
   #taskdep1.set('cycle_offset', '-' + str(cfg.frequency))
   #taskdep2 = ET.SubElement(taskdep_or, 'taskdep')
   dep = ET.SubElement(hwrf_task, 'dependency')
   #add_taskdep_node(dep, cfg, GSI_TASK_NAME, True)
   if cfg.da_type == 'enkf':
      if cfg.perform_enkf_additive_inflation:
         add_taskdep_node(dep, cfg, ADDITIVE_INFLATION_TASK_NAME, False)
      else:   
         taskdep_and = ET.SubElement(dep, 'and')
         add_taskdep_node(taskdep_and, cfg, ENKF_TASK_NAME, False)
         if not cfg.reuse_static_data:
            add_taskdep_node(taskdep_and, cfg, REAL_ENSEMBLE_METATASK_NAME, True)
   elif cfg.da_type == 'gsi':
      taskdep_and = ET.SubElement(dep, 'and')
      add_taskdep_node(taskdep_and, cfg, GSI_TASK_NAME, False)
      if not cfg.reuse_static_data:
         add_taskdep_node(taskdep_and, cfg, REAL_TASK_NAME, False)
   else:
      sys.stderr.write('Invalid DA_TYPE')
      sys.exit(1)

   
   command = ET.SubElement(hwrf_task, 'command')
   cyclestr = ET.SubElement(command, 'cyclestr')
   cyclestr.text = '%s %s %s %s %s %s %s %s %s %s %s %s' %(g_wrf_job_script_name, expt_id, g_member_str, get_atmos_dir(), '@s', '&CYCLE_FREQUENCY;', '&FCST_DURATION;', '&CFG_FILE_PATH;', 'WARM', 'TRUE', cfg.reuse_static_data, cfg.debug_mode )

   hwrf_task = add_job_params_to_task(hwrf_task, get_wrf_num_cores(), HWRF_GES_TASK_NAME, get_job_name(HWRF_GES_TASK_NAME, True), get_wrf_walltime())
   return root
   
   
def add_wrf_det_fcst_task(root): 
   '''
   Add the HWRF deterministic forecast task
   '''
   hwrf_task = ET.SubElement(root, 'task')
   hwrf_task.set('name', get_task_name(HWRF_DETERMINISTIC_FCST_TASK_NAME, False) )
   hwrf_task.set('cycledefs', FORECAST_CYCLEDEF_NAME)
   hwrf_task.set('maxtries', MAXTRIES)
   add_task_log(hwrf_task, HWRF_DETERMINISTIC_FCST_TASK_NAME, LOG_FILE_SUFFIX, False)
   
   command = ET.SubElement(hwrf_task, 'command')
   cyclestr = ET.SubElement(command, 'cyclestr')
   if cfg.da_type == 'coldstart':
      runtype = 'COLD'
   else:
      runtype = 'WARM'
   cyclestr.text = '%s %s %s %s %s %s %s %s %s %s %s %s' %(g_wrf_job_script_name, cfg.gfs_forecast_id, 'na',  get_atmos_dir() , 
      '@s', '&CYCLE_FREQUENCY;', '&FCST_DURATION;', '&CFG_FILE_PATH;', runtype, 'FALSE', cfg.reuse_static_data, cfg.debug_mode )
   
   # Forecast depends on the previous cycle restart-gen run (either spinup_wrf or warm_wrf)
   # But my convention is that the full forecast starting at 01:30 corresponds to the 01:00 cycle
   # so there is no cycle_offset
   # For coldstart "cycling", the only dependency is Real
   if cfg.da_type == 'coldstart':
      if not cfg.reuse_static_data:
         dep = ET.SubElement(hwrf_task, 'dependency')
         add_taskdep_node(dep, cfg, REAL_TASK_NAME, True)
   else:
      dep = ET.SubElement(hwrf_task, 'dependency')
      taskdep_and = ET.SubElement(dep, 'and')
      if not cfg.reuse_static_data:
         add_taskdep_node(taskdep_and, cfg, REAL_TASK_NAME, False)
      # technically, the det. fcst does not depend on the ges, but since they work in 
      # the same directory, creating the dependency will prevent race conditions  
      taskdep_or = ET.SubElement(taskdep_and, 'or')
      add_taskdep_node(taskdep_or, cfg, HWRF_GES_TASK_NAME, True)
      add_taskdep_node(taskdep_or, cfg, HWRF_SPINUP_TASK_NAME, True)
      # Deterministic forecast requires the analysis file for the current cycle
      if cfg.da_type == 'gsi':
         add_taskdep_node(taskdep_and, cfg, GSI_TASK_NAME, True)
      if cfg.da_type == 'enkf':
         add_taskdep_node(taskdep_and, cfg, ENKF_TASK_NAME, False)
   
   hwrf_task = add_job_params_to_task(hwrf_task, get_wrf_num_cores(), HWRF_DETERMINISTIC_FCST_TASK_NAME, get_job_name(HWRF_DETERMINISTIC_FCST_TASK_NAME, False), get_wrf_walltime(fcst_time=cfg.forecast_duration))
   return root


def add_gsi_task(root):
   '''
   Add the GSI task. 
   '''
   if cfg.da_type == 'enkf':
      gsi_metatask = ET.SubElement(root, 'metatask')
      gsi_metatask.set('name', GSI_TASK_NAME)
      add_member_var_node(gsi_metatask)
      gsi_task = ET.SubElement(gsi_metatask, 'task')
      expt_id = cfg.gfs_ensemble_id 
      work_dir_cyclestr = '&RUN_DIR;/' + cfg.gsi_ges_subdir + '.@Y_@m_@d_@H_@M'
   elif cfg.da_type == 'gsi':
      gsi_task = ET.SubElement(root, 'task')
      expt_id = cfg.gfs_forecast_id
      work_dir_cyclestr = '&RUN_DIR;/' + cfg.gsi_analysis_subdir + '.@Y_@m_@d_@H_@M'

   gsi_task.set('name', get_task_name(GSI_TASK_NAME, True) )
   gsi_task.set('cycledefs', WRFGSI_CYCLEDEF_NAME)
   gsi_task.set('maxtries', MAXTRIES)

   add_task_log(gsi_task, GSI_TASK_NAME, LOG_FILE_SUFFIX, True)

   # Add dependency node
   if cfg.da_type == 'enkf':
      dep = ET.SubElement(gsi_task, 'dependency')
      add_taskdep_node(dep, cfg, GSI_ENSMEAN_TASK_NAME, False)
   elif cfg.da_type == 'gsi':
      # GSI depends on the previous HWRF cycle (either spinup_wrf or warm_wrf)
      dep = ET.SubElement(gsi_task, 'dependency')
      taskdep_or = ET.SubElement(dep, 'or')
      # if doing a warm init, just run a dummy task to satisfy the dependency
      if cfg.warm_init:
         add_taskdep_node(taskdep_or, cfg, DUMMY_GSI_DEP_NAME, False, '-' + str(cfg.frequency))
      else:
         add_taskdep_node(taskdep_or, cfg, HWRF_SPINUP_TASK_NAME, True, '-' + str(cfg.frequency))
      add_taskdep_node(taskdep_or, cfg, HWRF_GES_TASK_NAME, True, '-' + str(cfg.frequency))
   
   # Add command node
   command = ET.SubElement(gsi_task, 'command')
   #if cfg.da_file_type == 'restart': daFilePrefix = cfg.restart_file_prefix 
   #elif cfg.da_file_type == 'wrfinput': daFilePrefix = cfg.wrfinout_file_prefix 
   #else:
   #   print 'Configuration parameter $DA_FILE_TYPE should be either "restart" or "wrfinput"'
   #   sys.exit(1)
   
   command.text = '%s %s %s %s %s %s %s %s' %(g_gsi_job_script_name, g_member_str,
      cyclestr('@s'), 
      #cyclestr(daFilePrefix + '_d' + cfg.analysis_domain + '_@Y-@m-@d_@H:@M:00'), # background file
      'analysis.nc',
      cyclestr('&RUN_DIR;/ATMOS.@Y_@m_@d_@H_@M', offset='-&CYCLE_FREQUENCY;'), # WRF run directory
      cyclestr(work_dir_cyclestr), 
      '&CFG_FILE_PATH;', 
      cfg.debug_mode) 
      

   gsi_task = add_job_params_to_task(gsi_task, get_gsi_num_cores(), GSI_TASK_NAME, get_job_name('gsi', True), get_gsi_walltime())
  
def add_gsi_ensmean_task(root):
   '''
   Add GSI ensemble mean task 
   '''
   gsi_task = ET.SubElement(root, 'task')
   gsi_task.set('name', get_task_name(GSI_ENSMEAN_TASK_NAME, False) )
   gsi_task.set('cycledefs', WRFGSI_CYCLEDEF_NAME)
   gsi_task.set('maxtries', MAXTRIES)

   add_task_log(gsi_task, GSI_ENSMEAN_TASK_NAME, LOG_FILE_SUFFIX, False)
   
   # GSI depends on the previous HWRF cycle (either spinup_wrf or warm_wrf)
   # For warm_init runs, we use a "dummy" task
   # The gsi_ensmean task only applies to EnKF experiments, so no need for separate
   # condition for GSI experiments.
   dep = ET.SubElement(gsi_task, 'dependency')
   dep_or = ET.SubElement(dep, 'or')
   if cfg.warm_init:
      add_taskdep_node(dep_or, cfg, DUMMY_GSI_DEP_NAME, False, '-' + str(cfg.frequency))
   else:
      add_taskdep_node(dep_or, cfg, HWRF_SPINUP_TASK_NAME, True, '-' + str(cfg.frequency))
   add_taskdep_node(dep_or, cfg, HWRF_GES_TASK_NAME, True, '-' + str(cfg.frequency))

   #if cfg.da_file_type == 'restart': daFilePrefix = cfg.restart_file_prefix
   #elif cfg.da_file_type == 'wrfinput': daFilePrefix = cfg.wrfinout_file_prefix
   #else:
   #   raise Exception('Configuration parameter $DA_FILE_TYPE should be either "restart" or "wrfinput"')

   # create command
   command = ET.SubElement(gsi_task, 'command')
   command.text = '%s %s %s %s %s %s %s %s' %(g_gsi_job_script_name, 'ensmean',
      cyclestr('@s'), 
      #cyclestr(daFilePrefix + '_d' + cfg.analysis_domain + '_@Y-@m-@d_@H:@M:00'),
      'analysis.nc',
      cyclestr('&RUN_DIR;/ATMOS.@Y_@m_@d_@H_@M', offset='-&CYCLE_FREQUENCY;'),
      cyclestr('&RUN_DIR;/' + cfg.gsi_ges_subdir + '.@Y_@m_@d_@H_@M'), 
      '&CFG_FILE_PATH;',
      cfg.debug_mode) 
  
   gsi_task = add_job_params_to_task(gsi_task, get_gsi_num_cores(), GSI_ENSMEAN_TASK_NAME, get_job_name(GSI_ENSMEAN_TASK_NAME, False), get_gsi_walltime())


def add_enkf_task(root):
   '''
   Add the EnKF task to the workflow
   '''
   enkf_task = ET.SubElement(root, 'task')
   enkf_task.set('name', get_task_name(ENKF_TASK_NAME, False) )
   enkf_task.set('cycledefs', WRFGSI_CYCLEDEF_NAME)
   enkf_task.set('maxtries', MAXTRIES)
   add_task_log(enkf_task, ENKF_TASK_NAME, LOG_FILE_SUFFIX, False)
   
   dep = ET.SubElement(enkf_task, 'dependency')
   add_taskdep_node(dep, cfg, GSI_TASK_NAME, True)

   restart_file_path = os.path.join( cfg.run_top_dir , 'ATMOS.@Y_@m_@d_@H_@M', cfg.gfs_ensemble_id )
   #if cfg.da_file_type == 'restart': daFilePrefix = cfg.restart_file_prefix
   #elif cfg.da_file_type == 'wrfinput': daFilePrefix = cfg.wrfinout_file_prefix
   #else: raise Exception('Configuration parameter $DA_FILE_TYPE should be either "restart" or "wrfinput"')
   command = ET.SubElement(enkf_task, 'command')
   command.text = '%s %s %s %s %s %s %s %s' %(g_enkf_job_script_name, 
      cyclestr('@s'), 
      cyclestr('&RUN_DIR;/ENKF.@Y_@m_@d_@H_@M'),
      cyclestr(restart_file_path, offset="-&CYCLE_FREQUENCY;"),
      cyclestr(cfg.auxhist_file_prefix  + '_@Y-@m-@d_@H:@M:00'),
      #cyclestr(daFilePrefix + '_d' + cfg.analysis_domain + '_@Y-@m-@d_@H:@M:00'),
      'firstguess.nc',
      '&CFG_FILE_PATH;',
      cfg.debug_mode )

   enkf_task = add_job_params_to_task(enkf_task, get_enkf_num_cores(), ENKF_TASK_NAME, get_job_name(ENKF_TASK_NAME, False), get_enkf_walltime())


def add_cycle_postproc_task(root):
   '''
   Add the postprocessing task for the cycling/firstguess/restartgen task
   '''
   pp_task = ET.SubElement(root, 'task')
   pp_task.set('name', POSTPROC_CYCLE_TASK_NAME)
   pp_task.set('cycledefs', WRFGSI_CYCLEDEF_NAME)
   pp_task.set('maxtries', MAXTRIES)

   add_task_log(pp_task, POSTPROC_CYCLE_TASK_NAME, LOG_FILE_SUFFIX, False)

   dep = ET.SubElement(pp_task, 'dependency')
   if cfg.da_type == 'gsi':
      add_taskdep_node(dep, cfg, GSI_TASK_NAME, False)
   elif cfg.da_type == 'enkf':
      add_taskdep_node(dep, cfg, ENKF_TASK_NAME, False)
   else:
      raise Exception("Unknown/Invalid DA_TYPE for postproc_cycle task")
   # note: GSI script will create a link to wrf_inout that resembles wrfout file, so we don't need any trickery in postproc script

   # determine output path and file name for cyling data
   # For the background:
   #  for GSI experiments, we use the unmodified GFS background file generated in the previous cycle's ATMOS dir
   #  (from the ges/restartgen run). For EnKF experiments, we use the value computed during the GSI ensemble
   #  mean step.
   # For the analysis: use the wrf_inout for GSI experiments and the analysis.ensmean for EnKF experiments
   if cfg.da_type == 'gsi':
      ges_output_path_cyclestr = cyclestr('&RUN_DIR;/ATMOS.@Y_@m_@d_@H_@M/' +cfg.gfs_forecast_id, offset='-&CYCLE_FREQUENCY;')
      analysis_output_path_cyclestr = cyclestr('&RUN_DIR;/' + cfg.gsi_analysis_subdir + '.@Y_@m_@d_@H_@M')
      ges_file_name = 'wrfout_d' + cfg.analysis_domain + '_@Y-@m-@d_@H:@M:00' # problem: this way, we can't cycle through domains in the script
      analysis_file_name = 'wrf_inout'
   elif cfg.da_type == 'enkf':
      ges_output_path_cyclestr = cyclestr('&RUN_DIR;/' + cfg.gsi_ges_subdir + '.@Y_@m_@d_@H_@M/' + cfg.member_dir_prefix + 'ensmean')
      analysis_output_path_cyclestr = cyclestr('&RUN_DIR;/ENKF.@Y_@m_@d_@H_@M')
      #ges_file_name = 'wrf_inout'
      if cfg.da_file_type != 'restart':
         print 'workflow generator and gsi.sh have hardwired wrfrst prefix for enkf. Gotta fix it'
         sys.exit(2)
      ges_file_name = 'wrfrst_ensmean_d' + cfg.analysis_domain + '_@Y-@m-@d_@H:@M:00' 
      analysis_file_name = 'analysis.ensmean'

   cmd = ET.SubElement(pp_task, 'command')
   cmd.text = '%s %s %s %s %s %s %s %s %s' %(g_postproc_job_script_name, 
                                             cyclestr('&RUN_DIR;/POSTPROC' + get_wrf_dir_suffix_cyclestr() ),   
                                             cyclestr('@s'),
                                             ges_output_path_cyclestr,
                                             cyclestr( ges_file_name ),
                                             analysis_output_path_cyclestr,
                                             analysis_file_name,
                                             "&CFG_FILE_PATH;",
                                             cfg.debug_mode_str)

   pp_task = add_job_params_to_task(pp_task, get_postproc_num_cores(), POSTPROC_CYCLE_TASK_NAME, get_job_name(POSTPROC_CYCLE_TASK_NAME, False), get_postproc_walltime() )


def add_ensemble_analysis_unipost_task(root):
   '''
   Add task that runs UPP on the analysis files from the ensemble after each cycle
   '''
   pp_task = ET.SubElement(root, 'task')
   pp_task.set('name', ENSEMBLE_ANALYSIS_UPP_TASK_NAME)
   pp_task.set('cycledefs', WRFGSI_CYCLEDEF_NAME)
   pp_task.set('maxtries', MAXTRIES)

   add_task_log(pp_task, ENSEMBLE_ANALYSIS_UPP_TASK_NAME, LOG_FILE_SUFFIX, False)

   dep = ET.SubElement(pp_task, 'dependency')
   if cfg.da_type == 'enkf':
      add_taskdep_node(dep, cfg, ENKF_TASK_NAME, False)
   else:
      raise Exception("Cannot add ensemble analysis UPP task for non-EnKF experiment")

   # determine output path and file name for cyling data
   ges_output_path_cyclestr = cyclestr('&RUN_DIR;/' + cfg.gsi_ges_subdir + '.@Y_@m_@d_@H_@M/' + cfg.member_dir_prefix + 'ensmean')
   analysis_output_path_cyclestr = cyclestr('&RUN_DIR;/ENKF.@Y_@m_@d_@H_@M')

   cmd = ET.SubElement(pp_task, 'command')
   cmd.text = '%s %s %s %s %s %s %s ' %(g_enkf_analysis_upp_job_script,
                                        cyclestr('&RUN_DIR;/POSTPROC' + get_wrf_dir_suffix_cyclestr() ),   
                                        cyclestr('@s'),
                                        ges_output_path_cyclestr,
                                        analysis_output_path_cyclestr,
                                        "&CFG_FILE_PATH;",
                                        cfg.debug_mode_str)

   pp_task = add_job_params_to_task(pp_task, get_postproc_num_cores(), ENSEMBLE_ANALYSIS_UPP_TASK_NAME, get_job_name(ENSEMBLE_ANALYSIS_UPP_TASK_NAME, False), get_postproc_walltime() )


def add_ensemble_ges_unipost_task(root):
   '''
   Add task that runs UPP on the analysis files from the ensemble after each cycle
   '''
   pp_task = ET.SubElement(root, 'task')
   pp_task.set('name', ENSEMBLE_PRIOR_UPP_TASK_NAME)
   pp_task.set('cycledefs', WRFGSI_CYCLEDEF_NAME)
   pp_task.set('maxtries', MAXTRIES)

   add_task_log(pp_task, ENSEMBLE_PRIOR_UPP_TASK_NAME, LOG_FILE_SUFFIX, False)

   # add dependency for HWRF task
   if cfg.da_type != 'enkf':
      raise Exception("Cannot add ensemble analysis UPP task for non-EnKF experiment")
   dep = ET.SubElement(pp_task, 'dependency')
   dep_or = ET.SubElement(dep, 'or')
   if cfg.warm_init:
      add_taskdep_node(dep_or, cfg, DUMMY_GSI_DEP_NAME, False, '-' + str(cfg.frequency))
   else:
      add_taskdep_node(dep_or, cfg, HWRF_SPINUP_TASK_NAME, True, '-' + str(cfg.frequency))
   add_taskdep_node(dep_or, cfg, HWRF_GES_TASK_NAME, True, '-' + str(cfg.frequency))
   
   # determine output path and file name for cyling data
   ges_output_path_cyclestr = cyclestr('&RUN_DIR;/' + 'ATMOS' + '.@Y_@m_@d_@H_@M', offset="-"+str(cfg.frequency) ) 
   analysis_output_path_cyclestr = cyclestr('&RUN_DIR;/ENKF.@Y_@m_@d_@H_@M')

   cmd = ET.SubElement(pp_task, 'command')
   cmd.text = '%s %s %s %s %s %s %s ' %(g_enkf_prior_upp_job_script,
                                        cyclestr('&RUN_DIR;/POSTPROC' + get_wrf_dir_suffix_cyclestr() ),   
                                        cyclestr('@s', offset="-"+str(cfg.frequency)),
                                        ges_output_path_cyclestr,
                                        analysis_output_path_cyclestr,
                                        "&CFG_FILE_PATH;",
                                        cfg.debug_mode_str)

   pp_task = add_job_params_to_task(pp_task, get_postproc_num_cores(), ENSEMBLE_PRIOR_UPP_TASK_NAME, get_job_name(ENSEMBLE_PRIOR_UPP_TASK_NAME, False), get_postproc_walltime() )

def add_fcst_diapost_task(root):
   '''
   Adds task that runs diapost after the deterministic forecast completes
   '''
   
   # TODO : check if bigmem queue exists; only use if the domain is above a certain size
   if cfg.supercomputer == 'THEIA':
      g_task_queue_mappings[DIAPOST_FCST_TASK_NAME] = BIGMEM_QUEUE_NAME

   diapost_task = ET.SubElement(root, 'task')
   diapost_task.set('name', DIAPOST_FCST_TASK_NAME)
   diapost_task.set('cycledefs', FORECAST_CYCLEDEF_NAME)
   diapost_task.set('maxtries', MAXTRIES)
   
   add_task_log(diapost_task, DIAPOST_FCST_TASK_NAME, LOG_FILE_SUFFIX, False)

   dep = ET.SubElement(diapost_task, 'dependency')
   add_taskdep_node(dep, cfg, HWRF_DETERMINISTIC_FCST_TASK_NAME, False)

   cmd = ET.SubElement(diapost_task, 'command')
   cmd.text = '%s %s %s %s %s %s' %(g_diapost_fcst_job_script_name, 
                              cyclestr('&RUN_DIR;' + '/' + 'POSTPROC.@Y_@m_@d_@H_@M'),
                              cyclestr('&RUN_DIR;' + '/' + 'ATMOS.@Y_@m_@d_@H_@M' + '/' + cfg.gfs_forecast_id ), 
                              cyclestr('@s'), '&CFG_FILE_PATH;',
                              cfg.debug_mode_str)
   diapost_task = add_job_params_to_task(diapost_task, get_diapost_fcst_num_cores(), 
                               DIAPOST_FCST_TASK_NAME, get_job_name(DIAPOST_FCST_TASK_NAME,False), 
                               get_diapost_fcst_walltime() )

def add_fcst_upp_task(root):
   '''
   Adds task that runs diapost after the deterministic forecast completes
   '''
   upp_task = ET.SubElement(root, 'task')
   upp_task.set('name', UPP_FCST_TASK_NAME)
   upp_task.set('cycledefs', FORECAST_CYCLEDEF_NAME)
   upp_task.set('maxtries', MAXTRIES)
   
   add_task_log(upp_task, UPP_FCST_TASK_NAME, LOG_FILE_SUFFIX, False)

   dep = ET.SubElement(upp_task, 'dependency')
   add_taskdep_node(dep, cfg, HWRF_DETERMINISTIC_FCST_TASK_NAME, False)

   cmd = ET.SubElement(upp_task, 'command')
   cmd.text = '%s %s %s %s %s %s' %(g_upp_fcst_job_script_name, 
                              cyclestr('&RUN_DIR;' + '/' + 'POSTPROC.@Y_@m_@d_@H_@M'),
                              cyclestr('&RUN_DIR;' + '/' + 'ATMOS.@Y_@m_@d_@H_@M' + '/' + cfg.gfs_forecast_id ), 
                              cyclestr('@s'), '&CFG_FILE_PATH;',
                              cfg.debug_mode_str)
   upp_task = add_job_params_to_task(upp_task, get_upp_fcst_num_cores(), 
                           UPP_FCST_TASK_NAME, get_job_name(UPP_FCST_TASK_NAME,False), 
                           get_upp_fcst_walltime() )

def add_fcst_gfdl_tracker_task(root):
   '''
   Adds task that runs the GFDL vortex trackerdiapost after the deterministic forecast completes
   '''
   trk_task = ET.SubElement(root, 'task')
   trk_task.set('name', GFDL_TRACKER_TASK_NAME)
   trk_task.set('cycledefs', FORECAST_CYCLEDEF_NAME)
   trk_task.set('maxtries', MAXTRIES)
   
   add_task_log(trk_task, GFDL_TRACKER_TASK_NAME, LOG_FILE_SUFFIX, False)

   dep = ET.SubElement(trk_task, 'dependency')
   add_taskdep_node(dep, cfg, UPP_FCST_TASK_NAME, False)

   cmd = ET.SubElement(trk_task, 'command')
# TODO : Get UPP output from cfg instead of using hardcoded 'postprd'
   cmd.text = '%s %s %s %s %s' %(g_gfdl_tracker_job_script_name, 
                              cyclestr('&RUN_DIR;' + '/' + 'POSTPROC.@Y_@m_@d_@H_@M' + '/' + 'postprd'),
                              cyclestr('@s'), 
                              '&CFG_FILE_PATH;',
                              cfg.debug_mode_str)
   trk_task = add_job_params_to_task(trk_task, get_gfdl_tracker_num_cores(), 
                           GFDL_TRACKER_TASK_NAME, get_job_name(GFDL_TRACKER_TASK_NAME,False), 
                           get_gfdl_tracker_walltime() )

def add_fcst_postproc_task(root):
   '''
   Add the postprocessing task for the forecast
   '''
   pp_task = ET.SubElement(root, 'task')
   pp_task.set('name', POSTPROC_FCST_TASK_NAME)
   pp_task.set('cycledefs', FORECAST_CYCLEDEF_NAME)
   pp_task.set('maxtries', MAXTRIES)
   
   add_task_log(pp_task, POSTPROC_FCST_TASK_NAME, LOG_FILE_SUFFIX, False)

   dep = ET.SubElement(pp_task, 'dependency')
   taskdep_and = ET.SubElement(dep, 'and')
   add_taskdep_node(taskdep_and, cfg, DIAPOST_FCST_TASK_NAME, False)
   add_taskdep_node(taskdep_and, cfg, UPP_FCST_TASK_NAME, False)

   cmd = ET.SubElement(pp_task, 'command')
   cmd.text = '%s %s %s %s %s %s' %(g_postproc_fcst_job_script_name, 
                              cyclestr('&RUN_DIR;' + '/' + 'POSTPROC.@Y_@m_@d_@H_@M'),
                              cyclestr('&RUN_DIR;' + '/' + 'ATMOS.@Y_@m_@d_@H_@M' + '/' + cfg.gfs_forecast_id ), 
                              cyclestr('@s'), '&CFG_FILE_PATH;',
                              cfg.debug_mode_str)
   pp_task = add_job_params_to_task(pp_task, get_postproc_num_cores(), POSTPROC_FCST_TASK_NAME, 
                        get_job_name(POSTPROC_FCST_TASK_NAME,False), 
                        get_postproc_fcst_walltime() )

def add_gsi_workflow_tasks(root):
   ''' Create the task elements of the workflow '''

   if not cfg.reuse_static_data:
      root = add_wps_task(root)
      root = add_real_task(root)
   
   if cfg.warm_init:
      root = add_dummy_task(root)
   else:
      root = add_wrf_spinup_task(root)
   
   add_gsi_task(root)
   add_wrf_ges_task(root)
   add_wrf_det_fcst_task(root)
   if cfg.perform_postproc_cycle:
      add_cycle_postproc_task(root)
   if cfg.perform_postproc_fcst:
      add_fcst_diapost_task(root)
      add_fcst_upp_task(root)
      add_fcst_postproc_task(root)
      add_fcst_gfdl_tracker_task(root)
   if cfg.perform_archive and not cfg.debug_mode:
      add_archive_task(root)
   add_postproc_experiment_task(root)

def add_coldstart_workflow_tasks(root):
   ''' Create task elements for coldstart exp '''
   if not cfg.reuse_static_data:
      root = add_wps_task(root)
      root = add_real_task(root)
   add_wrf_det_fcst_task(root)
   if cfg.perform_postproc_fcst:
      add_fcst_diapost_task(root)
      add_fcst_upp_task(root)
      add_fcst_postproc_task(root)
      add_fcst_gfdl_tracker_task(root)
   if cfg.perform_archive and not cfg.debug_mode:
      add_archive_task(root)
   add_postproc_experiment_task(root)

def add_enkf_workflow_tasks(root):
   
   if not cfg.reuse_static_data:
      add_wps_task(root)
      add_real_task(root)
      add_ensemble_wps_task(root)
      add_ensemble_real_task(root)
   if cfg.perform_enkf_additive_inflation:
      add_additive_inflation_task(root)   
   
   if cfg.warm_init:
      root = add_dummy_task(root)
   else:
      root = add_wrf_spinup_task(root)
   
   add_gsi_ensmean_task(root)
   add_gsi_task(root)
   add_wrf_ges_task(root)
   add_wrf_det_fcst_task(root)
   add_enkf_task(root)
   if cfg.perform_postproc_cycle:
      add_cycle_postproc_task(root)
   if cfg.perform_postproc_fcst:
      add_fcst_diapost_task(root)
      add_fcst_upp_task(root)
      add_fcst_postproc_task(root)
      add_fcst_gfdl_tracker_task(root)
   if cfg.perform_ensemble_analysis_upp:
      add_ensemble_analysis_unipost_task(root)
   if cfg.perform_ensemble_ges_upp:
      add_ensemble_ges_unipost_task(root)
   add_cleanup_task(root)
   if cfg.perform_archive and not cfg.debug_mode:
      add_archive_task(root)
   add_postproc_experiment_task(root)


def output_xml_to_file(root, xmlFile):
   '''
   Dump contents of ElementTree <root> to <xmlFile>
   '''
   out = ET.tostring(root)
   xmlOut = xml.dom.minidom.parseString(out)
   xmlText = xmlOut.toprettyxml()
   # hack to replace generated &amp;
   for line in xmlText.splitlines():
      line = line.replace('&amp;', '&')
      xmlFile.write(line + '\n')
   #print xmlText
   #tree = ET.ElementTree(root)
   #tree.write("filename.xml")


def create_common_workflow_header():
   '''
   Creates the basic header elements that are shared by both GSI and EnKF 
   workflow definitions. This includes the cycledefs.
   RETURN
     ElementTree node with the common elements added to it
   '''
   root = ET.Element('workflow')
   root.set('realtime', 'F')
   root.set('scheduler', cfg.batch_system_name)
   root.set('cyclethrottle', CYCLE_THROTTLE) # allow N cycles to execute in parallel (ALA deps are met)
   add_wf_log(root, 'workflow/workflow_@Y@m@d@H@M')

   add_cycle_defs(root)
   
   return root 


def create_gsi_workflow(xmlFile):
   '''
   Creates XML definition for a GSI experiment
   '''
   global g_member_str
   # sanity check 
   if cfg.da_type != 'gsi':
      sys.stderr.write('Sanity Check failed. Please set $DA_TYPE in experiment.cfg.sh to "gsi" ')
      sys.exit(1)
   g_member_str = 'NA'
   root = create_common_workflow_header()
   add_gsi_workflow_tasks(root)
   output_xml_to_file(root, xmlFile)
   

def create_enkf_workflow(xmlFile):
   '''
   Create workflow for EnKF run. Write contents to <xmlFile>
   '''
   global g_member_str
   # sanity check
   if cfg.da_type != 'enkf':
      sys.stderr.write('Sanity Check failed. Please set $DA_TYPE in experiment.cfg.sh to "enkf" ')
      sys.exit(1)
   g_member_str = '#member#'
   root = create_common_workflow_header()
   add_enkf_workflow_tasks(root)
   output_xml_to_file(root, xmlFile)   

def create_coldstart_workflow(xmlFile):
   '''
   Create a workflow for running just cold start forecasts
   '''
   if cfg.da_type != 'coldstart':
      sys.stderr.write('Sanity Check failed. Please set $DA_TYPE in experiment.cfg.sh to "coldstart" ')
      sys.exit(1)
   root = create_common_workflow_header()
   add_coldstart_workflow_tasks(root)
   output_xml_to_file(root, xmlFile)

   
def date_to_time_struct(eldate):
   '''
   Given a date in seconds since epoch, return a TimeStruct
   '''
   ts = TimeStruct()
   datestruct = time.localtime(eldate)

def find_existing_data(datadir):
   '''
   The user may specify that certain data already exists in a given location.
   In this case, look for data in this location
   '''
   global g_skip_cold_start_hwrf, g_skipable_wps, g_skipable_real

   # first check if cold start data is available for all members
   num_found = 0
   for i in ( CTRL_PLUS_DA_IDX, range(cfg.num_members) ):
      datapath = os.path.join(datadir, cfg.member_dir_prefix + zeropad(i) )
      wps_path = os.path.join( datapath, 'WPSV3')
      last_fcst_date = g_start_time + cfg.forecast_duration 
      ts = time.localtime(last_fcst_date)
      last_ouptut = 'wrfout_d01_%s-%s-%s_%s:%s:%s' %(ts.tm_year, ts.tm_mon, ts.tm_mday, ts.tm_hour, 
         ts.tm_min, ts.tm_sec)
      cold_start_output_path = os.path.join( datapath, 'ATMOS' + get_wrf_dir_suffix(cfg.start_date) , 
         last_output )
      # See if cold-start data exists
      if os.path.exists( cold_start_output_path ):
         num_found += 1
      else:
         break
   if num_found == cfg.num_members + 1 : # Add 1 for CTRL+DA run (TODO: check if we're actually doing the CTRL+DA
      print 'Found wrfouts for all members. Will skip cold start run generation in workflow.'


#if __name__ == '__main__':
def generate_workflow(conf, workflow_type):
   '''
   This is the main routine used to generate the workflow's XML file.
   The Cfg object generated by read_config() needs to be passed in.
   '''
   global cfg, g_start_time

   #parse_options()

   #cfg = read_config()
   cfg = conf
   startDay = '%s/%s/%s %s%s' %(cfg.start_date.month, cfg.start_date.day, cfg.start_date.year, 
                                cfg.start_date.hour, cfg.start_date.minute)
   g_start_time = int( time.mktime( time.strptime(startDay, '%m/%d/%Y %H%M') ) )

   elfile = open('entities.txt', 'w')
   add_entities(elfile)
   elfile.close()
   elfile = open('entities.txt', 'r')
   xmlfile = open('wf.xml', 'w')
   if workflow_type == 'gsi':
      create_gsi_workflow(xmlfile)
   elif workflow_type == 'enkf':
      create_enkf_workflow(xmlfile)
   elif workflow_type == 'coldstart':
      create_coldstart_workflow(xmlfile)
   else:
      sys.stderr.write('Invalid workflow type')
      sys.exit(1)
   xmlfile.close()
   xmlfile = open('wf.xml', 'r')
   
      
   # re-construct XML file with entities
   workflow = open('workflow.xml', 'w')
   workflow.write('<?xml version="1.0"?>\n')
   for line in elfile:
      workflow.write(line)
   xmldata = xmlfile.readlines()
   for i in range(1, len(xmldata) ): # skip header
      xmldata[i] = xmldata[i].replace('&lt;', '<')
      xmldata[i] = xmldata[i].replace('&gt;', '>')
      xmldata[i] = xmldata[i].replace('&quot;', '"')
      workflow.write( xmldata[i] )

   workflow.close()
   elfile.close()
   xmlfile.close()
   os.remove('wf.xml')
   os.remove('entities.txt')

def generate_gsi_workflow(cfg):
   generate_workflow(cfg, 'gsi')

def generate_enkf_workflow(cfg):
   generate_workflow(cfg, 'enkf')   

def generate_coldstart_workflow(cfg):
   generate_workflow(cfg, 'coldstart')
