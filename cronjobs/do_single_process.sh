#!/usr/bin/env bash
set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared_root.sh
source ./shared.sh
source ./discord.sh

flock -xn /tmp/dg_processor.lck python3 "${ETL_DIR}/data_processor.py" \
  --input_dir="${RAW_DIR}" \
  --es_dir="${ES_DIR}" \
  --media_dir="${DADGUIDE_MEDIA_DIR}" \
  --output_dir="${DADGUIDE_DATA_DIR}/processed" \
  --db_config="${DB_CONFIG}" \
  --server=$1 \
  --processors=$2 \
  --skipintermediate \
  --doupdates
