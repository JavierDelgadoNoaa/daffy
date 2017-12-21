#
# Settings for the WPS application
#
export WPS_TEMPLATE=${TEMPLATES_DIR}/wps.template.nl
export WPS_ROOT=${APPS_ROOT}/wps/${MODEL_CONFIG_ID}/vanilla/WPSV3
export WPS_OUTPUT_SUBDIR=WPSV3 # relative to member output dir

export WPS_TIME_INTERVAL=3600
#export WPS_TIME_INTERVAL=$TIME_LEVEL_PERIOD # This is defined in gsi.cfg.sh and may be needed for multi time level analysis

#
# Settings for boundary data using basic GFS data
#

# Set location of GFS data (determinsitic and ensemble)
export GFS_ROOT=${STATIC_DATA_ROOT}/meso_osse/GFS/
export GFS_ENSEMBLE_ROOT=${GFS_ROOT}

# string used to identify the boundary data being used for forecasts
# These should correspond to direct subdirectories of $GFS_ROOT/$GFS_ENSEMBLE_ROOT 
# for deterministic forecasts:
export GFS_FCST_ID='jcsda_hybrid_control'
# for ensembles:
export GFS_ENSEMBLE_ID='JCSDA_ENKF_control'

# Prefix used for Ungrib stage
export WPS_UNGRIB_PREFIX='FILE'

# How frequent are the GFS forecasts available (in seconds) ?
# Actually, what this really sets is how often do we run WPS ?
export WPS_GFS_FREQUENCY=$(( 6 * 60 * 60 ))
# How long are the GFS forecasts (seconds)
#export WPS_GFS_FCST_DURATION=$(( 120 * 60 * 60 ))
export WPS_GFS_FCST_DURATION=$(( 126 * 60 * 60 )) # for testing set to 24 hr
# What range of dates do we have initial/boundary condition data for? (values are in seconds since epoch)
export WPS_GFS_START_DATE=`date -d 07/29/2005 +%s`
# On what date does GFS data end?
export WPS_GFS_END_DATE=`date --date="08/09/2005 18:00" +%s`


# 
# Settings for ensemble data for boundary condtions
#

export GFS_ENSEMBLE_DATA_SUBDIR=''

# File name pattern of the Grib files used for GFS background. The following strings will be converted:
#  <fhrNN> -  2-digit forecast hour
#  <fhrNNN> - 3-digit forecast hour
#  <fhrAAA> -  forecast hour, arbitrary amount of digits
#  <YYYY> - 4 digit year
#  <YY> - 2-digit year
#  <MM> -- 2-digit month
#  <DD> - 2-digit day
#  <hh> - 2-digit hour
#  <mm> - 2-digit minute
#  <memNumNN> - 2-digit member number
#  <memNumNNN> - 3-digit member number
# The current code actually just treats them as arbitrary numbers of corresponding 
#  length, which should be sufficient
# for for ensemble forecasts
# # climapert
 export GFS_ENSEMBLE_FILE_PATTERN="pgrbfg_<YYYY><MM><DD><hh>_fhr<fhrNN>_mem<memNumNNN>"
 # esrl
#export GFS_ENSEMBLE_FILE_PATTERN="pgbf<fhrNN>.gfs.<YYYY><MM><DD><hh>.mem<memNumNNN>"

# for deterministic forecast
export GFS_FCST_FILE_PATTERN="pgbf<fhrAAA>.gfs.<YYYY><MM><DD><hh>"
# For ARW NR as b/g - daffy assumes that all files needed will have the date, so just copy all the files over
#export GFS_FCST_FILE_PATTERN="arwNR.d01.<YYYY><MM>*"
# duration of the ensemble forecasts
export GFS_ENSEMBLE_FORECAST_DURATION=$(( 9 * 3600 )) # seconds



# Number of Metgrid Levels (this value is only used if we can't obtain it from
# a met_nmm file or a text file that the WPS script writes it to
export NUM_METGRID_LEVELS=48


# Interval for interpolation of GFS boundary data (i.e. "interval_seconds" field of WPS namelist)
# For EnKF runs, this should be a multiple of the TIME_INTERVAL
#export WPS_INTERVAL=$CYCLE_FREQUENCY
export WPS_INTERVAL=3600

# Name to identify the source of data being used for initial/boundary conditions
#export METGRID_DATA_SOURCE=JCSDA_control
#export ENSEMBLE_METGRID_DATA_SOURCE=$GFS_ENSEMBLE_ID

export WPS_VTABLE=${WPS_ROOT}/ungrib/Variable_Tables/Vtable.GFS

# To ensure that the static (previously generated WPS and Real) data correspond
# to the same Metgrid and Geogrid Tables, we place them in a subdirectory
# named according to the md5 sum of the respective .TBL
# TODO : Geogrid checksum should also use the grid extents and resolution
# Metgrid one should use those and other namelist parameters.
export GEOGRID_CHECKSUM=`md5sum $WPS_ROOT/GEOGRID.TBL | awk '{print $1}'`
export METGRID_CHECKSUM=`md5sum $WPS_ROOT/METGRID.TBL | awk '{print $1}'`

# Directory containing time-invariant static data used by Geogrid
export GEOGRID_DATA_PATH=${STATIC_DATA_ROOT}/domain_data/geostatic/hwrf_wps_geo
# Directory containing Geogrid output for a given domain
export GEOGRID_OUTPUT_DATA_PATH=${STATIC_MODEL_DATA_PATH}/geogrid

export GEOGRID=$WPS_ROOT/geogrid.exe
export UNGRIB=$WPS_ROOT/ungrib.exe
export METGRID=$WPS_ROOT/metgrid.exe

# remove met_nmm files after running Real, since they are not needed after that
# This is fairly safe, but relies on certain assumptions (e.g. WPS_FREQUENCY is
# always used to determine when to run WPS).
# You may want to leave it false to be safe
export PURGE_METGRID_FILES=TRUE
