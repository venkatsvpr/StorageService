
<?php
  $csv_file_loc = "/tmp/Localization.csv";
  $csv_file_sync = "/tmp/SyncFetch.csv";
  $csv_file_async = "/tmp/AsyncFetch.csv";
  $csv_trajectory = "/tmp/Trajectory.csv";



  if(isset($_REQUEST["trajectory"]) && $_REQUEST["trajectory"]){
    $labels = array();
    $time = array();
    $file = fopen($csv_trajectory, 'r');
    while (($line = fgetcsv($file)) !== FALSE) {
      $first[] = $line[0];
      $second[] = $line[1];
      $third[] = $line[2];
    }

    $map = array();
    $map['x'] = $first;
    $map['y'] = $second;
    $map['type'] = $third;
    fclose($file);

    $response_json = json_encode($map);
    echo $response_json;
  }


  if(isset($_REQUEST["time-localization"]) && $_REQUEST["time-localization"]){
    $labels = array();
    $time = array();
    $file = fopen($csv_file_loc, 'r');
    while (($line = fgetcsv($file)) !== FALSE) {
      $labels[] = $line[0];
      $time[] = $line[1];
    }
    $map = array();
    $map['label'] = $labels;
    $map['time'] = $time;
    fclose($file);

    $response_json = json_encode($map);
    echo $response_json;
  }

  if(isset($_REQUEST["time-sync"]) && $_REQUEST["time-sync"] ){
    $labels = array();
    $time = array();
    $file = fopen($csv_file_sync, 'r');
    while (($line = fgetcsv($file)) !== FALSE) {
      $labels[] = $line[0];
      $time[] = $line[1];
    }
    $map = array();
    $map['label'] = $labels;
    $map['time'] = $time;
    fclose($file);

    $response_json = json_encode($map);
    echo $response_json;
  }

  if(isset($_REQUEST["time-async"]) && $_REQUEST["time-async"]){
    $labels = array();
    $time = array();
    $file = fopen($csv_file_async, 'r');
    while (($line = fgetcsv($file)) !== FALSE) {
      $labels[] = $line[0];
      $time[] = $line[1];
    }
    $map = array();
    $map['label'] = $labels;
    $map['time'] = $time;
    fclose($file);

    $response_json = json_encode($map);
    echo $response_json;
  }

?>
