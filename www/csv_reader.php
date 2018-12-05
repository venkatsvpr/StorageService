
<?php
  $csv_file_loc = "test_csv/Localization.csv";
  $csv_file_sync = "test_csv/SyncFetch.csv";
  $csv_file_async = "test_csv/AsyncFetch.csv";
  $csv_trajectory = "test_csv/Trajectory.csv";



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


  if(isset($_REQUEST['populate-time-graph']) && $_REQUEST["populate-time-graph"]){

    $labels = array();
    $localization = array();
    $sync = array();
    $async = array();
    $label =0;

    $file = fopen($csv_file_loc, 'r');

    while (($line = fgetcsv($file)) !== FALSE) {
      $labels[] = $label++;
      $localization[] = $line[1];
    }
    fclose($file);



    $file = fopen($csv_file_sync, 'r');

    while (($line = fgetcsv($file)) !== FALSE) {
      $sync[] = $line[1];
    }
    fclose($file);


    $file = fopen($csv_file_async, 'r');
    while (($line = fgetcsv($file)) !== FALSE) {
      $async[] = $line[1];
    }
    fclose($file);


    $map = array();

    $map['localization'] = $localization;
    $map['sync'] = $sync;
    $map['async'] = $async;
    $map['label'] = $labels;

    $response_json = json_encode($map);
    echo $response_json;
  }

  if(isset($_REQUEST["time-sync"]) && $_REQUEST["time-sync"] ){

  }

  if(isset($_REQUEST["time-async"]) && $_REQUEST["time-async"]){
    $labels = array();
    $time = array();
    $file = fopen($csv_file_async, 'r');
    $label = 0;
    while (($line = fgetcsv($file)) !== FALSE) {
      $labels[] = $label++;
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
