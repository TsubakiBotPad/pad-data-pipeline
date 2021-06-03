#!/bin/bash

set -e
set -x

cd "$(dirname "$0")" || exit
source ./discord.sh
source ./shared.sh
source "${VENV_ROOT}/bin/activate"

# This may not work on Mac
options=$(getopt -o '' --long server:,processor: -- "$@")
eval set -- "$options"
SERVER=""
PROCESSOR=""
while true; do
    case "$1" in
    --server)
        shift;
        SERVER=${1^^}
        [[ ! $COLOR =~ JP|NA|KR|COMBINED ]] && {
            echo "Server must be JP/NA/KR"
            exit 1
        }
        ;;
    --processor)
        shift;
        PROCESSOR=$1
        ;;
    --)
        shift
        break
        ;;
    esac
    shift
done

function error_exit() {
  hook_error "DadGuide $SERVER Pipeline failed <@&${NOTIFICATION_DISCORD_ROLE_ID}>"
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
if [ -z "$PROCESSOR" ]; then
  ./data_processor.sh $SERVER
else
  ./do_single_process.sh "$SERVER" "$PROCESSOR"
fi

echo "Exporting Data"
./export_data.sh

echo "Syncing"
./sync_data.sh

hook_info "Pipeline completed successfully!"
