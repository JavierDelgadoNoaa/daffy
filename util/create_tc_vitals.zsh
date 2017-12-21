# just pasting what I previously put in the GSI script...
# Create TCVitals file if desired
if [[ $ASSIM_TCVITALS == TRUE ]] ; then
   # TODO : handle 3+ domains
   #TC_FILE_SUFFIX=${CURRENT_START_YMDHM}
   #tc_file=${TCVITALS_DIR}/${TC_FILE_PREFIX}${TC_FILE_SUFFIX}
   #[[ ! -e $tc_file ]] && echo ":( TC File '$tc_file' does not exist " && exit 2
   #[[ `cat $tc_file | wc -l` != 2 ]] && echo "Unrecognized TCVitals file format" && exit 2
   # get lat/lon
   #latLine=`head -n 1 $tc_file`
   #lonLine=`tail -n 1 $tc_file`
   # since the TCV card should have the lat*10 and lon*10 values, we
   # want at most one decimal
   #latLine=`printf "%.1f" $latLine`
   #lonLine=`printf "%.1f" $lonLine`
   # first, trim negative sign, decimal, and excess digits
   #lat=`echo $latLine | sed "s#\.##" | sed s#-## | cut -c 1-3`
   #lon=`echo $lonLine | sed "s#\.##" | sed s#-## | cut -c 1-4`
   # now add w/e and n/s suffix
   #if [[ $latLine[1] == "-" ]] ; then
   #   lat="${lat}S"
   #else
   #   lat="${lat}N"
   #fi
   #if [[ $lonLine[1] == "-" ]] ; then 
   #   lon="${lon}W"
   #else
   #   lon="${lon}E"
   #fi

   #abcd abc abcdefgh NNnnnnnn NNNN NNNa NNNNa NNN NNN ( NNNN NNNN NNNN) NN NNN (NNNN NNNN NNNN) a
   # create file   
   #printf "%4s %3s %9s %8i %4s %4s %5s %3i %3i %4i %4i %4i %2i %3i %4i %4i %4i %4i %1s\n" \
   #         AOML 01L ONEARW01L ${CURRENT_START_YMD} ${CURRENT_START_HOUR}00 $lat $lon -99 -99 -999 -999 -999 -9 -99 -999 -999 -999 -999 X \
   #  > tcvitl
