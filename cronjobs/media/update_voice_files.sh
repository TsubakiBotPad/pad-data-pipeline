#!/bin/bash
#
# Updates the local cache of voice files and fixes them.

source /home/bot/pad-data-pipeline/bin/activate

cd "$(dirname "$0")" || exit
source ../shared.sh

RUN_DIR="${MEDIA_ETL_DIR}/voice_pull"
CACHE_DIR="${PAD_DATA_DIR}/voices/raw"
FINAL_DIR=/home/bot/dadguide/data/media/voices

python3 "${RUN_DIR}/PADVoiceDownload.py" \
  --cache_dir="${CACHE_DIR}" \
  --final_dir="${FINAL_DIR}" \
  --server=na

python3 "${RUN_DIR}/PADVoiceDownload.py" \
  --cache_dir="${CACHE_DIR}" \
  --final_dir="${FINAL_DIR}" \
  --server=jp
