<html>
   <head>

      <title> Portal :: TEST :: get_matching_experiments </title>
      <link rel="stylesheet" type="text/css" href="_styles.css" media="screen">

      <script type="text/javascript">
      function handleExperimentCriteriaChange(url) {

         // create httpRequest object
         var httpRequest ;
         if ( window.XMLHttpRequest ) {
            httpRequest = new XMLHttpRequest() ;
         } 
         else if (window.ActiveXObject) {
            try {
               httpRequest = new ActiveXObject("Msxml2.XMLHTTP");
            }
            catch (e) {
               try {
                  httpRequest = new ActiveXObject("Microsoft.XMLHTTP");
               }
               catch(e) {} // fail
            }
         }
         if (!httpRequest) {
            alert('Giving up :( Cannot create an XMLHTTP instance');
            return false;
         }
         // set HTTP Request object
         httpRequest.onreadystatechange  = getMatchingExperiments ;
         httpRequest.open('GET', url) ;
         httpRequest.send() ;
      
         // needs to be an inner function to have access to httpRequest object
         function getMatchingExperiments() {
            if (  httpRequest.readyState == 4 ) {
               if (httpRequest.status == 200 ) {
                  matching_experiments_pane= document.getElementById("exptPane1").innerHTML = httpRequest.responseText ;
               }
               else {
                  alert('Problem with request')
               }
            }
         }
      }

      </script>
   </head>

   <body>
      <span id="experimentCriteriaUpdateButton" onclick="handleExperimentCriteriaChange('get_matching_experiments.php?spinup_date=200508010000&experiment_type[]=enkf&experiment_type[]=gsi&end_date=200508050000')" >
         click me!         
      </span>
      <div id="exptPane1">Results should go here</div>

   </body>

</html>
