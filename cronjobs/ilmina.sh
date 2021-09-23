#!/usr/bin/env bash
set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared_root.sh
source ./shared.sh

python3 "${ETL_DIR}/export_spawns.py" \
  --db_config="${DB_CONFIG}" \
  --output_dir="${DADGUIDE_ILMINA_DIR}"
cp -r ${RAW_DIR}/na/. ${DADGUIDE_ILMINA_DIR}
