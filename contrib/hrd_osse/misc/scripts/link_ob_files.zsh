#!/usr/bin/env zsh
##
# Create links to files inside all subdirectories specified by "ob_types" residing under
# top level directory "OB_DATA_ROOT".
#
# The algorithm looks for files with names having the date in the format yyyymmddHH as its
# suffix (plus files with _additional_ suffix .bfr and .viir) and creates links 
# for each time interval within "dt" at intervals of "subfrequency".
# 
# Starts looking for files with date "start_date" and ending on "end_date", at frequency
# "interval". All values are in seconds.
#
# IMPORTANT NOTES
#  - Some files have the simulation date timestamp in the file name as well. In this case,
#    for the +/-3 hour dates, the simulation date timestamp on the files will be for
#    the corresponding previous (i.e. -3 hour) timestamp
#    .
# Javier.Delgado@noaa.gov
##
set -aeu

# Path to data
#OB_DATA_ROOT="/home/Javier.Delgado/projects/osse/static/meso_osse/data/OSSEONE/"
OB_DATA_ROOT=`pwd`/ob_data_links
# Ob types to create links for - will create links for all files within 
# subdirectories with these names
ob_types="GPSRO SAT_CONTROL RAD_CONTROL SST-ICE"
#PLATFORMS="gpsro.n_t511 prepqc.osse airs281_aqua.n_t511 amsua_aqua amsua_metop amsua_n15 amsua_n18 amsua_n19 amsub_n17.n_t511_ 

# first date to create links for (i.e. existing files should start here)
start_date=`date --date='8/1/2005 00:00' +%s` 
# last date to create links for
end_date=`date --date='8/5/2005 00:00' +%s` 
# frequency that data files are available at
frequency=$(( 6 * 3600 ))
# difference in time +/- (exclusive) that you want to create links for
dt=$(( 3 * 3600 ))
# frequency within dt to create links at (e.g. every hour)
subfrequency=$(( 1 * 3600 ))

function create_links
{
    ##
    # Create links of files whose names contain the yyyymmddHH corresponding to
    # `nearest_time` pointing to a file, with the same prefix as the existing file,
    # but with the suffix corresponding to the yyyymmddHH suffix.
    # Additional suffix of .bfr or .viir will be recognized
    ##
    local nearest_time=$1 # seconds since epoch
    local curr_time=$2 # seconds since epoch
    
    zmodload zsh/datetime
    yyyy=`strftime "%Y" $curr_time`
    mm=`strftime "%m" $curr_time`
    dd=`strftime "%d" $curr_time`
    HH=`strftime "%H" $curr_time`
    MM=`strftime "%M" $curr_time`
    curr_yyyymmddHH=$yyyy$mm$dd$HH # ASSUME : all ob files have this patten in the prefix

    n_yyyy=`strftime "%Y" $nearest_time`
    n_mm=`strftime "%m" $nearest_time`
    n_dd=`strftime "%d" $nearest_time`
    n_HH=`strftime "%H" $nearest_time`
    n_MM=`strftime "%M" $nearest_time`
    nearest_yyyymmddHH=$n_yyyy$n_mm$n_dd$n_HH # ASSUME : all ob files have this patten in the prefix
	
    orig_dir=`pwd`
    for ob_type in `echo $ob_types` ; do
        cd $OB_DATA_ROOT/$ob_type 
        for fil in `ls $OB_DATA_ROOT/$ob_type | grep -E "$nearest_yyyymmddHH\$|$nearest_yyyymmddHH.bfr\$|$nearest_yyyymmddHH.viir\$"` ; do
            file_prefix_end_idx=$(( ${fil[(i)$nearest_yyyymmddHH]} - 1 ))
            link_prefix=$fil[1,$file_prefix_end_idx]
            # since we do not know if it ends with just the date or if there
            # is an additional suffix (e.g. .bfr)
            idx=$(( $file_prefix_end_idx + 1 + 10))
            link_suffix=$fil[$idx,-1]
            #ln -sf $fil ${link_prefix}${curr_yyyymmddHH}${link_suffix}
            ln -s $fil ${link_prefix}${curr_yyyymmddHH}${link_suffix}
        done
        cd $orig_dir
    done
}

