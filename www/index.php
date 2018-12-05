<?php




?>


<!DOCTYPE html>
<html lang="en">

  <head>
    <script type="text/javascript">
       window.onload = setupRefresh;
       function setupRefresh()
       {
           setInterval("getCSVDataForGraph();",5000);
       }
 </script>

    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>Storage Service</title>
    <link href="vendor/bootstrap/css/bootstrap.min.css" rel="stylesheet">
    <link href="css/thumbnail-gallery.css" rel="stylesheet">
    <script src="vendor/jquery/jquery.min.js"></script>
    <script src="vendor/bootstrap/js/bootstrap.bundle.min.js"></script>
    <script src="vendor/chart-js/Chart.bundle.js"></script>
    <script src="vendor/chart-js/chartjs-init.js"></script>
  </head>

  <body>

    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
      <div class="container">
        <a class="navbar-brand" href="#">Storage Service</a>
        <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarResponsive" aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarResponsive">
          <ul class="navbar-nav ml-auto">
            <!-- <li class="nav-item active">
              <a class="nav-link" href="#">Home
                <span class="sr-only">(current)</span>
              </a>
            </li> -->
          </ul>
        </div>
      </div>
    </nav>

    <!-- Page Content -->
    <div class="container-fluid">
    <div class="row">
    <div class="col-sm-5" style="border-right:1px solid #eee; ">
              <h3 class="my-4 text-center text-lg-left">Virtual Locations of the User </h3>
              <div class="col-sm-12" style="height:300px">
                   <img id="preview-image" src="" alt="Current Location of the User" height="300px" width="100%">
              </div>
              <div class="col-sm-12" style="overflow-y: scroll; height:450px; margin-top:10px;">
              <div class="row text-center text-lg-left">

                <?php
                    //$dir = getcwd()."/";
                    $pic_directory = "user_loc_rgb";
                    //$files_dir = $dir.$pic_directory;
                    foreach(glob($pic_directory.'/*.jpg') as $file) {
                        $go = realpath($file);
                        print("<div class='col-lg-3 col-md-4 col-xs-6'>
                                    <a href='#' class='d-block mb-4 h-150'>
                                        <img class='img-fluid img-thumbnail' src='$file' onclick='sendFileName(\"$go\",\"$file\")'>
                                    </a>
                                </div>");
                    }
                 ?>


              </div>
            </div>
    </div>
        <!-- charts -->
    <div class="col-sm-7" id = "chart_div">
        <div class="row">
            <div class="col-sm-12">
                <canvas id="myChart1" width="500px" height="200"></canvas>
            </div>
        </div>
        <div class="row">
          <div class="col-sm-12">
            <canvas id = "trajectory" width = "500px" height = "200"></canvas>
          </div>
        <div>
    </div>
</div>
</div>
    <!-- /.container -->

    <!-- Footer -->
    <!-- <footer class="py-5 bg-dark">
      <div class="container">
        <p class="m-0 text-center text-white">Copyright &copy; Your Website 2017</p>
      </div>
    </footer> -->

    <!-- Bootstrap core JavaScript -->
<div id ="temp"></div>
  </body>
  <script>


function sendFileName(file_path, server_path){

  $('#preview-image').attr('src', server_path);
  console.log(file_path);
   getCSVDataForGraph();
   url ="http://localhost:8099?url="+file_path;
   var xmlHttp = new XMLHttpRequest();
   xmlHttp.open( "GET", url, true ); // false for synchronous request
   xmlHttp.send();

}

function getCSVDataForGraph(){
  url = "http://localhost:8071/csv_reader.php?populate-time-graph=true";

  var saveData = $.ajax({
      type: 'GET',
      url: url,
      dataType: "text",
      success: function(resultData) {
      //   console.log(resultData);
         var json = JSON.parse(resultData);
         console.log(json);
         graph1(json.label, json.async, json.localization, json.sync);

      }
  });

  url = "http://localhost:8071/csv_reader.php?trajectory=true";
  var saveData = $.ajax({
      type: 'GET',
      url: url,
      dataType: "text",
      success: function(resultData) {
        console.log(resultData);
         var json = JSON.parse(resultData);
         graph4(json.x, json.y);

      }
  });

//  graph4();

}
function graph1(labels, async1, localization, sync1){
  var ctx1 = document.getElementById("myChart1").getContext('2d');
  var myChart = new Chart(ctx1, {
      type: 'line',
      data: {
        datasets: [{
              label: 'asynchronous',
              data: async1,
              fill: false,
						  borderColor: "red"
            }, {
              label: 'synchronous',
              data: sync1,
              // Changes this dataset to become a line
              type: 'line',
              fill: false,
              borderColor:"green"
            },
            {
              label: 'localization',
              data:localization,
              // Changes this dataset to become a line
              type: 'line',
              fill: false,
              borderColor:"blue"
            }
          ],
        labels: labels
      },
      options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero:true
                }
            }]
        },
          animation: {
            duration: 0
            }
      }
  });
}

function graph4(labels, data){
  var ctx3 = document.getElementById("trajectory").getContext('2d');
  var myChart = new Chart(ctx3, {
      type: 'line',
      data: {
        //  labels: ["Red", "Blue", "Yellow", "Green", "Purple", "Orange"],
        labels: labels,
          datasets: [{
              label: 'trajectory',
              data: data,
              backgroundColor: [
                  'rgba(255, 99, 132, 0.2)',
                  'rgba(54, 162, 235, 0.2)',
                  'rgba(255, 206, 86, 0.2)',
                  'rgba(75, 192, 192, 0.2)',
                  'rgba(153, 102, 255, 0.2)',
                  'rgba(255, 159, 64, 0.2)'
              ],
              borderColor: [
                  'rgba(255,99,132,1)',
                  'rgba(54, 162, 235, 1)',
                  'rgba(255, 206, 86, 1)',
                  'rgba(75, 192, 192, 1)',
                  'rgba(153, 102, 255, 1)',
                  'rgba(255, 159, 64, 1)'
              ],
              borderWidth: 1
          }]
      },
      options: {
          scales: {
              yAxes: [{
                  ticks: {
                      beginAtZero:true
                  }
              }]
          },
          animation: {
            duration: 0
            }
      }
  });
}
</script>

</html>
