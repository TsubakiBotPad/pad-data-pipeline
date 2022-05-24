#!/usr/bin/env bash
set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared_root.sh
source ./shared.sh
source ./discord.sh

function error_exit() {
  hook_error "Azurlane pull failed <@&${NOTIFICATION_DISCORD_ROLE_ID}>"
}

function success_exit() {
  hook_info "Azurlane pull succeeded"
}

# Enable alerting to discord
trap error_exit ERR
trap success_exit EXIT

flock -xn /tmp/dg_processor.lck python3 "${ETL_DIR}/misc/azurlane_image_download.py" \
  --output_dir="${DADGUIDE_DATA_DIR}/azurlane"
