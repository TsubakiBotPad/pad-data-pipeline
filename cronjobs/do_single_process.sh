#!/bin/bash
set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared.sh
source ./discord.sh

function human_fixes_check() {
  human_fixes_path="/tmp/dadguide_pipeline_human_fixes.txt"
  if [[ -s ${human_fixes_path} ]]; then
    echo "Alerting for human fixes"
    hook_warn "\`\`\`\n$(cat /tmp/dadguide_pipeline_human_fixes.txt \
                       | sed ':a;N;$!ba;s/\n/\\n/g' \
                       | head -c 1990)\n\`\`\`"
  else
    echo "No fixes required"
  fi
}

flock -xn /tmp/dg_processor.lck python3 "${ETL_DIR}/data_processor.py" \
  --input_dir="${RAW_DIR}" \
  --es_dir="${ES_DIR}" \
  --media_dir="${DADGUIDE_MEDIA_DIR}" \
  --output_dir="${DADGUIDE_DATA_DIR}/processed" \
  --db_config="${DB_CONFIG}" \
  --server=$1 \
  --processors=$2 \
  --skipintermediate \
  --doupdates \
  --skip_long

human_fixes_check
