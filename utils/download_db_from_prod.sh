#!/usr/bin/env bash
mysql_db="https://f002.backblazeb2.com/file/dadguide-data/db/dadguide.mysql"
sqlite_db="https://f002.backblazeb2.com/file/dadguide-data/db/dadguide.sqlite"
folder="../pad_data/db/"
wget -P $folder -N $mysql_db
wget -P $folder -N $sqlite_db
