#!/bin/bash

set -e
set -x

cd "$(dirname "$0")" || exit
source ./discord.sh
source ./shared.sh
source "${VENV_ROOT}/bin/activate"

case ${1^^} in
  NA | JP | KR | '')
  ;;

  *)
    echo "The first positional argument must be NA/JP/KR or left unfilled."
    exit 1
  ;;
esac

function error_exit() {
  hook_error "DadGuide $1 Pipeline failed <@&${NOTIFICATION_DISCORD_ROLE_ID}>"
  hook_file "/tmp/dg_update_log.txt"
}

function success_exit() {
  echo "Pipeline finished"
}

# Enable alerting to discord
trap error_exit ERR
trap success_exit EXIT

echo "Pulling Data"
./pull_data.sh

echo "Updating DadGuide"
if [ -z "$2" ]; then
  ./data_processor.sh $1
else
  ./do_single_process.sh $1 $2
fi


echo "Exporting Data"
./export_data.sh

echo "Syncing"
./sync_data.sh

hook_info "Pipeline completed successfully!"
