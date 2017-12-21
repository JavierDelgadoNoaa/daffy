# gotta disable since they have dirty code there
set +aeu
source /etc/profile.d/modules.sh
if [[ $STRICT_MODE == 'TRUE' ]] ; then
    set -aeu 
fi

if [[ $SUPERCOMPUTER == 'JET' ]] ; then
   source /etc/profile.d/torque.sh
   source /etc/profile.d/moab.sh
fi

if [[ $SUPERCOMPUTER == 'THEIA' ]] ; then
   source /etc/profile.d/gold_moab_torque.sh
fi

# 
# Load modules
#
if [[ $SUPERCOMPUTER == 'JET' ]] ; then
   module load intel
   module load netcdf
   module load mvapich2
   module load hsms
   module load ncview
   module load grads
   module load imagemagick
   module load nco
   module load wgrib
elif [[ $SUPERCOMPUTER == 'THEIA' ]] ; then
   module load intel/15.1.133
   # TODO : Generalize or just decide on one to keep
   # UPDATE: Just stick to impi unless we are testing
   # mvapich
   #if [[ $MODEL_CONFIG_ID == '2014i' ]] ; then
	  module load impi #/4.1.3.048 
   #else
   #   module load mvapich2
   #fi
   module load netcdf/3.6.3   
   module load pnetcdf
   module load ncview
   module load grads
   module load imagemagick
   module load nco
   module load wgrib
   module load hpss
elif [[ $SUPERCOMPUTER == 'S4' ]] ; then
   # Note: bundle/basic-1 will load impi, so we purge first to reduce unimportant warnings
   #       we also unload impi before loading intel to prevent the "reloading impi" message
   #       from displaying
   module purge
   module load bundle/basic-1
   module load jobvars
   module load license_intel
   module unload impi
   module load intel/12.1
   module load netcdf3
   module load impi/4.0.3.008
   module load ruby/1.8.7
   module load udunits2
   # needed for grads and/or nco ; grads provides wgrib
   module load geotiff netcdf4 hdf hdf5 szip udunits udunits2
   module load nco
   module load grads
   export NETCDF=$SSEC_NETCDF3_DIR
elif [[ $SUPERCOMPUTER == 'PEGASUS' ]] ; then
   module load impi
   module load share-rpms
   module load imagemagick 
   module load nco 
   module load wgrib
   module load netcdf-gcc 
   module load grads
else
   echo "Configuration ERROR :: Unknown \$SUPERCOMPUTER!" | tee -a $DAFFY_LOG
   exit 1
fi

# 
# Set environment variables
#
# For python. For GFDL tracker to work, you'll need Python with PyGrib installed
export PYTHONPATH=${EXT_ROOT}/local/lib/python2.7/site-packages:${EXT_ROOT}/scripts/py:${TOP_DIR}/lib:${TOP_DIR}/extern/py/lib:${TOP_DIR}
export PATH=$APPS_ROOT/canopy_sys/Canopy_64bit/User/bin:$PATH

if [[ $SUPERCOMPUTER == 'JET' ]] ; then
   export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/apps/intel/12.1/composer_xe_2011_sp1.10.319/compiler/lib/intel64/
	fpath=(/apps/intel/12.1/composer_xe_2011_sp1.10.319/mkl/includelp64 /usr/share/zsh/site-functions /usr/share/zsh/4.3.10/functions)
   #export FFTW_PATH=/pan2/projects/gfsenkf/whitaker/lib
   export FFTW_PATH=/home/Javier.Delgado/local/lib64
   export NCDUMP=ncdump
   export WGRIB_BIN=`which wgrib`
   export GRIB2CTL=$APPS_ROOT/util/grib2ctl
   export GRIBMAP=$APPS_ROOT/util/gribmap
elif [[ $SUPERCOMPUTER == 'THEIA' ]] ; then
   export FFTW_PATH=/home/Javier.Delgado/local/lib_from_jet
   export NCDUMP=ncdump
   export WGRIB_BIN=`which wgrib`
   export GRIB2CTL=$APPS_ROOT/util/grib2ctl
   export GRIBMAP=$APPS_ROOT/util/gribmap
elif [[ $SUPERCOMPUTER == 'S4' ]] ; then
   export FFTW_PATH=${APPS_ROOT}/misc/libs
   export MPD_CON_EXT="sge_$JOB_ID.$SGE_TASK_ID"
   export NCDUMP=/opt/netcdf3/3.6.3-intel-12.1/bin/ncdump
   export WGRIB_BIN=$SSEC_GRADS_BIN/wgrib
   export GRIB2CTL=$APPS_ROOT/util/grib2ctl
   export GRIBMAP=$APPS_ROOT/util/gribmap
elif [[ $SUPERCOMPUTER == 'PEGASUS' ]] ; then
   export FFTW_PATH=/nethome/jdelgado/apps/util_gsi/from_jeff_on_jet/misc/
   export NCDUMP=ncdump
   export GRIBMAP=$NCARG_ROOT/bin/gribmap
   export GRIB2CTL="/share/opt/perl/5.16.3/bin/perl -w $APPS_ROOT/misc/grib2ctl"
fi


