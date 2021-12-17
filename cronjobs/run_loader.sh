#!/usr/bin/env bash

set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared_root.sh
source ./shared.sh
source ./discord.sh
source "${VENV_ROOT}/bin/activate"

# This may not work on Mac
options=$(getopt -o '' --long skipdownload,skipupload,server:,processors: -- "$@")
eval set -- "$options"

# Defaults
SERVER="COMBINED"
PROCESSORS=""
DOWNLOAD=1
UPLOAD=1

while true; do
    case "$1" in
    --server)
        shift;
        SERVER=${1^^}
        [[ ! $SERVER =~ JP|NA|KR|COMBINED ]] && {
            echo "Server must be JP/NA/KR"
            exit 1
        }
        ;;
    --processors)
        shift;
        PROCESSORS=$1
        ;;
    --skipdownload)
        DOWNLOAD=0
        ;;
    --skipupload)
        UPLOAD=0
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

if [ $DOWNLOAD -eq 1 ]; then
  echo "Pulling Data"
  ./pull_data.sh
fi

echo "Updating DadGuide"
if [ -z "$PROCESSORS" ]; then
  ./data_processor.sh $SERVER
else
  ./do_single_process.sh "$SERVER" "$PROCESSORS"
fi

echo "Exporting Data"
./export_data.sh

if [ $UPLOAD -eq 1 ]; then
  echo "Syncing"
  ./sync_data.sh
fi

hook_info "Pipeline completed successfully!"
