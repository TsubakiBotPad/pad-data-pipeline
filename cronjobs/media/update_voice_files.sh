#!/bin/bash
#
# Updates the local cache of voice files and fixes them.

cd "$(dirname "$0")" || exit
source ../shared.sh

RUN_DIR="${MEDIA_ETL_DIR}/voice_pull"
CACHE_DIR=/home/tactical0retreat/pad_data/voices/raw
FINAL_DIR=/home/tactical0retreat/dadguide/data/media/voices

python3 "${RUN_DIR}/PADVoiceDownload.py" \
  --cache_dir="${CACHE_DIR}" \
  --final_dir="${FINAL_DIR}" \
  --server=na

python3 "${RUN_DIR}/PADVoiceDownload.py" \
  --cache_dir="${CACHE_DIR}" \
  --final_dir="${FINAL_DIR}" \
  --server=jp
