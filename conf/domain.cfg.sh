##
# Domain-related configuration parameters go here. When an experiment is run, 
# the namelist template ( $WRF_NAMELIST_TEMPLATE in model.cfg.sh ) will be
# copied to the running directory of the cycle and then the parameters 
# specified in this file will replace those in the template.
# In order to change other parameters, they must be changed in the template itself.
##

# number of domains/storms
export MAX_DOM=2
export NUM_STORMS=1 # this currently does nothing

# TODO ? : Get from TCvitals
#export REF_LAT=`head -n 1 $TCVITALS_DIR/$START_DATE`
#export REF_LON=`tail -n 1 $TCVITALS_DIR/$START_DATE`

# overwriting these with new values from modified domain (due
# to boundary data issue) 
export REF_LAT=24.8
export REF_LON=-50.0

# Grid size(s)
export E_WE="354, 176,"  
export E_SN="412, 340," # Must be even

# resolution
export DX="0.06, 0.02,"
export DY="0.06, 0.02,"

# number of vertical levels 
export E_VERT=61

# Integration time step (HWRF automatically uses ratio of 3 for nesting)
export TIME_STEP=15

# Interval between GFS data  (For EnKF runs, this should be TIME_INTERVAL (from gsi.cfg.sh) or a multiple of it
#export INTERVAL_SECONDS=$CYCLE_FREQUENCY
export INTERVAL_SECONDS=3600

#
# "Extend" values that are the same for all domains
#
e_vert_tmp=""
for (( i=0 ; i<$MAX_DOM ; i++ )) ; do
   e_vert_tmp="${E_VERT}, $e_vert_tmp"
done
export E_VERT=${e_vert_tmp}

# Number of nests per storm (e.g. 2 for a 9km middle nest and 3km inner nest)
export NESTS_PER_STORM=1

# number of metgrid levels - this will be determined using ncdump on met_nmm files
#export NUM_METGRID_LEVELS=48
#export NUM_METGRID_LEVELS=27

