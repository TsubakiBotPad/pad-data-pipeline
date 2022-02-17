#!/usr/bin/env bash
set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared_root.sh
source ./shared.sh

source "${VENV_ROOT}/bin/activate"

python3 "${ETL_DIR}/export_spawns.py" \
  --db_config="${DB_CONFIG}" \
  --output_dir="${DADGUIDE_ILMINA_DIR}"
cp -r ${RAW_DIR}/na/. ${DADGUIDE_ILMINA_DIR}
cp "${DADGUIDE_ILMINA_DIR}/download_card_data.json" "${DADGUIDE_ILMINA_DIR}/download_card_data_3.json"
