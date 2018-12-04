
<?php
  $csv_file_loc = "test_csv/Localization.csv";
  $csv_file_sync = "test_csv/SyncFetch.csv";
  $csv_file_async = "test_csv/AsyncFetch.csv";

  if($_REQUEST["time-localization"]){
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

  if($_REQUEST["time-sync"]){
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

  if($_REQUEST["time-async"]){
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
