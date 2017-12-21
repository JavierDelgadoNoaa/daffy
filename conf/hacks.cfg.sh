##
# This file contains toggles for hacks in the framework. Some of these
# should be set to FALSE, but under certain circumstances (e.g. you have a
# deadline and need the workflow to proceed despite less-than-optimal 
# conditions) they can help you get your results.
# Others are just here to deal with system-related quirks
##

# On Jet, it seems that you are pinned to a particular CPU when you log in, and
# all non-MPI processes invoked share that CPU. To work around this, I have
# code in certain functions that uses taskset to manually reassign CPUs processes.
# Setting this to TRUE should not have a negative effect even if not on Jet, but
# may result in extra warnings/output.
# Note: I'm assuming the same thing occurs on Theia
if [[ $SUPERCOMPUTER == 'JET'  || $SUPERCOMPUTER == 'THEIA' ]] ; then
   export JET_CPU_PIN_TRICK=TRUE
else
   export JET_CPU_PIN_TRICK=FALSE
fi

#force i/j parent start
# note that i_parent_start and j_parent_start must be greater than shw, which defaults to
# 2 in the current Registry, so we need to force it to at least 3
export FORCE_SWCORNER_POSITION_HACK=TRUE

# If you want to use a nest for the forecasts, but no nest for the guesses,
# set this to true.
# This is just a temporary until I modify the framework to allow different
# settings for forecasts and guesses
# (NOTE: max_dom should be set to the number of domains you want for the _forecast_)
export NO_NEST_GUESS=TRUE

# Lustre file system has a problem with sqlite, so we can't invoke Rocoto if the 
# database is in a Lustre file system. If this is set to TRUE, the database will
# be moved to a temporary location on another file system when invoking Rocoto
export LUSTRE_ROCOTO_HACK='FALSE'
[[ $SUPERCOMPUTER == "S4" ]] && LUSTRE_ROCOTO_HACK='TRUE'
export ROCOTO_STATE_FILE_TEMP_LOCATION='/home/jdelgado/.workflow_state_files'

# Timing-related shell scripts may have issues due to the way some systems (e.g. Pegasus2) deal with daylight savings time (DST).
# Setting this to true will use the is_dst utility to determine if the time should be modified to deal with
# this. Setting this to True even on systems that do not have this problem should be fine.
export DST_HACK='TRUE'
