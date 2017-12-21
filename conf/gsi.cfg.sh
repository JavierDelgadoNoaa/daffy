#
# Observation data configuration
#

# Root directory in which to find observation data. This is value will be passed to the 
# copy_gsi_obs.py script as the <GSI_OBS_DATA_TOPDIR> variable. Data outside this directory
# will need to specify its full path in the gsi_obs_mappings configuration files
export GSI_OBS_DATA_TOPDIR=${STATIC_DATA_ROOT}/meso_osse/data/$DOMAIN

# Directory containing individual configuration files that map data to be assimilated to where it resides
export GSI_OBS_CFG_TOPDIR=${CONF_DIR}/gsi_obs_mappings

# Some datasets may have missing data for some dates. By default, any time a missing data
# is encountered, the experiment fails. Adding certain data's tag to this line will 
# cause the experiment to continue even if data is missing.
export SPORADIC_DATASETS='cris'
# If this is True and the file corresponding to an ob that is not in the SPORADIC_DATASETS is missing, 
# the GSI task will be force failed with exit status 3
export GSI_FAILS_IF_OBS_MISSING='TRUE'

# By default, the GSI script will fail if GSI executes properly but no obs are assimilated.
# Setting this to true will cause it to proceed in these cases.
export PROCEED_IF_NO_DA=FALSE

# 
# Set paths for GSI and related utilities
#

# Top-level directory of GSI 
#export GSI_ROOT=${APPS_ROOT}/gsi/mingjing/201402_2/GSI/
export GSI_ROOT=${APPS_ROOT}/gsi/comgsi/3.3/${MODEL_CONFIG_ID}
# GSI executable to use
export GSI_EXE=${GSI_ROOT}/run/gsi.exe

# Path to executable used for satellite data cycling
# Leaving this undefined will skip this step
export SATANG_UPDATE_DIR=${GSI_ROOT}/util/gsi_angupdate
# Namelist to use for SATANG_UPDATE. Note that different GSIs use different ones
export SATANG_UPDATE_NAMELIST='global_angupdate.namelist'
if [[ `grep -c global_angupdate.nml ${SATANG_UPDATE_DIR}/main.?90` -gt 0 ]] ; then
   export SATANG_UPDATE_NAMELIST='global_angupdate.nml' # For older and for EMC
fi
export SATANG_UPDATE_EXE=${SATANG_UPDATE_DIR}/gsi_angupdate.exe

# Namelist to use for GSI
if [[ $DA_TYPE == 'gsi' ]] ; then
   export GSI_NL_TEMPLATE=${TEMPLATES_DIR}/gsiparm_o_minus_a.nl
elif [[ $DA_TYPE == 'enkf' ]] ; then
   export GSI_NL_TEMPLATE=${TEMPLATES_DIR}/gsiparm_o_minus_f.nl
fi
export GSI_ENSMEAN_TEMPLATE=${TEMPLATES_DIR}/namelist.ensemble-mean 

# deprecated - just putting it directly into template
#export OBS_INPUT_FILE=${TEMPLATES_DIR}/gsi_obsinput.cfg

# the niter-related section of the namelist will be replaced with this
# this is also deprecated; using separate namelist templates for each
#export NUM_ITER_ANALYSIS="miter=2,niter(1)=70,niter(2)=70," #analysis
#export NUM_ITER_OF="miter=0,niter(1)=1,niter(2)=1," # o-f

# Domain on which data assimilation will be performed (NOTE: this has only been tested on 01)
export ANALYSIS_DOMAIN=01
# Assimilation time window (normally this should be 6 for global and 3 for regional, but
# we're not normal)
export NHR_ASSIMILATION=6

# Do we want to use multi-time level analysis
# Currently we use this iff doing an EnKF experiment, so it's set as such here
export MULTI_TIME_LEVEL_ANALYSIS=FALSE
[[ $DA_TYPE == 'enkf' ]] && export MULTI_TIME_LEVEL_ANALYSIS=TRUE
# The following two are only used if MULTI_TIME_LEVEL_ANALYSIS==TRUE
# Number of time levels to use for the analysis
export NUM_TIME_LEVELS=7 # Analysis time, plus 3 additional times before and after
# Period between time levels
export TIME_LEVEL_PERIOD=$(( $CYCLE_FREQUENCY / 6 )) # For hourly cycling, this should probably be less
# These are the files that will be used for the GSI analysis for the EnKF
export ANALYSIS_FILE_PREFIX=gsi_wrfhwrf_d${ANALYSIS_DOMAIN}
# perform satellite data thinning after ensemble mean (TRUE/FALSE)
export SAT_DATA_THINNING=TRUE


# General GSI configuation
export BYTE_ORDER=Big_Endian
export CRTM_ROOT=${GSI_ROOT}/CRTM
export FIX_ROOT=${GSI_ROOT}/fix


#
# Set static/fix files
#
# Need more hacks here to deal with different structures of different versions
if [[ -e ${FIX_ROOT}/nam_glb_berror.f77.gcv ]] ; then
   # older/EMC version
   export BERROR_STATS=${FIX_ROOT}/nam_glb_berror.f77.gcv
else
   # comGSI 3.3 
   export  BERROR_STATS=${FIX_ROOT}/${BYTE_ORDER}/nam_nmmstat_na.gcv
fi
export OBERROR=${FIX_ROOT}/nam_errtable.r3dv
# for Hyperspectral
export SATINFO=${STATIC_DATA_ROOT}/gsi/hwrf_basinscale_satinfo.txt
#export SATINFO=/mnt/lfs1/projects/hfip-hda/bannane/OSSE/test/comGSI_v3.1/comGSI_v3.1/fix/global_satinfo.txt_orig
#export SATINFO=/mnt/lfs1/projects/hfip-hda/bannane/OSSE/run_experiment/analyses/Long/CLR/exprt1/08_01_0100/satinfo

export SCANINFO=${FIX_ROOT}/global_scaninfo.txt

# we tend to change the convinfo, so there are some conditions here
export CONVINFO=${FIX_ROOT}/global_convinfo.txt
# for CYGNSS
if [[ `echo $GSI_DATA_THIS_EXPERIMENT | grep -Ec 'cygnss'` > 0 ]] ; then
  echo "Config :: INFO :: May need to change convinfo for CYGNSS runs" | tee -a $DAFFY_LOG
# export CONVINFO=${STATIC_DATA_ROOT}/gsi/convinfo_cygnss.txt
# export CONVINFO=${STATIC_DATA_ROOT}/gsi/convinfo_cygnss_height.txt
fi

export SATANGL=${FIX_ROOT}/global_satangbias.txt
export OZINFO=${FIX_ROOT}/global_ozinfo.txt
export PCPINFO=${FIX_ROOT}/global_pcpinfo.txt
export RTMFIX=${CRTM_ROOT}
export RTMEMIS=${RTMFIX}/${BYTE_ORDER}/EmisCoeff.bin
export RTMAERO=${RTMFIX}/${BYTE_ORDER}/AerosolCoeff.bin
export RTMCLDS=${RTMFIX}/${BYTE_ORDER}/CloudCoeff.bin
export INITIAL_SATBIAS_INPUT=${FIX_ROOT}/sample.satbias

#
# Override default settings for specific observation types
# TODO : put this in a site-specific script
#

# for OAWL
if [[ `echo $GSI_DATA_THIS_EXPERIMENT | grep -Ec 'oawl|wisscr'` > 0 ]] ; then
   export SCANINFO=${STATIC_DATA_ROOT}/gsi/global_scaninfo.txt
   export CONVINFO=${STATIC_DATA_ROOT}/gsi/global_convinfo.txt
fi

