#!/usr/bin/env bash
cd "$(dirname "$0")"
mysql_db="https://d1kpnpud0qoyxf.cloudfront.net/db/dadguide_wave_data.mysql.zip"
folder="../pad_data/db/"
wget -P $folder -N $mysql_db
unzip "$folder/dadguide_wave_data.mysql.zip" -d $folder
