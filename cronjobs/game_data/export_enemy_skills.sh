#!/bin/bash
cd "$(dirname "$0")" || exit
source ../shared.sh

cd "${GAME_DATA_DIR}" || exit
git pull --rebase --autostash

python3 "${ETL_DIR}/rebuild_enemy_skills.py" \
  --input_dir="${RAW_DIR}" \
  --output_dir="${GAME_DATA_DIR}"

git add behavior_*
git commit -m 'rebuild enemy skills'
git push
