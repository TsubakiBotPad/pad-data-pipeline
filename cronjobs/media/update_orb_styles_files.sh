#!/usr/bin/env bash
#
# Updates the local cache of orb skin files.

cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh
source "${VENV_ROOT}/bin/activate"

RUN_DIR="${MEDIA_ETL_DIR}/orb_styles_pull"
CACHE_DIR="${PAD_DATA_DIR}/orb_styles"
OUTPUT_DIR="${DADGUIDE_MEDIA_DIR}/orb_skins"

python3 "${RUN_DIR}/PADOrbStylesDownload.py" \
  --cache_dir="${CACHE_DIR}" \
  --output_dir="${OUTPUT_DIR}" \
  --server=na

python3 "${RUN_DIR}/PADOrbStylesDownload.py" \
  --cache_dir="${CACHE_DIR}" \
  --output_dir="${OUTPUT_DIR}" \
  --server=jp
