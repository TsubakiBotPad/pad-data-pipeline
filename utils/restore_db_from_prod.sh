#!/usr/bin/env bash
cd "$(dirname "$0")"
user=$(grep user ../etl/db_config.json | sed -r 's/.*: "(.*)",/\1/')
pword=$(grep password ../etl/db_config.json | sed -r 's/.*: "(.*)",/\1/')
input_file="../pad_data/db/dadguide.mysql"

echo "using credentials: ${user} ${pword}"
mysql -u ${user} -p${pword} dadguide <${input_file}
