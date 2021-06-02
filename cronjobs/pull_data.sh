#!/bin/bash
#
# Expects a file called account_config.csv to exist, formatted as:
# <[JP,NA]>,<[A,B,C,D,E]>,<uuid>,<int_id>,<RED,GREEN,BLUE>
#
# Group ID and starter color are not used, just for documentation

set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared.sh
source ./discord.sh

IFS=","

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
