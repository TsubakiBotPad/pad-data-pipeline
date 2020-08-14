#!/bin/bash
cd "$(dirname "$0")" || exit
source ../shared.sh

cd "${GAME_DATA_DIR}" || exit
git pull --rebase --autostash

python3 "${UTILS_ETL_DIR}/data_exporter.py" \
  --input_dir="${RAW_DIR}" \
  --output_dir="${GAME_DATA_DIR}"

git add .
git commit -m 'data updates'
git push
