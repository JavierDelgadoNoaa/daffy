#!/bin/zsh -l
##
# This is the main configuration file. The main parameters of the run are set here.
# This script also sources the other configuration files inside ./conf .
#
# To interact with the main (python) code, this script will be sourced and the python variables
# populated from environment variables. So if the _name_ of one of these variables is 
# changed, the read_config() method of cfg.py must be updated accordingly
# Since the variables are being extracted from the environment, they must be exported
##


export EXPERIMENT_TOPDIR=/home/Javier.Delgado/projects/osse/experiments/test_enkf/with_additive_inflation
# Parent execution directory. (e.g. for source files)
export TOP_DIR=${EXPERIMENT_TOPDIR}/exec
# Parent Run directory
export RUN_TOP_DIR=${EXPERIMENT_TOPDIR}/run

# name of Domain being used
export DOMAIN=OSSEONE

# Set the start date
# NOTE: For warm start runs, this should be the previous cycle, and there should be
# copies of the ATMOS and GSI directories for the start date's cycle in the $RUN_TOP_DIR
# For cold start experiments, it should be the cold start (i.e. cycle_frequency seconds 
# before the first DA)
export START_YEAR=2005
export START_MONTH=08
export START_DAY=01
export START_HOUR=00
export START_MINUTE=00

export END_YEAR=2005
export END_MONTH=08
export END_DAY=05
export END_HOUR=00
export END_MINUTE=00

# Set the cold start date
# This will be used to determine whether to perform satellite data cycling.
# It may also be used in the postprocessing stage for the generation of comparison plots
export COLD_START_YEAR=2005
export COLD_START_MONTH=08
export COLD_START_DAY=01
export COLD_START_HOUR=00
export COLD_START_MINUTE=00

# Short identifier that will be appended to certain output files' names (e.g. UPP outs)
export EXPERIMENT_ID='test_enkf_newCfg'
# Short identifier for config version. This is currently used to set the paths for 
# HWRF and utilities that compile against it. It is also used when looking for
# previously generated static data.
export MODEL_CONFIG_ID='2014'

# expriment type (gsi or enkf or coldstart).
# Coldstart is not a DA experiment since nothing is cycled; this variable
# was created before we saw a need for this functionality (sorry)
export DA_TYPE='enkf'
# number of ensemble members for EnKF experiment (ignored for GSI experiment)
export NUM_MEMBERS=30

# For each value in this string, a file named <value>.cfg inside $GSI_OBS_CFG_TOPDIR will be used
# to determine the data to assimilate (see comments in these files for details)
export GSI_DATA_THIS_EXPERIMENT="control_v1 tc_vitals_d03"


# Interval (in _seconds_) between each cycle 
export CYCLE_FREQUENCY=$(( 6 * 3600 )) # in _SECONDS_
 
#
# Forecast Settings
#
# Duration of each forecast (rename to FORECAST_LENGTH) 
export FORECAST_DURATION=$(( 5 * 24 * 3600 )) # _Seconds_
# Offset (in seconds) from the start date at which to run the first forecasts
export FIRST_FORECAST=$(( 6  * 3600 )) # seconds
# How often do we run full forecasts (as opposed to just cycling)
export FORECAST_FREQUENCY=$(( 6 * 3600 )) # seconds

# What kind of file to use for DA (should be either 'wrfinput' or 'restart')
export DA_FILE_TYPE='wrfinput'

# Log information will be appended here
export DAFFY_LOG=$RUN_TOP_DIR/global_log.txt

# Log level (should be either DEBUG, INFO, WARN, or ERROR)
#  note: If the --debug flag is used, this will be set to DEBUG
export LOG_LEVEL='INFO'

# This is the root directory from which external utilities' paths will be
export EXT_ROOT=/home/Javier.Delgado

#
# The rest of the options can probably be ignored
#


# This will set -aeu in the enviornment. Set to False if you want to introduce
# bad code.
export STRICT_MODE='TRUE'

# Determine what system we're on (this will affect values of certain variables)
if [[ `hostname -f | grep pegasus | wc -l` -eq 1 ]] ; then
   export SUPERCOMPUTER='PEGASUS'
   export EXT_ROOT=/nethome/jdelgado
   export DATA_ROOT=$EXT_ROOT
   export APPS_ROOT=$EXT_ROOT/apps
   export STATIC_DATA_ROOT=${DATA_ROOT}/static
