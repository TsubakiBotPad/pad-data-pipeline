#!/usr/bin/env bash
#
# Updates the local cache of story files.

cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh
source "${VENV_ROOT}/bin/activate"

RUN_DIR="${MEDIA_ETL_DIR}/story_pull"
TOOL_DIR=${RUN_DIR}

CACHE_DIR="${PAD_DATA_DIR}/story"
OUTPUT_DIR="${DADGUIDE_MEDIA_DIR}/story"

python3 "${RUN_DIR}/PADStoryDownload.py" \
  --tool_dir="${TOOL_DIR}" \
  --cache_dir="${CACHE_DIR}" \
  --output_dir="${OUTPUT_DIR}" \
  --server=na

python3 "${RUN_DIR}/PADStoryDownload.py" \
  --tool_dir="${TOOL_DIR}" \
  --cache_dir="${CACHE_DIR}" \
  --output_dir="${OUTPUT_DIR}" \
  --server=jp
