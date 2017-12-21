<html>
 <head>
   <style type="text/css">
   .exptForm {
      width: 30% ;
      /*background: #504 ;*/
   }
   select {
      float: left ;
      width: 200px ;
      padding: 4px 2px ;
      margin: 0 0 20px 10px;
   }
   label {
      display: block ;
      text-align: right ;
      margin-left : 1em ;
      float: left ;
      width: 200px ;
   }
   button {
      clear: both ;
      margin-left:230px ;
      width: 200px ;
      height: 25px ;
   }  
   </style>
  <title>OSSE Portal</title>
 </head>

<body>

<h1>OSSE Portal</h1>


<p>Select Desired Experiment Configuration</p>
<div class="exptForm">
<form method="get">
<?php
   
   $EXPERIMENT_DATA_BASEDIR  = '/data/www/Javier.Delgado/experiments' ;
   
function add_option_tag_for_each_subdir($dir, $selected_option) {
   /*
    * Read directory <$dir> and create an <option> tag for each directory entry.
    * The entries will be sorted using the default behavior of the sort() function.
    * If one of the files in the directory matches <$selected_option>, mark it
    * as selected (i.e. <option selected>)
    * Skip the special directories "." and ".." 
    * Also, skip any entries that start with "_"
    */
   #experiments = scandir($experiment_type_dir) ;
   $dir_contents = array() ;
   if ( is_dir($dir) ) {
      if ( $dh = opendir($dir) ) {
         while (( $dir_entry = readdir($dh) ) !== false ) {
            if ( substr( $dir_entry, 0, 1) == "_") continue ;
            if ( $dir_entry == "." ) continue ;
            if ( $dir_entry == ".." ) continue ;
            array_push( $dir_contents, $dir_entry ) ;
         }
      }
   }
   $sorted = sort($dir_contents) ;
   for( $i=0 ; $i<count($dir_contents) ; $i++ ) {
      $dir_entry = $dir_contents[$i] ;
      if ( $selected_option == $dir_entry) 
         { printf("<option selected> %s </option> \n", $dir_entry)  ; }
      else 
         { printf("<option> %s </option> \n", $dir_entry) ; }
         
      
   }
}

