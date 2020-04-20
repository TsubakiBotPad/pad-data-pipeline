#!/usr/bin/env bash
cd "$(dirname "$0")"
mysql_db="https://f002.backblazeb2.com/file/dadguide-data/db/dadguide_wave_data.mysql.zip"
folder="../pad_data/db/"
wget -P $folder -N $mysql_db
unzip "$folder/dadguide_wave_data.mysql.zip" -d $folder
