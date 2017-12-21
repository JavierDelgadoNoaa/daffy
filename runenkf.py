#!/usr/bin/env python
import sys
import time
import os
from lib.cfg import read_config
from lib.workflow_generator import generate_gsi_workflow, generate_enkf_workflow
from optparse import OptionParser
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
class EnkfExperimentRunner(ExperimentRunner):
   def __init__(self, cfg):
      self.cfg = cfg
      
##
# VARS
##
DEFAULT_ROCOTO_VERBOSITY = '3' # just shows failures
# TODO make it default to loaded  module version
WORKFLOW_ENGINE_PATH = '/apps/rocoto/1.2.3/bin/rocotorun'

##
# METHODS
##

#def runcmd(cmd):
def runcmd():
    global g_rocoto_running
    if not os.path.exists(WORKFLOW_ENGINE_PATH):
       log.error('Path to workflow engine does not exist [%s]' %WORKFLOW_ENGINE_PATH)
       sys.exit(1)
    #cmd = '%s -w workflow.xml -d %s' %(rocotorun, cfg.rocoto_db_path)
    #cmd = '/apps/rocoto/1.1/bin/%s -w workflow.xml -d %s' %(rocotorun, cfg.rocoto_db_path) 
    rocoto_db_file = get_rocoto_db_file(cfg) # get temporary state file, if necessary
    cmd = [WORKFLOW_ENGINE_PATH, '-w', 'workflow.xml', '-d', rocoto_db_file]
#  test
#  cmd = ['sleep', '15']
    
    g_rocoto_running = True
    import subprocess
    #p = subprocess.Popen(cmd)
    #p.wait()
    #print 'running'
    
    #orig
    #p = subprocess.call(cmd)
    # for Python 2.7
    #output = subprocess.check_output(cmd)
    # for earlier python
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output = p.communicate()[0].strip()
    commit_rocoto_state_file(cfg) # move state file back to working path, if  necessary
    
    g_rocoto_running = False
    
    # TODO
    if len(output) > 0:
       handle_workflow_output()


def sigint_handler_kludge(signum, frame):
   log.info('Clean exit')
   sys.exit(0)

def sigint_handler(signum, frame):
   '''
   This is supposed to be the standard signal handler for the workflow monitor. It
   delays the termination of the program if Rocoto is being invoked, to prevent the
   possibility of the workflow state file being corrupted.
   However, If the user sends to continuous SIGINT's, it will quit.
   Currently this behavior is not working, though, see comment in the Main function
   '''
   global sigint_sent
   print '\n\nhandling\n\n'
   if sigint_sent:
        print "Process terminated abruptly. Workflow state may be compromised"
        sys.exit(1)

   if g_rocoto_running:
     print 'Workflow is being invoked, will terminate shortly. Press Ctl+C again to force unclean shutdown'
     while(g_rocoto_running):
       time.sleep(0.5)
     sys.exit(0)
   else:
     log.debug('Clean exit')
     sys.exit(0)

   sigint_sent = True

##
#  MAIN
##
if __name__ == '__main__':
   
   sigint_sent = False
   
   cfg = read_config()
   log = DaffyLog(cfg.log_level)
   enkf_runner = EnkfExperimentRunner(cfg)
   enkf_runner.set_log(log)
   
   # This flag is set to True when rocoto is running
   g_rocoto_running = False 
   #import pdb ; pdb.set_trace()
   
   # Parse options and check for potential hazards
   parse_options(enkf_runner)

   if cfg.debug_mode :
      log = DaffyLog(DaffyLog.DEBUG)
      cfg.debug_mode_str = 'TRUE'
   else:
      cfg.debug_mode_str = 'FALSE'

   if cfg.warm_init or cfg.cold_init :
      generate_enkf_workflow(cfg) # cold/warm-specific changes are handled internally
      if not os.path.exists('workflow.xml'):
         print ':O workflow.xml was not created. Something is wrong'
         sys.exit(1)
      log.info('Generated workflow definition file "workflow.xml"')

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

      if os.path.exists(cfg.rocoto_db_path):
         log.warn( 'Workflow state file already exists. Workflow will be continued accordingly.')
         log.info('To restart the experiment, remove state file [%s]' %cfg.rocoto_db_path)

      log.info('This executable is unresponsive to Ctrl+C/SIGINT while the workflow engine is being invoked')
      while(1):
         #rocotorun = os.path.join(cfg.rocoto_path, 'bin', 'rocotorun -v' + cfg.rocoto_verbosity)
         rocotorun = 'rocotorun -v ' + cfg.rocoto_verbosity 
         #rocotorun = 'rocotorun' # use stable/module version of Rocoto
         #log.info(' EXEC :: %s -w workflow.xml -d %s' %(rocotorun, cfg.rocoto_db_path) )
         #cmd = '%s -w workflow.xml -d %s' %(rocotorun, cfg.rocoto_db_path) 
         
         # To prevent the state file from being compromised due to sending SIGINT (i.e. Ctl+C) while
         # rocoto is running, we add a special handler for the signal.
         # The default POSIX behavior is for forked processes to inherit the paren't signal dispositions,
         # unless the signals are ignored which are left unchanged, so we need to turn off the handling of 
         # SIGINT while we start the child process and turn it back on (actually, set its handler) after
         signal.signal(signal.SIGINT, signal.SIG_IGN)
         #t1 = threading.Thread(target=runcmd, args=(cmd))
         t1 = threading.Thread(target=runcmd)
         t1.start()
         
         #signal.signal(signal.SIGINT, sigint_handler)  
         # Well, POSIX behavior is not being followed, so naturally we resort to a hack - 
         # sleep for a bit while Rocoto starts and then wait until it finishes to re-set the
         # signal handler
         time.sleep(0.3)
         while(g_rocoto_running): time.sleep(0.5)
         signal.signal(signal.SIGINT, sigint_handler_kludge)
         commit_to_local_database(enkf_runner)
         if experiment_complete( get_rocoto_db_file(cfg) ):
            add_to_global_database(cfg)
            log.info('Experiment Completed. Good bye')
            break
         time.sleep(cfg.poll_interval)
   #TODO : add elif for cron mode

   else:
      log.info('Neither monitor nor cron support requested. My work here is done')

