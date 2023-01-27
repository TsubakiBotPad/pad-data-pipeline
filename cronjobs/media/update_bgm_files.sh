#!/usr/bin/env bash
#
# Updates the local cache of voice files and fixes them.

cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh
source "${VENV_ROOT}/bin/activate"

RUN_DIR="${MEDIA_ETL_DIR}/extras"
EXTRA_DIR="${PAD_DATA_DIR}/extras"
FINAL_DIR="${DADGUIDE_MEDIA_DIR}/bgm"

for server in na jp; do
  python3 "${RUN_DIR}/PADDSMGParser.py" \
    --db_config="${DB_CONFIG}" \
    --server=$server

  python3 "${RUN_DIR}/PADBGMDownload.py" \
    --extra_dir="${EXTRA_DIR}" \
    --final_dir="${FINAL_DIR}" \
    --server=$server
done
