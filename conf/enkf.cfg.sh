# Path settings
export ENKF_ROOT=${APPS_ROOT}/hybrid_enkf_system/enkf/snapshots/201402/osse
export ENKF_EXE=${ENKF_ROOT}/src/global_enkf_wrf
export ENSEMBLE_MEAN_EXE=${APPS_ROOT}/hybrid_enkf_system/ensemble-mean/ENSEMBLE_MEAN.exe

# Templates 
export ENKF_NAMELIST_TEMPLATE=${TEMPLATES_DIR}/enkf.nml
export ADDITIVE_INFLATION_TEMPLATE=${TEMPLATES_DIR}/namelist.additive-inflation
export ENKF_ENSMEAN_NAMELIST_TEMPLATE=${TEMPLATES_DIR}/ensemble_mean_for_enkf.nl

#
# EnKF settings
#
# Adaptive posterior inflation...
#0 for no inflatoin, 1 to inflate posterior stdev to that of the prior
export ADAPTIVE_POSTERIOR_INFLATION_TROPICS='0.9' 
export ADAPTIVE_POSTERIOR_INFLATION_NORTHERN_HEMISPHERE='0.9'
export ADAPTIVE_POSTERIOR_INFLATION_SOUTHERN_HEMISPHERE='0.9'
# Vertical localization length (in ln(p) ) for tropics, NH, and SH ...
# ... for All obs except satellite and ps
export VERTICAL_LOCALIZATION_TROPICS_CONVOBS=1.0 # LN(P)
export VERTICAL_LOCALIZATION_SOUTHERN_HEMISPHERE_CONVOBS=1.0 # LN(P)
export VERTICAL_LOCALIZATION_NORTHERN_HEMISPHERE_CONVOBS=1.0 # LN(P)
# ... for sat obs
export VERTICAL_LOCALIZATION_TROPICS_SATOBS=1.0 # LN(P)
export VERTICAL_LOCALIZATION_SOUTHERN_HEMISPHERE_SATOBS=1.0 # LN(P)
export VERTICAL_LOCALIZATION_NORTHERN_HEMISPHERE_SATOBS=1.0 # LN(P)
# ... for ps obs
export VERTICAL_LOCALIZATION_TROPICS_PSOBS=1.0 # LN(P)
export VERTICAL_LOCALIZATION_SOUTHERN_HEMISPHERE_PSOBS=1.0 # LN(P)
export VERTICAL_LOCALIZATION_NORTHERN_HEMISPHERE_PSOBS=1.0 # LN(P)

# Horizontal localization (in km)
export HORIZONTAL_LOCALIZATION_TROPICS=130 # km
export HORIZONTAL_LOCALIZATION_SOUTHERN_HEMISPHERE=130 # km
export HORIZONTAL_LOCALIZATION_NORTHERN_HEMISPHERE=130 # km

# Observation time localization
export OBSERVATION_TIME_LOCALIZATION='1.e30'

# Inflation
export MIN_INFLATION='1.0'
export MAX_INFLATION='100.0'
# 1 means "inflate all the way back to prior spread"
export INFLATION_SMOOTHING_PARAMETER='-1' # -1 for NO smoothing

# If [Posterior_variance / Prior_variance] reduces variance by less than [this value], skip ob) (PaOverPb in code)
export POSTERIOR_PRIOR_THRESHOLD='1' 

# number of times to iterate satellite bias correction 
export ENKF_SATBIAS_ITERATIONS=6

# Use SR filter ('deterministic' in namelist)
export USE_ENSRF='TRUE'
