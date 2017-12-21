#
##
# This is used for the creation of comparison plots. It must be sourced prior to running
# the tile*.zsh scripts.
# Note that this script contains logic for setting the variables of three experiments, but
# it will also work with two experiments, as the tiling script can just ignore the EXPT3* settings.
# By default, EXPT1 will be the Nature RUn, EXPT2 will be the control (enkf for EnKF experiments an
# GSI for GSI experiments)., and EXPT3 will be the experiment.
##

# Last forecast hour to process. Value is in hours
LAST_FHR=__LAST_FHR__ #120 or $(( $FORECAST_DURATION / 3600 ))
# Interval between outputs, in hours
FHR_INCREMENT=__FHR_INCREMENT__ # 6 or $UPP_FCST_INTERVAL
# How to align the figures being tiled
APPEND="+append" # use "-append" to align vertically and "+append" to align side-by-side
# Name to prefix output files with
OUTPUT_PREFIX=__OUTPUT_PREFIX__ # "comparo_vs_nature_and_control"
# Titles to put on generated images. This should use ZSH array syntax ( E.G. ( 'foo' 'bar' baz' ) )
# Also, no spaces or ImageMagick complains
#TITLES=__TITLES__ # ( 'Nature'  'Control' 'Experiment' ) # no spaces or IM complains
#NUM_IMG=$#TITLES
# Path to PDFTK executable, which will be used to combine generated PDF images into a single file
# This is set in DAFFY
#PDFTK=pdftk

# General rendering options
STROKE=black
FILL=blue # font will be this color
POINTSIZE=80
FONT=Utopia-Bold # use 'identify -list type' to see what's available
IMG_WIDTH=1200
IMG_HEIGHT=1600
IMG_EXTENSION=png
OUTPUT_IMG_EXTENSION=pdf


START_FHR=0

# IF running outside of DAFFY, certain variables will need to be set
#    RUN_TOP_DIR ( e.g. EXPERIMENTS/enkf/${EXPERIMENT1_TYPE}/${EXPERIMENT1_subtype})
#    CURRENT_START_...
#    CONV_CONTROL_DATA_DIR

# Configuration for DAFFY
MAPS_SUBDIR=PRODUCTS.$CURRENT_START_DIR_SUFFIX/8_panel_maps
#MAPS_SUBDIR=PRODUCTS.${YEAR}_${MONTH}_${DAY}_${HOUR}_${MINUTE}/8_panel_maps

# NOTE: The config script will automatically set the Control directory according to the experiment 
# type (GSI/EnKF) and start date
CONTROL_OUTPUT_DIR=$CONV_CONTROL_DATA_DIR/$MAPS_SUBDIR
   
# nature
EXPT1_DIR=${RUN_TOP_DIR}/$MAPS_SUBDIR/d${DOMAIN_NUMBER}/maps/NatureRun
# control
EXPT2_DIR=${CONV_CONTROL_DATA_DIR}/$MAPS_SUBDIR/d${DOMAIN_NUMBER}/maps
# experiment
EXPT3_DIR=$RUN_TOP_DIR/$MAPS_SUBDIR/d${DOMAIN_NUMBER}/maps 

EXPT1_FILE_PREFIX='fhr'
EXPT2_FILE_PREFIX='fhr'
EXPT3_FILE_PREFIX='fhr'

EXPT1_FILE_SUFFIX=.${IMG_EXTENSION}
#EXPT2_FILE_SUFFIX=_${EXPERIMENT2_ID}_D${DOMAIN_NUMBER}.${IMG_EXTENSION}
EXPT2_FILE_SUFFIX=.${IMG_EXTENSION}
#EXPT3_FILE_SUFFIX=_${EXPERIMENT3_ID}_D${DOMAIN_NUMBER}.${IMG_EXTENSION}
EXPT3_FILE_SUFFIX=.${IMG_EXTENSION}
