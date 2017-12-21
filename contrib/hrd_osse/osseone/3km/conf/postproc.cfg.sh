# MAIN PRODUCTS DIR name.  All products will be created under $RUN_TOP_DIR/$PRODUCTS_DIR.<cycle date>
export PRODUCTS_DIR=PRODUCTS
# Setting this to FALSE will disable all postprocessing of forecasts
export PERFORM_POSTPROC_FCST='TRUE'
# Setting this to FALSE will disable all postprocessing of analysis/guess data
export PERFORM_POSTPROC_CYCLE='FALSE'
# Setting this to TRUE will result in generating UPP data for all members of the analysis (posterior only)
export PERFORM_UPP_ENSEMBLE_ANALYSIS='FALSE'
# Setting this to TRUE will result in generating UPP data for all members of the guess forecast
export PERFORM_UPP_ENSEMBLE_GES='FALSE'
# Setting this to False will skip the experiment-wide postprocessing. Note: Must be TRUE If doing archive
export PERFORM_EXPERIMENT_POSTPROC='TRUE'

# The experiment will have cycle-specific and entire experiment products
# products that pertain to the entire experiment will go here
export EXPERIMENTAL_PRODUCTS_OUTPUT_DIR=${RUN_TOP_DIR}/PRODUCTS.experimental_averages

# Path to utility to calculate TC stats
export TC_STATS_UTIL_DIST=${APPS_ROOT}/postproc_utils/tcstats/
export TCVITALS_DOM=02 # Domain of experimental model execution on which to process TC stats 
# Path to utility to get average of domain average errors
export DOMAIN_AVERAGE_DIST=${APPS_ROOT}/postproc_utils/domain_stats/v1

# Directory containing the postprocessing scripts.
# Scripts in this directory ending with ".pp.fcst.zsh" will be sourced by the postproc_fcst job
# Scripts in this directory ending with ".pp.cycle.zsh" will be sourced by the postproc_cycle job
export POSTPROC_SCRIPTS=${JOB_SCRIPTS_DIR}/post

#
# Set paths
#
# Diapost
export DIAPOST_DIST=${APPS_ROOT}/diapost/hedas_sim_fft/dist
# UPP
export UPP_HOME=${APPS_ROOT}/upp/dtc/$MODEL_CONFIG_ID/osse

# Name of scripts that does UPP processing for each cycle
export UPP_CYCLE_SCRIPT=$UPP_HOME/scripts/run_unipost_osse.zsh
# interval between UPP outputs (in hours)
export UPP_FCST_INTERVAL=6

export CUMMULATIVE_TRACK_FILE=$RUN_TOP_DIR/../cummulative_fcst_track_gsi.txt

# These 3 variables describe the scructure of the _cold-start_ control data, 
# which are used for the generation of sawtooth plots
export COLDSTART_DATA_DIR=/lfs1/projects/hur-aoml/lbucci/meso_osse/hwrf/gfs/
export COLDSTART_RUN_PREFIX=ONE01L
export COLDSTART_DATA_SUBDIR=ATMOS

# This is the location of the other control, which assimilates the "conventional" obs
if [[ $DA_TYPE == 'gsi' ]] ; then
   export CONV_CONTROL_DATA_DIR=${EXT_ROOT}/projects/osse/experiments/gsi/control_v1/start_at_${COLD_START_YEAR}${COLD_START_MONTH}${COLD_START_DAY}${COLD_START_HOUR}/run
elif [[ $DA_TYPE == 'enkf' ]] ; then
  export CONV_CONTROL_DATA_DIR=${EXT_ROOT}/projects/osse/experiments/enkf/control_v1/start_at_${COLD_START_YEAR}${COLD_START_MONTH}${COLD_START_DAY}${COLD_START_HOUR}/run
fi

export NATURE_STATS_FILE=${STATIC_DATA_ROOT}/nature/trackNatureRunD02_jd.txt

# If TRUE, this will generate some basic figures for the prior and posterior as part of 
# the postproc_cycle script (e.g. mslp, phi, rh, tpw) and put them in 
# $RUN_TOP_DIR/graphics_$date
export GENERATE_STANDARD_FIGURES=TRUE

# Size of "process pool" (i.e. how many instances of UPP will run concurrently)
export NUM_CONCURRENT=4 

#
# For mplot
#
export MPLOT_DIST=${APPS_ROOT}/postproc_utils/mplot/1.1
# These 3 control which side-by-side comparison plots are generated
export TILE_VS_NATURE=FALSE
export TILE_VS_NATURE_AND_COLDSTART=FALSE
export TILE_VS_NATURE_AND_CONTROL=FALSE
export PDFTK=${EXT_ROOT}/local/bin/pdftk
# Nature run grib data
export NATURE_RUN_1KM_GRID_DATA_PATH=${STATIC_DATA_ROOT}/meso_osse/1km_NR/grib
# 
# For TC stats
#
export NATURE_RUN_ATCF_DIR=${STATIC_DATA_ROOT}/meso_osse/wrf-arw/atcf
export NATURE_RUN_ATCF_FOR_TCVITALS=atcfNRD03.txt
# domain on which all the TC vitals comparisons/calculations will be done
export TCV_DOMAIN=01

#
# For bias correction (not yet implemented)
#
export BIAS_CORRECTION_PLOT_DIST=${APPS_ROOT}/postproc_utils/bias_correction/v0
# the next 3 should be space-delimited strings
export BIASCORR_OB_TYPES='airs281SUBSET' 
export BIASCORR_SATELLITE_NAMES='aqua'
export BIASCORR_INSTRUMENT_NAMES='airs'

#
# For GFDL Vortex tracker
#
export cfg_gfdl_tracker_tcvitals_path=${STATIC_DATA_ROOT}/meso_osse/data/${DOMAIN}/tc_vitals_d03/
export cfg_gfdl_tracker_nl_template="$TEMPLATES_DIR/gfdl_tracker.nml"
export cfg_gfdl_tracker_verbosity=3 # 1-3
export cfg_gfdl_tracker_bin=${APPS_ROOT}/gfdl_vortex_tracker/dtc/3.5b/gfdl-vortextracker/trk_exec
export cfg_gfdl_tracker_util_path=${APPS_ROOT}/gfdl_vortex_tracker/dtc/3.5b/tracker_util
export cfg_grbindex=$cfg_gfdl_tracker_util_path/exec/grbindex.exe
export cfg_gfdl_tracker_products_subdir=tc_stats
export cfg_gfdl_tracker_atcf_file="atcf_trk.txt"
export cfg_gfdl_tracker_alt_atcf_file="alt_atcf_trk.txt"
export cfg_gfdl_tracker_cyclogenesis_atcf_file="cyclogenesis_atcf_trk.txt"
## Select the scheme to be used to generate the tracker input ('hwrftrk') files
# - "operational_moving" : Creates inputs centered at the TC-vitals of the 
#    corresponding forecast hour. Loosely follows the operational system.
# - "operational_static" : Like the above, but the location is static (i.e.
#      all forecast hours' inputs are centered at the initial time's TCV lat/lon
# - "basic" - Uses the highest resolution domain's UPP output interpolated onto 
#             the parent domain
# - "d01" - Just uses the parent domain's UPP output
#export cfg_two_doms_hwrftrk_generator="basic"
export cfg_two_doms_hwrftrk_generator="operational_moving"
export cfg_one_dom_hwrftrk_generator="basic"
