<?php

     #
     # GLOBALS
     #
     $TESTING_MODE = False ;

    #
    # Define functions
    #
    function xml_attribute($object, $attribute)
    {
       if(isset($object[$attribute]))
          return (string) $object[$attribute];
    }

    function get_list_of_obs($xml) {
       /**
        * Get a list/array of obs assimilated for an experiment node ($xml)
        * <observations_configuration name="control_v1">
        */
       $list_of_obs = "" ;
       #$matching_experiment_element->data_assimilation->observations->observations_configuration
       foreach ( $xml->children() as $child) {
          if ( $child->getName() == 'data_assimilation' ) {
             foreach ( $child->children() as $obsNode ) {
                if ( $obsNode->getName() == 'observations' ) {
                   foreach ( $obsNode->children() as $obConfigNode ) {
                      if ( $obConfigNode->getName() == "observations_configuration" ) {
                         $obConfigName = xml_attribute($obConfigNode, "name") ;
                         $list_of_obs = "$list_of_obs $obConfigName," ;
                      }
                   }
                }
             }
          }
       }
       return substr($list_of_obs, 0, -1) ; // remove trailing ','
    }

    function get_deterministic_fcst_bc($xml) {
       /**
        * Get the value for for the deterministic_forecast_gfs_data_id
        * for the given expeirment node ($xml)
        */
       foreach ( $xml->children() as $child) {
           if ( $child->getName() == 'model' ) {
              #echo $child ;
              return $child->deterministic_forecast_gfs_data_id ;
           }
       }
       return "unknown" ;
       //throw new Exception('Missing element in XML') ;
   }



   #
   # Read in selected parameters
   #
    if ( $_GET["experiment_type"]) {
      $experiment_type = $_GET["experiment_type"] ;
    }
    // TODO : Get multiple experiment_type

    if ( $_GET["spinup_date"]) {
      $spinup_date = $_GET["spinup_date"] ;
    }
    if ( $_GET["end_date"]) {
      $end_date = $_GET["end_date"] ;
    }
    if ( $_GET["observations"]) {
      $observations = $_GET["observations"] ;
    }
    // TODO : GET Multiple obs
    if ( $_GET["det_fcst_bc"]) {
      $det_fcst_bc = $_GET["det_fcst_bc"] ;
    }
    if ( $_GET["ens_fcst_bc"]) {
      $ens_fcst_bc = $_GET["ens_fcst_bc"] ;
    }

    // sanity checks
    // TODO : terminate if something fails
    //echo $spinup_date ;
    if ( preg_match("/20[0-9][0-9][0-9][0-9][0-3][0-9][0-2][0-9][0-5][0-9]/", $spinup_date) == 0 ) {
      echo "Invalid date" ;
    }

   #test
   //$horz_loc_nh_wanted = 1200 ;
   //$adaptive_posterior_inflation_nh_min = 0.7 ;
   //$adaptive_posterior_inflation_nh_max = 0.99 ;
   
   
   $xml = simplexml_load_file('experiments.xml') ;
 
   #
   # Build the xpath string
   #
   $xpath_string = "/daffy_experiments/experiment" ;
      // choose experiment type
      $xpath_string = $xpath_string . "[" ;
      foreach ( $experiment_type as $exptType ) {
         $xpath_string = $xpath_string . "@da_type='$exptType' or " ;
      }
      $xpath_string = substr($xpath_string, 0, -3) . " ]" ; // remove trailing 'or'
      // Build timing-related parts of the query

      $xpath_string = $xpath_string . "
         [spinup_date=$spinup_date]
         [end_date=$end_date]" ;

      // Build DA part of the query
      $xpath_string = $xpath_string . "/data_assimilation" ;

         // Build EnKF part of the DA-related settings
         $xpath_string = "$xpath_string" . "/enkf_configuration" ;
         if ( isset($horz_loc_nh_wanted) ) { 
            $xpath_string = "$xpath_string" . "[horizontal_localization_nh=$horz_loc_nh_wanted]" ; 
         }
         if ( isset($adaptive_posterior_inflation_nh_min) ) {
            $xpath_string = "$xpath_string" . "[adaptive_posterior_inflation_nh>=$adaptive_posterior_inflation_nh_min]" ;
         }
         if ( isset($adaptive_posterior_inflation_nh) ) {
            $xpath_string = "$xpath_string" . "[adaptive_posterior_inflation_nh<=$adaptive_posterior_inflation_nh_max]" ;
         }
  
  $matches = $xml->xpath( "$xpath_string/parent::*/parent::*") ;
  
//and[adaptive_posterior_inflation_nh=0.44]") ;
   if (!$matches || count($matches) == 0 ) {
      echo "No matches!" ;
      exit() ;
   }
   #echo count($matches) ;
   #print_r($matches) ;
   //foreach( $matches as $matching_experiment_element)

   if ( $TESTING_MODE) {
      echo "<html><head><title>test</title></head>" ;
      echo '<link rel="stylesheet" type="text/css" href="_styles.css" media="screen">' ;
      echo "</head><body>" ;
   } # end testing mode
   
   echo "<ol>" ;
   while(list( , $matching_experiment_element) = each($matches)) {
      //print $matching_experiment_element->daffy_revision ;
      $uuid = xml_attribute($matching_experiment_element, "uuid") ;
      $list_of_obs = get_list_of_obs($matching_experiment_element) ;
      $cycle_frequency_hrs = $matching_experiment_element->cycle_frequency / 3600 ;
      $deterministic_fcst_bc =  get_deterministic_fcst_bc($matching_experiment_element) ;
      $ensemble_forecast_bc = "foo" ; // get_ensemble_fcst_bc($matching_experiment_element) ;
      echo "
      <li class='exptEntry'>
        <label for='matchingExpt$uuid' class='experimentEntryText'>$uuid</label>
        <input type='checkbox' id='matchingExpt$uuid' />
        <ol>
           <li>Spinup Date: $matching_experiment_element->spinup_date</li>
           <li>End Date: $matching_experiment_element->end_date</li>
           <li>Obs Assimilated: $list_of_obs </li>
           <li>Cycle Frequency: $cycle_frequency_hrs (hours) </li>
           <li>DAFFY Revision: $matching_experiment_element->daffy_revision </li>
           <li>Deterministic Forecast BC: $deterministic_fcst_bc </li>
           <li>Ensemble Forecast BC: $ensemble_forecast_bc </li>
        </ol>
      " ;
      
       // epoch time: date('U') ;

      //echo "<span class=experimentEntryText>$matching_experiment_element->spinup_date</span>" ;
      echo "</li>" ;
      //echo $matching_experiment_element->asXML() ;
   }
   echo "</ol>" ;
   if ( $TESTING_MODE ) {
      echo "</body></html>" ;
   } # end testing
?>