elif [[ -e /home/Javier.Delgado/jet.info || -e /home/Javier.Delgado/.daffy_theia ]] ; then
   [[ -e /home/Javier.Delgado/jet.info ]] && export SUPERCOMPUTER='JET'
   [[ -e /home/Javier.Delgado/.daffy_theia ]] && export SUPERCOMPUTER='THEIA'
   export EXT_ROOT=/home/Javier.Delgado
   export DATA_ROOT=$EXT_ROOT/projects/osse
   export APPS_ROOT=$EXT_ROOT/apps
   export STATIC_DATA_ROOT=${DATA_ROOT}/static
elif [[ `hostname | grep -c 'ssec.wisc.edu'` -gt 0 ]] ; then 
   export SUPERCOMPUTER='S4'
   export EXT_ROOT=/home/jdelgado
   export DATA_ROOT=/data/lbucci/osse
   export APPS_ROOT=/home/lbucci/osse/apps
   export STATIC_DATA_ROOT=${DATA_ROOT}/static
else
   echo "Undefined or Uknown \$SUPERCOMPUTER" | tee -a $DAFFY_LOG
   exit 1
fi

# Putting this here for now to keep it in the field of view until
# we decide on a strategy for it
# This is the path to the TC vitals cards that are used for TC Vitals assimilation
# in GSI. These are NOT used by the model (i.e. Real)
export TCV_DIR=${STATIC_DATA_ROOT}/domain_data/$DOMAIN/tc_vitals

# Directory in which static model-related files (i.e. geo_nmm, wrfinput, wrfbdy)
# files can be found. When using the --reuse parameter, existing files will be
# searched for in this directory.
export STATIC_MODEL_DATA_PATH=${STATIC_DATA_ROOT}/domain_data/$DOMAIN/

# Path to workflow manager (Note: It will attempt to use the one in the environment first)
export ROCOTO_PATH=${APPS_ROOT}/rocoto/current

# Interval between invocations of the workflow engine
export POLL_INTERVAL=200 # seconds 

# Assuming start_seconds (and end_seconds and next_cycle_seconds) is always 00
export START_SECONDS=00



export JOB_SCRIPTS_DIR=${TOP_DIR}/scripts
export CONF_DIR=$TOP_DIR/conf
export TEMPLATES_DIR=$TOP_DIR/templates
export AUX_SCRIPTS=${JOB_SCRIPTS_DIR}/aux_scripts

# These should probably stay the same, and changing them has not been thoroughly tested.
# The idea behind making them flexible is in case DAFFY needs to be integrated with other
# frameworks in the future
# number of digits to  use for numbers used in filenames (e.g. member-002)
export NUM_DIGITS=3 
# Individual members' directory names will be prefixed with this string
# (the suffix will be the <num_digits> long member number
# (e.g. ATMOS.<date>/member-001
export MEMBER_DIR_PREFIX="member-" 

# Subdirectory to put GSI o-f run data
export GSI_GES_DIR='GSI_OF'
# Subdirectory to put GSI analysis (o-a) run data
export GSI_ANALYSIS_DIR='GSI_ANALYSIS'
# Prefix of WPS directories
export WPS_DIR_PREFIX='WPSV3'
# Prefix of HWRF directories
export ATMOS_DIR_PREFIX='ATMOS'

# file that stores experiment configuration information in XML (this is merged with the global database
export LOCAL_DATABASE_FILE_NAME='config.xml'
# The global database file name. Local database is merged with this one when experiment successfully 
# completes. It will look for the latest file in this directory and merge with it.
export GLOBAL_DATABASE_PATH="$EXT_ROOT/projects/osse/experiments/database"

# These are here for dealing with older (and less intuitive) variable names
export YEAR=$START_YEAR
export MONTH=$START_MONTH
export FREQUENCY=$CYCLE_FREQUENCY
export RUN_LENGTH=$FORECAST_DURATION
export FORECAST_LENGTH=$RUN_LENGTH


# Obtain other configuration values
source ${CONF_DIR}/domain.cfg.sh # Modify this to set the domain properties 
source ${CONF_DIR}/wps.cfg.sh
source ${CONF_DIR}/model.cfg.sh
source ${CONF_DIR}/gsi.cfg.sh
source ${CONF_DIR}/scheduler.cfg.sh
source ${CONF_DIR}/postproc.cfg.sh
source ${CONF_DIR}/env.cfg.sh
source ${CONF_DIR}/hacks.cfg.sh
source ${CONF_DIR}/enkf.cfg.sh
source ${CONF_DIR}/archive.cfg.sh
[[ -e ${CONF_DIR}/site_specific.cfg.sh ]] && source ${CONF_DIR}/site_specific.cfg.sh

set -x