function echo_form_label($str) {
   echo "<label class='formLabel'>" . $str . "</label>" ;
}
   
   # 
   # Select experiment type
   #
   echo_form_label("Experiment Type") ;
   echo "<select name='experiment_type' onChange='this.form.submit()'> \n" ;
   
   # See if experiment type has been chosen
   if ( $_GET["experiment_type"] ) {
      $selected_experiment_type = $_GET["experiment_type"] ;
   }
   # Scan directory. Each subdirectory corresponds to an experiment type
   # Add option to dropdown list for each
   if ( is_dir($EXPERIMENT_DATA_BASEDIR) ) {
      add_option_tag_for_each_subdir($EXPERIMENT_DATA_BASEDIR, $selected_experiment_type) ;
      echo "</select> \n" ;
      echo "<br /> \n" ;
   }

   
   #
   # Select experiment name/id
   #
   if ( $_GET["experiment_name"]) {
      $selected_experiment = $_GET["experiment_name"] ;
   }
   
   // TODO: onChange: invalidate other forms; unset all other _get variables and restart
   if ( $selected_experiment_type ) {
      echo_form_label("Experiment ID") ;
      echo "<select name='experiment_name' onChange='this.form.submit()'> \n" ;
      $experiment_type_dir = $EXPERIMENT_DATA_BASEDIR . '/' . $selected_experiment_type ;
      add_option_tag_for_each_subdir($experiment_type_dir, $selected_experiment) ;
      echo "</select> \n" ;
      echo "<br /> \n" ;
   }

   # 
   # Get subexperiment (which usually corresponds to the modality used for DA and/or DA configuration
   if ( $_GET["subexperiment_name"]) {
      $selected_subexperiment = $_GET["subexperiment_name"] ;
   }
   if (  $selected_experiment) { 
      echo_form_label("SubExperiment ID") ;
      echo "<select name='subexperiment_name' onChange='this.form.submit()'> \n" ;
      $experiment_dir = $experiment_type_dir . "/" . $selected_experiment ;
      add_option_tag_for_each_subdir($experiment_dir, $selected_subexperiment) ;
      echo "</select> \n" ;
      echo "<br /> \n" ;
   }

   #
   # Determine which cycle(s) to display data for 
   # (currently only supports one cycle at a time
   #
   if ( $_GET["cycles"] ) {
      $selected_cycles = $_GET["cycles"] ;
      $selected_cycles = explode( ',' ,  $selected_cycles ) ;
      $sorted = sort( $selected_cycles ) ;
   }      
  
   # TODO : These should probably be check boxes
   #        Create option to download archive of all the runs
   if ( $selected_subexperiment) {
      echo_form_label("Cycle") ;
      echo "<select name='cycles' onChange='this.form.submit()'> \n" ;
      $subexperiment_dir = $experiment_dir . "/" . $selected_subexperiment ;
      if ( is_dir($subexperiment_dir) ) {
         if ( $dh=opendir($subexperiment_dir) ) {

            // first, filter out some directories and create a sorted array of product subdirectories
            $sorted_list_of_products = array() ;
            while(( $productdir = readdir($dh) ) !== false) {
               if ( $productdir == "." ) continue ;
               if ( $productdir == ".." ) continue ;
               // occasionally, there are files in the directory (i.e. not subdirectories, e.g. tgz's), ignre them
               if ( ! is_dir($subexperiment_dir . "/" . $productdir)) continue ;
               array_push( $sorted_list_of_products, $productdir) ;
            }

            // now iterate through the sorted array and transform the directory names into something more
            // human readable
            $sorted = sort($sorted_list_of_products) ;
            for ( $i=0 ; $i<count($sorted_list_of_products) ; $i++ ) {
               $productdir = $sorted_list_of_products[$i] ;
               // Make more human readable
               $productdirHR = strtr( $productdir, '_', '/') ;
               $correspondingDate = substr( $productdirHR, 9, 10 ) ;
               $correspondingHour = substr( $productdirHR, 20, 2 ) ;
               $correspondingMin = substr( $productdirHR, 23, 2 ) ;
               $productdirHR = $correspondingDate . "  @  " . $correspondingHour . $correspondingMin . "z" ;
               
               // add to drop down list
               if ( in_array( $productdir, $selected_cycles ))
                  printf("<option value='%s' selected> %s </option> \n", $productdir, $productdirHR) ; 
               else
                  printf("<option value='%s'> %s </option> \n", $productdir, $productdirHR) ; 
            }
         }
      }
      echo "</select> \n" ;
      echo "<br /> \n" ;
   }

   if ( $_GET["product_types"]) {
      $product_types = explode(",", $_GET["product_types"]) ; 
   }

   # If cycles have been selected, select the product type
   if ( $selected_cycles ) {
      echo_form_label("Product") ;
      echo "<select name='product_types' onChange='this.form.submit()'> \n" ;
      # TODO Support multiple cycles
      for ( $i=0 ; $i<count($selected_cycles) ; $i++ ) {
         $selected_cycle_dir = $selected_cycles[$i] ;
         $product_subdir = $subexperiment_dir . "/" . $selected_cycle_dir ;
         
         // see what products are available
         if ( is_dir($product_subdir) ) {
            if ( $dh=opendir($product_subdir) ) {
               while( ($productName = readdir($dh) ) !== false) {
                  #echo "<option value='" . $productName . "'> " . $productName . "</option> \n" ;
                  if ( $productName == "." ) continue ;
                  if ( $productName == ".." ) continue ;
                  $productNameHR = $productName ;
                  // add to drop down list
                  // if productName in product_types
                  if ( in_array( $productName, $product_types ))
                     echo "<option value='" . $productName . "' selected >" . $productNameHR . "</option> \n" ;
                  else
                     #printf("<option value='%s'> %s </option> \n, $productName, $productNameHR") ;
                     echo "<option value='" . $productName . "'> " . $productNameHR . "</option> \n" ;

               }
            }
         }
      }
      echo "</select> \n" ;
      echo "<br /> \n" ;
   }
   
   echo "<button type='submit'>Update</button>" ;
   echo "</form>" ;
   echo "<form action='" . $_SERVER['PHP_SELF'] . "'>" ;
   echo "<input type='submit' value='reset'/>" ;
   echo "</form>" ;
   
   echo "<h2>Results</h2>" ;

   //
   // For each selected product type, list the directory contents as a link
   //
   if ( $product_types ) {
      for ( $i=0 ; $i<count($product_types) ; $i++ ) {
         # TODO : Recursively iterate through directories
         $product_type = $product_types[$i] ;
         $product_type_subdir = $product_subdir . "/" . $product_type ;
         if ( is_dir($product_type_subdir) ) {
            if ( $dh = opendir($product_type_subdir) ) {
               while ( ( $fileName = readdir($dh) ) !== false) {
                  if ( $fileName == ".") continue ;
                  if ( $fileName == "..") continue ;
                  // The link needs to be relative to the current working directory 
                  $link =  "experiments" . "/" . $selected_experiment_type . "/" . $selected_experiment . "/" . $selected_subexperiment .  "/" . $selected_cycle_dir . "/" . $product_type . "/" . $fileName ;
                  if ( is_dir($link) ) continue ; # TODO: ITERATE
                  printf("<a href='%s'>%s</a> <br /> \n", $link, $fileName) ;
               }
            }
         }
      }
   }
?>
</div>
<br />
<br />
<p>
<a href="https://docs.google.com/a/noaa.gov/spreadsheet/ccc?key=0AnC1wmqcWwXrdDVMY21QZ0w0bklaR05qM05Fck9KSGc&usp=drive_web#gid=0">OSSE Experiments Spreadsheet</a>
</p>
</body>
</html>
