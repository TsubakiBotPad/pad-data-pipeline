#!/usr/bin/env bash
#
# Updates the local cache of voice files and fixes them.

cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh
source "${VENV_ROOT}/bin/activate"

RUN_DIR="${MEDIA_ETL_DIR}/bgm_pull"
EXTRA_DIR="${PAD_DATA_DIR}/extras"
FINAL_DIR="${DADGUIDE_MEDIA_DIR}/bgm"

python3 "${RUN_DIR}/PADBGMDownload.py" \
  --extra_dir="${EXTRA_DIR}" \
  --final_dir="${FINAL_DIR}" \
  --server=na

python3 "${RUN_DIR}/PADBGMDownload.py" \
  --extra_dir="${EXTRA_DIR}" \
  --final_dir="${FINAL_DIR}" \
  --server=jp