function concatenate_files
{
    ##
    # Concatenate files containing the timestamp (in yyyymmddHH) corresponding to 
    # `previous_cycle` and `next_cycle` onto a file with the timestamp (in yyyymmddHH)
    # corresponding to `current_time`.
    # This will apply to all files inside $OB_DATA_ROOT/$ob_type (for all $ob_types). 
    # The prefix will be whatever is the prefix for the matching files with the 
    # `previuos_cycle` date as its filename.
    ##
    local current_time=$1 # seconds since epoch
    local previous_cycle=$2 # seconds since epoch
    local next_cycle=$3 # seconds since epoch
    zmodload zsh/datetime

    curr_yyyymmddHH=`strftime "%Y%m%d%H" $current_time`

    yyyy=`strftime "%Y" $previous_cycle`
    mm=`strftime "%m" $previous_cycle`
    dd=`strftime "%d" $previous_cycle`
    HH=`strftime "%H" $previous_cycle`
    MM=`strftime "%M" $previous_cycle`
    previous_yyyymmddHH=$yyyy$mm$dd$HH # ASSUME : all ob files have this patten in the prefix

    n_yyyy=`strftime "%Y" $next_cycle`
    n_mm=`strftime "%m" $next_cycle`
    n_dd=`strftime "%d" $next_cycle`
    n_HH=`strftime "%H" $next_cycle`
    n_MM=`strftime "%M" $next_cycle`
    next_yyyymmddHH=$n_yyyy$n_mm$n_dd$n_HH # ASSUME : all ob files have this patten in the prefix

    orig_dir=`pwd`
    for ob_type in `echo $ob_types` ; do
        cd $OB_DATA_ROOT/$ob_type 
        for fil in `ls $OB_DATA_ROOT/$ob_type | grep -E "$previous_yyyymmddHH\$|$previous_yyyymmddHH.bfr\$|$previous_yyyymmddHH.viir\$"` ; do
            file_prefix_end_idx=$(( ${fil[(i)$previous_yyyymmddHH]} - 1 ))
            link_prefix=$fil[1,$file_prefix_end_idx]
            # since we do not know if it ends with just the date or if there
            # is an additional suffix (e.g. .bfr)
            idx=$(( $file_prefix_end_idx + 1 + 10))
            link_suffix=$fil[$idx,-1]
            dest_file=${link_prefix}${curr_yyyymmddHH}${link_suffix}
            cat ${link_prefix}${previous_yyyymmddHH}${link_suffix} > $dest_file
        done
        
        # gotta do separately for the later synoptic time since part of the 
        # prefixes (i.e. the creation date part) will be diffeent 
        for fil in `ls $OB_DATA_ROOT/$ob_type | grep -E "$next_yyyymmddHH\$|$next_yyyymmddHH.bfr\$|$next_yyyymmddHH.viir\$"` ; do
            file_prefix_end_idx=$(( ${fil[(i)$next_yyyymmddHH]} - 1 ))
            link_prefix=$fil[1,$file_prefix_end_idx]
            idx=$(( $file_prefix_end_idx + 1 + 10))
            link_suffix=$fil[$idx,-1]
            cat ${link_prefix}${next_yyyymmddHH}${link_suffix} >> $dest_file
        done
        cd $orig_dir
    done
}

#############
# MAIN
# #############
for (( d=$start_date ; d<=$end_date ; d+=$frequency )) ; do

    # for  t > t-3 
    for (( dtime=$(( 0 - $dt )) ; dtime<0 ; dtime+=$subfrequency )) ; do
        [[ $dtime == $(( 0 - $dt )) ]] && continue # skip t-3
        curr_time=$(( $d + $dtime ))
        create_links $d $curr_time
    done
    
    # for t == 3
    concatenate_files $(( $d + $dt )) $d $(( $d + $frequency ))

    # for  t < t+3
    for (( dtime=$subfrequency ; dtime<$dt ; dtime+=$subfrequency)) ; do
        curr_time=$(( $d + $dtime ))
        create_links $d $curr_time
    done

done

