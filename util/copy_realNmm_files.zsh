#!/usr/bin/env zsh
## 
# Copy the Real files generated by runenkf to an external directory, so they can be used for future
# runs with the --reuse option.
# Then compress them
##

DEST=/home/Javier.Delgado/projects/osse/static/domain_data/OSSEONE/horizontal_interpolation/d53645a8f4e6321fce6adf21a36bcc0d/climapert_ensemble//

rsync -avu ATMOS.2005_08_0* ${DEST}/ --include=\*/ --include=member-\* --include=namelist.input\* --include=wrfinput_d01 --include=wrfbdy_d01 --exclude=\*

cd $DEST
for atmosDir in `ls ` ; do              
   cd $atmosDir
   cd climapert_ensemble
   for memberDir in `ls` ; do
      cd $memberDir
      rmdir $memberDir
      gzip wrfbdy_d01
      gzip wrfinput_d01
      cd .. 
   done
   cd ..
   cd ..
done

