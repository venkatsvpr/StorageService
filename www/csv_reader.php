
<?php
  $csv_file_loc = "test_csv/Localization.csv";
  $csv_file_sync = "test_csv/SyncFetch.csv";
  $csv_file_async = "test_csv/AsyncFetch.csv";
  $csv_trajectory = "test_csv/Trajectory.csv";

  if(isset($_REQUEST["trajectory"]) && $_REQUEST["trajectory"]){

    $labels = array();
    $time = array();
    $file = fopen($csv_trajectory, 'r');
    $localization = array();
    $sync = array();
    $async = array();

    while (($line = fgetcsv($file)) !== FALSE) {
      $type = $line[0];
      $localization_val= array();
      $sync_val = array();
      $async_val = array();
      if($type == 1){
        $localization_val['x'] = $line[1];
        $localization_val['y'] = $line[2];
        $localization[] = $localization_val;
      }
      else if($type == 2){
        $sync_val['x'] = $line[1];
        $sync_val['y'] = $line[2];
        $sync_val['r'] = $line[4] * 50;
        $sync[] = $sync_val;
      }
      else if($type == 3){
        $async_val['x'] = $line[1];
        $async_val['y'] = $line[2];
        $async_val['r'] = $line[4] * 50;
        $async[] = $async_val;
      }
    }

    $map = array();

    $map['localization'] = $localization;
    $map['sync'] = $sync;
    $map['async'] = $async;

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
