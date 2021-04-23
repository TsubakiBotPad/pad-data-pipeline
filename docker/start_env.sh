#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

container_name="docker_db_1"

folder="../pad_data/db/"
mkdir -p ${folder}

echo "Checking for db file"
local_db_file="${folder}/dadguide.mysql"
if [[ ! -f "${local_db_file}" ]]; then
  echo "Downloading to ${local_db_file}"
  mysql_db="https://d1kpnpud0qoyxf.cloudfront.net/db/dadguide.mysql"
  wget -P $folder -N $mysql_db
fi

echo "Checking if environment has started"
env_up=$(docker ps | grep $container_name) || true
if [[ -z "${env_up}" ]]; then
  echo "Starting environment"
  docker-compose -f docker_mysql.yml up -d
fi

echo "Fetching credentials"
user=$(grep user docker_db_config.json | sed -E 's/.*: "(.*)",/\1/')
pword=$(grep password docker_db_config.json | sed -E 's/.*: "(.*)",/\1/')
echo "using credentials: ${user} ${pword}"

docker exec -i ${container_name} mysql -u ${user} -p${pword} dadguide <${local_db_file}
