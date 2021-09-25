#!/usr/bin/env bash

set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared_root.sh
source ./shared.sh
source ./discord.sh
source "${VENV_ROOT}/bin/activate"

function error_exit() {
  hook_error "Autodungeon failed <@&${NOTIFICATION_DISCORD_ROLE_ID}>"
  hook_file "/tmp/dg_scraper_log.txt"
}

function success_exit() {
  echo "Autodungeon finished"
}

function human_fixes_check() {
  processor_fails="/tmp/autodungeon_processor_issues.txt"
  if [[ -s ${processor_fails} ]]; then
    echo "Alerting for autodungeon processor issues"
    hook_file "${processor_fails}"
    hook_warn "\`\`\`\n$(cat "${processor_fails}" \
                       | sed ':a;N;$!ba;s/\n/\\n/g' \
                       | head -c 1990)\n\`\`\`"
  else
    echo "Autodungeon completely successful"
  fi
}

# Enable alerting to discord
trap error_exit ERR
trap success_exit EXIT

flock -xn /tmp/dg_scraper_na.lck python3 ${REPO_ROOT}/etl/auto_dungeon_scrape.py \
  --db_config=${DB_CONFIG} \
  --input_dir=${RAW_DIR} \
  --doupdates \
  --server=na \
  --group=${NA_PAD_USER_COLOR_GROUP} \
  --user_uuid=${NA_PAD_USER_UUID} \
  --user_intid=${NA_PAD_USER_INTID}

human_fixes_check

flock -xn /tmp/dg_scraper_jp.lck python3 ${REPO_ROOT}/etl/auto_dungeon_scrape.py \
  --db_config=${DB_CONFIG} \
  --input_dir=${RAW_DIR} \
  --doupdates \
  --server=jp \
  --group=${JP_PAD_USER_COLOR_GROUP} \
  --user_uuid=${JP_PAD_USER_UUID} \
  --user_intid=${JP_PAD_USER_INTID}

human_fixes_check

hook_info "Autodungeon finished"
