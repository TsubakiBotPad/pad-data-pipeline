#!/bin/bash

source /home/bot/pad-data-pipeline/bin/activate

set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared.sh

flock -xn /tmp/dg_scraper_na.lck python3 ${REPO_ROOT}/etl/auto_dungeon_scrape.py \
  --db_config=${DB_CONFIG} \
  --input_dir=${RAW_DIR} \
  --doupdates \
  --server=na \
  --group=${NA_PAD_USER_COLOR_GROUP} \
  --user_uuid=${NA_PAD_USER_UUID} \
  --user_intid=${NA_PAD_USER_INTID}

flock -xn /tmp/dg_scraper_jp.lck python3 ${REPO_ROOT}/etl/auto_dungeon_scrape.py \
  --db_config=${DB_CONFIG} \
  --input_dir=${RAW_DIR} \
  --doupdates \
  --server=jp \
  --group=${JP_PAD_USER_COLOR_GROUP} \
  --user_uuid=${JP_PAD_USER_UUID} \
  --user_intid=${JP_PAD_USER_INTID}
