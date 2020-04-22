<?php
  header('Content-Type: application/json');

  $dg_home = "/home/tactical0retreat/dadguide";
  $script = "${dg_home}/dadguide-data/web/serve_dadguide_donor.py";
  $db_config = "${dg_home}/dadguide-jobs/db_config.json";

  $email = $_REQUEST["email"];

  $cmd = "python3 ${script} --db_config=${db_config} --email=${table}";
  passthru($cmd, $err);
?>
