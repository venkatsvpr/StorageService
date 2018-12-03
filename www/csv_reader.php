
<?php

  if($_REQUEST["time-plot"]){
    $csv_file = "test.csv";
    $labels = array();
    $time = array();
    $file = fopen($csv_file, 'r');
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
