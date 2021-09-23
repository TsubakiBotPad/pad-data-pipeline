#!/usr/bin/env bash
cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh
source "${VENV_ROOT}/bin/activate"

cd "${GAME_DATA_DIR}" || exit
git add behavior*
git commit -m 'manually approved ES' || true

git pull --rebase --autostash

python3 "${UTILS_ETL_DIR}/data_exporter.py" \
  --input_dir="${RAW_DIR}" \
  --output_dir="${GAME_DATA_DIR}" \
  --image_data_only

git add ./*/assets/
git add ./*/extras/
git commit -m 'asset updates' || true
git push
