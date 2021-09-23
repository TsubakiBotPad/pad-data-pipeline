#!/usr/bin/env bash
#
# Updates the local cache of hq monster pics.

cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh
source "${VENV_ROOT}/bin/activate"

python3 "${MEDIA_ETL_DIR}/image_pull/PADImageDownload.py" \
  --alt_input_dir="${IMG_DIR}/jp/full/raw_data" \
  --output_dir="${IMG_DIR}/hq_images"
