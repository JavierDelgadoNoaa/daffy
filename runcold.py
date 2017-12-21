#!/usr/bin/env python
import sys
import time
import os
from lib.cfg import read_config
from lib.workflow_generator import generate_coldstart_workflow
import shutil
import logging as log
import signal
import threading
from lib.daffy_log import DaffyLog
from lib.common import print_experiment_info, parse_options, get_rocoto_db_file, commit_rocoto_state_file, commit_to_local_database, ExperimentRunner, experiment_complete, add_to_global_database

try:
   import wrfutils # export PYTHONPATH=~Javier.Delgado/scripts/py
   import jdutils
except:
   print ':( Unable to import wrfutils. Try adding ~Javier.Delgado/scripts/py to PYTHONPATH'
   sys.exit(1)

##
# Classes
##
class ColdStartExperimentRunner(ExperimentRunner):
   def __init__(self, cfg):
      self.cfg = cfg


##
#  MAIN
##
if __name__ == '__main__':
   
   cfg = read_config()
   log = DaffyLog(cfg.log_level)
   experiment_runner = ColdStartExperimentRunner(cfg)
   experiment_runner.set_log(log)
   parse_options(experiment_runner)

   if cfg.warm_init or cfg.cold_init :
      generate_coldstart_workflow(cfg) # cold/warm-specific changes are handled internally
      if not os.path.exists('workflow.xml'):
         print ':O workflow.xml was not created. Something is wrong'
         sys.exit(1)

   if os.path.exists(cfg.run_top_dir) and not cfg.force_execution : 
      sys.stdout.write('Path %s already exists. Using -f option will append to it (and possibly overwrite its contents).\n' %(cfg.run_top_dir) )
      sys.exit(1)
   
   # Copy configuration files to Run directory
   if not os.path.exists(os.path.join(cfg.run_top_dir, 'cfg', 'conf') ) :
      os.makedirs( os.path.join(cfg.run_top_dir, 'cfg', 'conf') )
   shutil.copy(cfg.config_file_path, os.path.join(cfg.run_top_dir, 'cfg') )
   for fil in os.listdir( 'conf'): 
      if fil.endswith('.cfg.sh'): shutil.copy( 'conf/' + fil , os.path.join(cfg.run_top_dir, 'cfg', 'conf') )

   if cfg.warm_init or cfg.cold_init :
      print_experiment_info(cfg, log)

   # main loop
   if cfg.monitor_mode:
      
      if not os.path.exists('workflow.xml'):
         print 'Workflow definition does not exist. Generate it using the --cold-init or --warm-init option'
         sys.exit(1)

      # try to find Rocoto in the environment. If not found, try the one specified in experiment.cfg.sh
      try:
         loaded_modules = os.environ['LOADEDMODULES']
      except:
         loaded_modules = None
      if loaded_modules != None:
         try:
            idx = loaded_modules.index('rocoto')
         except ValueError:
            print 'Rocoto not found in $LOADEDMODULES. Try "module load rocoto/1.1"'
            sys.exit(1)
         if idx :
            try:
               rocoto_version = float( loaded_modules[idx+7:idx+10] )
            except:
               print 'Unable to determine loaded Rocoto version. This is a bug, please notify a developer'
               sys.exit(1)
            if rocoto_version < 1.1:
               print 'Need Rocoto >= 1.1 . Either load it (e.g. "module load rocoto/1.1") or \
                      unload it, install it separately, and set its path in experiment.cfg.sh'
               sys.exit(1)
            else:
               rocotorun = 'rocotorun'
      else:
         rocotorun = os.path.join( cfg.rocoto_path , 'bin', 'rocotorun')

      if os.path.exists(cfg.rocoto_db_path):
         log.warn( 'Workflow state file already exists. Workflow will be continued accordingly.')
         log.info('To restart the experiment, remove state file [%s]' %cfg.rocoto_db_path)

      while(1):
         rocoto_db_file = get_rocoto_db_file(cfg) # get temporary state file, if necessary
         os.system('%s -w workflow.xml -d %s -v %s' %(rocotorun, rocoto_db_file, cfg.rocoto_verbosity) )
         commit_rocoto_state_file(cfg) # move state file back to working path, if  necessary
         commit_to_local_database(experiment_runner)
         if experiment_complete( get_rocoto_db_file(cfg) ):
            add_to_global_database(cfg)
            log.info('Experiment Completed. Good bye')
            break
         time.sleep(cfg.poll_interval)
         
         
   #TODO : add elif for cron mode

   else:
      print 'Neither monitor nor cron support requested. My work here is done'

