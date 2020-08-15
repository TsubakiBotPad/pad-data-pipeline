<?php
  header('Content-Type: application/json');

  $dg_home = "/home/bot/dadguide";
  $script = "${dg_home}/dadguide-data/web/serve_dadguide_data.py";
  $db_config = "${dg_home}/dadguide-jobs/db_config.json";

  $table = $_REQUEST["table"];

  $cmd = "python3 ${script} --db_config=${db_config} --table=${table}";
  if (array_key_exists("tstamp", $_REQUEST)) {
    $tstamp = $_REQUEST["tstamp"];
    $cmd = "$cmd --tstamp=${tstamp}";
  }
  if (array_key_exists("plain", $_REQUEST)) {
    $cmd = "$cmd --plain";
  }

  passthru($cmd, $err);
?>
