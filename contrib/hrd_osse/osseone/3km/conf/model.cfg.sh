
# define the "history interval". Note: You can use different values for different domains
# Note that this depends on whether its a cycle or forecast
export WRFOUT_INTERVAL="360, 360"
export RESTART_INTERVAL="72000, 36000"

#export WRF_ROOT=${APPS_ROOT}/wrf/2014/osse/WRFV3
export WRF_ROOT=${APPS_ROOT}/wrf/${MODEL_CONFIG_ID}/osse/WRFV3

# These are the TC Vitals used by Real to place the nest and by Diapost to set
# the "storm_center". They are not used by GSI
export TCVITALS_DIR=${STATIC_DATA_ROOT}/nature/TCVITALS/locations_arw_d03
export TC_FILE_PREFIX=ONEARW01L.

export SWCORNER=${APPS_ROOT}/hwrf-utilities/xuejin_swcorner/hwrf_swcorner_dynamic.exe

export WRF_INPUT_FILE_PREFIX="wrf_3dvar_input"

# NOTE: These should not be used with the current paradigm of using 3dvar files
#export RESTART_FILE_PREFIX=wrfrst_d01_prior_
export RESTART_FILE_PREFIX=wrfrst
#export RESTART_FILE_SUFFIX=_TEST1
export RESTART_FILE_SUFFIX=''

# Set HWRF namelist template, depending on the version of hwrf being used
export WRF_NAMELIST_TEMPLATE=${TEMPLATES_DIR}/_wrf_template.nl
if [[ `echo $WRF_ROOT | grep -c 2014` > 0 ]] ; then
   export WRF_NAMELIST_TEMPLATE=${TEMPLATES_DIR}/hwrf2014_3_OSSEONE.nl
fi

# These are the restart and wrfinout intervals for non-restartgen runs
export FCST_RESTART_INTERVAL=36000
export FCST_WRFINPUT_INTERVAL=36000

# These are the three tools used for boundary smoothing
export BOUNDARY_TOOLS_ROOT=${APPS_ROOT}/gsi_util/boundary_tools/$MODEL_CONFIG_ID
export ANALYSIS_BOUNDARIES=${BOUNDARY_TOOLS_ROOT}/analysis_boundaries/ANALYSIS_BOUNDARIES.exe
export UPDATE_BC_NMM=${BOUNDARY_TOOLS_ROOT}/update_bc_nmm/UPDATE_BC_NMM.exe
export BDY_UPDATE=${BOUNDARY_TOOLS_ROOT}/bdy_update/BDY_UPDATE.exe

# Additive inflation settings
export ADDITIVE_INFLATION=${APPS_ROOT}/hybrid_enkf_system/additive-inflation/ADDITIVE_INFLATION.exe
export PERFORM_ENKF_ADDITIVE_INFLATION=TRUE
export ENKF_ADDITIVE_INFLATION_COEFF=0.5

# Auxillary history file
export AUXHIST_PREFIX="gsi_wrfhwrf_d<domain>_<date>"
# Interval at which to write auxillary history files used by GSI. This should match TIME_LEVEL_INTERVAL in conf/gsi.cfg.sh
export AUXHIST_INTERVAL=$(( 60 * 60 )) # seconds
# Gotta set this to 15 even though its only needed every hour due to output behavior of restart runs
export AUXHIST_INTERVAL=$(( 15 * 60 )) # seconds

