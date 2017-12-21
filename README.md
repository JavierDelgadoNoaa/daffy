UPDATE: 
  Choosing a configuration
   - Recall that the configuration of an experiment is dictated by the 
     configuration options (in the conf/*.cfg.sh) and the templates
     (in the templates directory). The 'contrib' folder contains 
     configuration-reolated files for different configurations. 
     Since some config related options (i.e. execution times and
     resource requirements) are currently hardcoded in the 
     workflow generator, there may be a workflow generator there 
     as well. 
     For HRD OSSE related configurations, you can look at 
     "contrib/hrd_osse/configurations/<domain name>" for a list
     of configurations. In this directory you'll find subdirectories
     for templates/ and conf/ containing config files that differ for
     the default (9/3) configuration and the other configurations (e.g. 
     uniform 3km). Only files that differ are put in these directories
     to avoid having to maintain multiple version of all the config files.
     This means that they must be individually linked. 


DEVELOPMENT PHILOSOPHY

The framework was designed to allow experiments to be started, debugged, and 
resumed randomly.
The main script for running GSI experiments is "rungsi.py". Use the "-h" option
to see available options. Basically, you generate a workflow definition using the
"--cold-init (-c)" or "--warm-init (-w)" option and then run the experiment using
the "--monitor (-m)" option. 
By default, subsequent invocations of the program with -m will automatically resume
the experiment. To start from scratch, you will have to remove the workflow state
information file (i.e. database), which is $RUN_DIR/rocotodb.sql

The configuration is done via configuration files and templates. In the configuration files, 
you generally set dynamic parameters and/or system-specific parameters. Although this is
not always the case, since it's easier to modify setting in a config file that to search
for where to set the same parameter in a template, generally speaking.

CONFIGURING THE EXPERIMENT

   GENERAL CONFIGURATION

   The main configuration files is "experiment.cfg.sh" in the top-level directory.
   It contains basic experiment-related configuration settings such as the 
   start and end times of the experiment, the cycle frequency, and the duration and
   frequency of forecasts.
   
   CONFIGURATION OF INDIVIDUAL TASKS
   
   Inside the "conf" directory, there are individual configuration files for different
   aspects of the experiment.
   
       DOMAIN CONFIGURATION
       
       domain.cfg.sh contains domain-related settings. Anything that cannot be set here must
       be set in the namelist templates for WRF and/or WPS in $TEMPLATES_DIR (default: scripts/templates).
          
       OBSERVATION DATA CONFIGURATION
       
       The following 3 variables in gsi.cfg.sh determine the data that is assimilated:
           GSI_OBS_DATA_TOPDIR - Root directory where observation data files reside
           GSI_OBS_CFG_TOPDIR - Root directory where configuration files describing how data
                                in the above directory are to be used at runtime
           GSI_DATA_THIS_EXPERIMENT - Space-separated string that specifies which configuration
                                      files in GSI_OBS_CFG_TOPDIR are to be processed for the experiment.
                                      See comments in the cfg files in GSI_OBS_CFG_TOPDIR to get a better
                                      idea of how the data is processed in order to be assimilated by GSI
