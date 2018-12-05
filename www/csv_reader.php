
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

?>
