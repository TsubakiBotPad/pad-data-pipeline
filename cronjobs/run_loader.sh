#!/bin/bash
#
# Expects a file called account_config.csv to exist, formatted as:
# <[JP,NA]>,<[A,B,C,D,E]>,<uuid>,<int_id>,<RED,GREEN,BLUE>
#
# Group ID and starter color are not used, just for documentation

source /home/bot/pad-data-pipeline/bin/activate

set -e
set -x

cd "$(dirname "$0")" || exit
source ./discord.sh
source ./shared.sh

echo "Processing"
IFS=","

function error_exit {
    hook_error "DadGuide Pipeline failed <@&${NOTIFICATION_DISCORD_ROLE_ID}>"
    hook_file "/tmp/dg_update_log.txt"
}

function success_exit {
    echo "Pipeline finished"
}

# Enable alerting to discord
trap error_exit ERR
trap success_exit EXIT

function dl_data() {
  # shellcheck disable=SC2034
  while read -r server group uuid intid scolor; do
    do_only_bonus=""
    if [ "${scolor^^}" != "RED" ]; then
      do_only_bonus="--only_bonus"
    fi

    echo "Processing ${server}/${scolor}/${uuid}/${intid} ${do_only_bonus}"
    EXIT_CODE=0
    python3 "${ETL_DIR}/pad_data_pull.py" \
      --output_dir="${PAD_DATA_DIR}/raw/${server,,}" \
      --server="${server^^}" \
      --user_uuid="${uuid}" \
      --user_intid="${intid}" \
      --user_group="${scolor}" \
      ${do_only_bonus} || EXIT_CODE=$?

    if [ $EXIT_CODE -ne 0 ]; then
      hook_error "Processing ${server}/${scolor} failed with code ${EXIT_CODE}"
    fi
  done <$1
}

dl_data "${ACCOUNT_CONFIG}"

echo "Updating DadGuide"
./data_processor.sh

echo "Exporting Data"
./export_data.sh

echo "Syncing"
./sync_data.sh
      
hook_info "Pipeline completed successfully!"
