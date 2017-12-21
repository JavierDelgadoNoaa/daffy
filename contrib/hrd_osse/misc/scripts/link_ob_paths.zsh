#!/usr/bin/env zsh
##
# Create dicrecotyr names corresponding to OB_TYPES in TARGET_DIR and link all files in 
# those OB_TYPES directories in the new "clone" directories
# Create symlinks of all files in the subdirectories specified in 
# `OB_TYPES` from `OB_DATA_ROOT` to `TARGET_DIR`
#
# Javier.Delgado@noaa.gov
##

set -aeu

OB_DATA_ROOT="/home/Javier.Delgado/projects/osse/static/meso_osse/data/OSSEONE/"
TARGET_DIR=`pwd`/ob_data_links
OB_TYPES="GPSRO SAT_CONTROL RAD_CONTROL SST-ICE"
#PLATFORMS="gpsro.n_t511 prepqc.osse airs281_aqua.n_t511 amsua_aqua amsua_metop amsua_n15 amsua_n18 amsua_n19 amsub_n17.n_t511_ 

[[ -e $TARGET_DIR ]] && echo "WARN :: You should probably delete the TARGET_DIR first" 
mkdir $TARGET_DIR 
orig_dir=`pwd`
for ob_type in `echo $OB_TYPES` ; do
    mkdir $TARGET_DIR/$ob_type
    cd $TARGET_DIR/$ob_type 
    for fil in `ls $OB_DATA_ROOT/$ob_type` ; do
        ln -s $OB_DATA_ROOT/$ob_type/$fil .
    done
    cd $orig_dir
done

