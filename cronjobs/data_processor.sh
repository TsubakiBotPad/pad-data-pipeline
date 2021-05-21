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

case ${1^^} in
  '') CUR_DB_CONFIG="${DB_CONFIG}"; ;;
  JP) CUR_DB_CONFIG="${JP_DB_CONFIG}"; ;;
  NA) CUR_DB_CONFIG="${NA_DB_CONFIG}"; ;;
  KR) CUR_DB_CONFIG="${KR_DB_CONFIG}"; ;;

  *)
    echo "The first positional argument must be NA, JP, or KR."
    exit 1
  ;;
esac

flock -xn /tmp/dg_processor.lck python3 "${ETL_DIR}/data_processor.py" \
  --input_dir="${RAW_DIR}" \
  --es_dir="${ES_DIR}" \
  --media_dir="${DADGUIDE_MEDIA_DIR}" \
  --output_dir="${DADGUIDE_DATA_DIR}/processed" \
  --db_config="${CUR_DB_CONFIG}" \
  --server=${1:-JP} \
  --doupdates \
  --skip_long

human_fixes_check
