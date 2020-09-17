#!/usr/bin/env bash
cd "$(dirname "$0")"
mysql_db="https://d1kpnpud0qoyxf.cloudfront.net/db/dadguide.mysql"
sqlite_db="https://d1kpnpud0qoyxf.cloudfront.net/db/dadguide.sqlite"
folder="../pad_data/db/"
wget -P $folder -N $mysql_db
wget -P $folder -N $sqlite_db
