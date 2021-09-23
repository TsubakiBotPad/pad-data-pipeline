#!/usr/bin/env bash
cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh
source "${VENV_ROOT}/bin/activate"

cd "${GAME_DATA_DIR}" || exit
git pull --rebase --autostash

python3 "${ETL_DIR}/rebuild_enemy_skills.py" \
  --input_dir="${RAW_DIR}" \
  --output_dir="${GAME_DATA_DIR}"

git add behavior_*
git commit -m 'Enemy skill update' || true
git push
