#!/usr/bin/env zsh
#
##
# "Quick and dirty" script to compare the Jo values for two GSI experiments, for multiple cycles.
# The script iterates through the lines between "Begin Jo table outer loop" and "Jo Global" (i.e.
# lines containing assimilation stats for each ob type/variable) of the first experiemnt (expt1)
# and compares to the values reported in the second experiment (expt2).
# If they are different, it prints out the difference.
# Javier.Delgado@noaa.gov
##

expt1=/home/Javier.Delgado/projects/osse/experiments/hyperspectral/retrievals_moisture_clr_real/run
expt2=/home/Javier.Delgado/projects/osse/experiments/hyperspectral/control/run

start_date=`date --date="08/01/2005 06:00" +%s`
end_date=`date --date="08/09/2005 00:00" +%s`
cycle_frequency=$(( 6 * 3600 )) # seconds
date_env=/home/Javier.Delgado/apps/daffy/1.0.3/scripts/aux_scripts/set_date_env_vars.zsh

for (( t=$start_date ; t<=$end_date ; t+=$cycle_frequency )) ; do
   
   source $date_env $start_date $end_date &> /dev/null

   # for exp1
   firstline=`cat $expt1/GSI_ANALYSIS.$CURRENT_START_DIR_SUFFIX/stdout | /bin/grep -n 'Begin Jo table outer loop' | awk '{print $1}' | tr ':' ' ' | tail -n 1`
   lastline=`cat $expt1/GSI_ANALYSIS.$CURRENT_START_DIR_SUFFIX/stdout | /bin/grep -n 'Jo Global' | awk '{print $1}' | tr ':' ' ' | tail -n 1` # tail to get last iteration only
   cat $expt1/GSI_ANALYSIS.$CURRENT_START_DIR_SUFFIX/stdout | head -n $(( $lastline - 2 )) | tail -n $(( ($lastline - $firstline) - 3 )) > data1
   sed -i "s#surface\ pressure#surface_pressure#" data1 # we'll be using awk to get the first field later, so convert space

   # for exp2
   firstline=`cat $expt2/GSI_ANALYSIS.$CURRENT_START_DIR_SUFFIX/stdout | /bin/grep -n 'Begin Jo table outer loop' | awk '{print $1}' | tr ':' ' ' | tail -n 1`
   lastline=`cat $expt2/GSI_ANALYSIS.$CURRENT_START_DIR_SUFFIX/stdout | /bin/grep -n 'Jo Global' | awk '{print $1}' | tr ':' ' ' | tail -n 1`
   cat $expt2/GSI_ANALYSIS.$CURRENT_START_DIR_SUFFIX/stdout | head -n $(( $lastline - 2 )) | tail -n $(( ($lastline - $firstline) - 3 )) > data2
   sed -i "s#surface\ pressure#surface_pressure#" data2

   while read line ; do
      ob=`echo $line | awk '{print $1}'`
      nobs1=`echo $line | awk '{print $2}'`
      nobs2=`grep $ob data2 | awk '{print $2}'`
      diff=$(( $nobs1 - $nobs2 ))
      if [[ $diff > 0 ]] ; then
         echo "Cycle $CURRENT_START_DIR_SUFFIX, Observation $ob, Difference: $diff"
      fi
   done < data1

done
