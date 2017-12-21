#!/usr/bin/env zsh
##
# Run tcvitals.sh on all cycles and output figure and text file to each cycle's respective
# PRODUCTS.<cycle_date> directory
#
# INSTRUCTIONS
# - This should be run from within the tcvitals distribution
# - Set basedir, expName, and postproc_topdir and run the script
##

# run top dir
basedir=/home/Javier.Delgado/projects/osse/experiments/enkf/hyperspectral/hs_rads_d1_120km/run
#basedir=/home/Javier.Delgado/projects/osse/experiments/0801_control_v2/exec/../run/
# experiment name
expName=hs_rads_d1_120km
#expName=control_v2_with_err
# This is the prefix of the directory under which Diapost subdirectories reside
#postproc_topdir=ATMOS
postproc_topdir=POSTPROC
#postproc_topdir=ATMOS
# Fix new Diapost files to address fhr issue?
FIX_TRACK_FILE=TRUE

[[ ! -e tcvitals.sh ]] && echo "This should be run from the tcvitals distribution directory" && exit 1

module load grads
which grads &> /dev/null ; [[ $? != 0 ]] && echo "Could not find grads. Try 'module load grads'" && exit 1

for expDir in `ls $basedir | grep $postproc_topdir` ; do
    echo $basedir/$expDir/Diapost ;
     [[  ! -e $basedir/$expDir/Diapost ]] && continue
     cp $basedir/$postproc_topdir.$expDir[-16,-1]/Diapost/fcst_track.txt .
     if [[ $FIX_TRACK_FILE == TRUE ]] ; then
        awk 'BEGIN{hour=0}{print $1,hour,0,$4,$5,$6,$7,$8;hour=hour+6}' fcst_track.txt > tmp
        mv tmp fcst_track.txt
     fi
     ./tcvitals.sh ${expName}_
      convert ${expName}_tcStats.png -rotate 270 ${expName}_tcStats.png 
      destDir=$basedir/PRODUCTS.$expDir[-16,-1]/tc_stats
      mkdir -p $destDir
      cp      ${expName}_tcStats.png $destDir/tc_stats.png 
      cp error.txt $destDir/error.txt  
done
