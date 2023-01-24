#!/usr/bin/env bash
#
# Updates the local cache of hq monster pics.

cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh
source "${VENV_ROOT}/bin/activate"

python3 "${MEDIA_ETL_DIR}/image_pull/PADHQImageDownload.py" \
  --raw_file_dir="${IMG_DIR}/jp/portrait/raw_data" \
  --db_config="${DB_CONFIG}" \
  --output_dir="${IMG_DIR}/hq_images"
