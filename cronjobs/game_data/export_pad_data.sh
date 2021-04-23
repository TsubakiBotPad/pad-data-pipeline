#!/bin/bash
cd "$(dirname "$0")" || exit
source ../shared.sh
source /home/bot/pad-data-pipeline/bin/activate

cd "${GAME_DATA_DIR}" || exit
git pull --rebase --autostash

python3 "${UTILS_ETL_DIR}/data_exporter.py" \
  --input_dir="${RAW_DIR}" \
  --output_dir="${GAME_DATA_DIR}"
