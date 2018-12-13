<?php




?>


<!DOCTYPE html>
<html lang="en">

  <head>
    <script type="text/javascript">
       window.onload = setupRefresh;
       function setupRefresh()
       {
           setInterval("getCSVDataForGraph();",1000);
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
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
  </head>

  <body>

    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
      <div class="container">
        <a class="navbar-brand" href="#">Caching Service for AR Applications</a>
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
    <div class="container-fluid" style="height:100%;text-align:center;">
    <div class="line">
        <div class="col-md-6 quad" style="padding-top:10px;border-right:1px lightgrey solid;">
              <h3 style="position:absolute;top:40%;left:40%;z-index:-1;">Select image</h3>
              <img id="preview-image" src="" height="90%">
        </div>
        <div class="col-md-6 quad">
            <canvas id="myChart1" style=""></canvas>
        </div>
        <div class="col-md-6 quad" style="overflow-y: scroll;border-right:1px lightgrey solid;">
              <div class="row text-center text-lg-left">

               <?php
                    //$dir = getcwd()."/";
                    $pic_directory = "user_loc_rgb";
                    //$files_dir = $dir.$pic_directory;
                    foreach(glob($pic_directory.'/*.jpg') as $file) {
                        $go = realpath($file);
                        print("<div class='col-lg-2 col-md-3 col-xs-6' style='height:80px;width:auto'>
                                    <a href='#' class='d-block mb-4 h-150'>
                                        <img class='img-fluid img-thumbnail'  src='$file' onclick='sendFileName(\"$go\",\"$file\")'>
                                    </a>
                                </div>");
                    }
                 ?>


              </div>
        </div>
        <div id="traj" class="col-md-6 quad" style="height:100%; width:100%;">
        </div>
    </div>

</body>
<script>


function sendFileName(file_path, server_path){

  $('#preview-image').attr('src', server_path);
  // console.log(file_path);
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
      //   console.log(json);
         graph1(json.label, json.async, json.localization, json.sync);

      }
  });

  url = "http://localhost:8071/csv_reader.php?trajectory=true";
  var saveData = $.ajax({
      type: 'GET',
      url: url,
      dataType: "text",
      success: function(resultData) {
  //      console.log(resultData);
         var json = JSON.parse(resultData);
        //  console.log(json.localization);

         trajectory_graph(json.localization, json.sync, json.async);

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
              label: 'Asynchronous',
              data: async1.slice(Math.max(async1.length - 30, 1)),
              fill: false,
						  borderColor: "red"
            }, {
              label: 'Synchronous',
              data: sync1.slice(Math.max(sync1.length - 30, 1)),
              // Changes this dataset to become a line
              type: 'line',
              fill: false,
              borderColor:"green"
            },
            {
              label: 'Localization',
              data:localization.slice(Math.max(localization.length - 30, 1)),
              // Changes this dataset to become a line
              type: 'line',
              fill: false,
              borderColor:"blue"
            }
          ],
        labels: labels.slice(Math.max(labels.length - 30, 1))
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

function trajectory_graph(localization, sync, async){

  localization_points = {
    x: localization.map(pair => pair.x),
    y: localization.map(pair => pair.y),
    mode: 'markers',
    type: 'scatter',
    marker: { size: 2, color: 'rgb(255, 0, 0)' }
  };
  
  var async_circles = async.map(pair => { return {
    type: 'circle',
    xref: 'x',
    yref: 'y',
    fillcolor: 'rgba(29, 192, 33, 0.08)',
    x0: parseFloat(pair.x) - 3.5,
    y0: parseFloat(pair.y) - 3.5,
    x1: parseFloat(pair.x) + 3.5,
    y1: parseFloat(pair.y) + 3.5,
    line: {
      color: 'rgba(29, 192, 33, 0.15)',
      width: 1
    }
  }});


  var layout = {
    xaxis: {
      range: [-5, 60],
      zeroline: true,
      dtick: 5,
    },
    yaxis: {
      range: [-5, 25],
      scaleanchor: "x",
      dtick: 5
    },
    margin: {
      t: 40, //top margin
      l: 40, //left margin
      r: 40, //right margin
      b: 40 //bottom margin
    },
    shapes: async_circles
  };

  Plotly.newPlot('traj', [localization_points], layout);

}
</script>

</html>
