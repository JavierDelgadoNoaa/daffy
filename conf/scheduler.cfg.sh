if [[ $SUPERCOMPUTER == 'JET' ]] ; then
   export ACCOUNT='hur-aoml'
   export BATCH_SYSTEM_PARTITION='-l partition=tjet:ujet:vjet' # this will be "native" in Rocoto
   export BATCH_SYSTEM_NAME='moabtorque'
   export DEFAULT_QUEUE='batch'
   export ROCOTO_DB_PATH=$RUN_TOP_DIR/rocotodb.sql
elif [[ $SUPERCOMPUTER == 'THEIA' ]] ; then
   export ACCOUNT='aoml-osse'
   export BATCH_SYSTEM_PARTITION=''
   export BATCH_SYSTEM_NAME='moabtorque'
   export DEFAULT_QUEUE='batch'
   export ROCOTO_DB_PATH=$RUN_TOP_DIR/rocotodb.sql
elif [[ $SUPERCOMPUTER == 'PEGASUS' ]] ; then
   export ACCOUNT='dummy' # need to have something or Rocoto will pass -P with no value
   export BATCH_SYSTEM_PARTITION=''
   export BATCH_SYSTEM_NAME='lsf'
   export DEFAULT_QUEUE=general
   export ROCOTO_DB_PATH=$RUN_TOP_DIR/rocotodb.sql
elif [[ $SUPERCOMPUTER == 'S4' ]] ; then
   export ACCOUNT='dummy'
   #export BATCH_SYSTEM_PARTITION='-V'
   export BATCH_SYSTEM_PARTITION='-V  -l excl=false' # disable exclusivity since nodes are 48 cores
   export BATCH_SYSTEM_NAME='sge'
   # There is no queue in s4, but due to a technicality in SGE, we need to pass the processing environment
   # to the <queue> so that Rocoto passes it as the processing environment
   export DEFAULT_QUEUE='mpi2_mpd'
   # Can't use SQLite in Lustre file system
   export ROCOTO_DB_PATH=$HOME/rocotodb_${EXPERIMENT_ID}.sql
else
   echo "Configuration ERROR :: Unknown/Unset \$SUPERCOMPUTER"  | tee -a $DAFFY_LOG
   exit 1
fi
