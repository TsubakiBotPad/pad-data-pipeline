<?php
  $dg_home = "/home/tactical0retreat/dadguide"
  $script = "${dg_home}/dadguide-data/web/serve_dadguide_data.py";
  $db_config = "${dg_home}/dadguide-jobs/db_config.json";

  $cmd = "python3 ${script} --db_config=${db_config} --db_table=${tbl_name}";
  if (array_key_exists("tstamp", $_POST)) {
    $tstamp = $_POST["tstamp"];
    $cmd = "$cmd --tstamp=${tstamp}";
  }
  if (array_key_exists("plain", $_POST)) {
    $cmd = "$cmd --plain";
  }

  passthru($cmd, $err);
?>
