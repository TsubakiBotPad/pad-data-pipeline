#!/bin/bash
set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared.sh

flock -xn /tmp/dg_scraper_na.lck python3 /home/bot/dadguide-data/etl/auto_dungeon_scrape.py \
  --db_config=${DB_CONFIG} \
  --input_dir=${RAW_DIR} \
  --doupdates \
  --server=na \
  --group=red \
  --user_uuid="00000000-0000-0000-00000000000000000" \
  --user_intid="111111111"

flock -xn /tmp/dg_scraper_jp.lck python3 /home/bot/dadguide-data/etl/auto_dungeon_scrape.py \
  --db_config=${DB_CONFIG} \
  --input_dir=${RAW_DIR} \
  --doupdates \
  --server=jp \
  --group=blue \
  --user_uuid="00000000-0000-0000-00000000000000000" \
  --user_intid="111111111"

