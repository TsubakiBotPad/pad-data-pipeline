#!/usr/bin/env bash
#
# Updates the local cache of full monster pics / portraits from the JP server.

cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh
source ../discord.sh
source "${VENV_ROOT}/bin/activate"

exec 8>"/tmp/image.lock";
flock -nx 8;

function error_exit() {
  hook_error "Image Pipeline failed <@&${NOTIFICATION_DISCORD_ROLE_ID}>"
  hook_file "/tmp/dg_image_log.txt"
}

function success_exit() {
  echo "Image pipeline finished"
  hook_info "Image pipeline finished"
}

# Enable alerting to discord
trap error_exit ERR
trap success_exit EXIT

RUN_DIR="${MEDIA_ETL_DIR}/assets"

# Enable NVM (Spammy)
set +x
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 16
set -x

for SERVER in na jp; do
  FILE_DIR="${IMG_DIR}/${SERVER}"
  # Make folders (Spammy)
  set +x
  for FOLDER in raw_data portraits cards icons spine_files animated_portraits; do
    mkdir -p "${FILE_DIR}/${FOLDER}"
  done
  set -x
  yarn --cwd=${PAD_RESOURCES_ROOT} update "${FILE_DIR}/raw_data" \
    --new-only --for-tsubaki --server "${SERVER}" --quiet
  yarn --cwd=${PAD_RESOURCES_ROOT} extract "${FILE_DIR}/raw_data" \
    --still-dir "${FILE_DIR}/portraits" \
    --card-dir "${FILE_DIR}/cards" \
    --animated-dir "${FILE_DIR}/spine_files" \
    --new-only --for-tsubaki --server "${SERVER}" --quiet
  xvfb-run -s "-ac -screen 0 640x388x24" \
    yarn --cwd=${PAD_RESOURCES_ROOT} render "${FILE_DIR}/spine_files" \
    --animated-dir "${FILE_DIR}/animated_portraits" \
    --still-dir "${FILE_DIR}/portraits" \
    --new-only --for-tsubaki --server "${SERVER}" --quiet \
  || yarn --cwd=${PAD_RESOURCES_ROOT} render "${FILE_DIR}/spine_files" \
    --animated-dir "${FILE_DIR}/animated_portraits" \
    --still-dir "${FILE_DIR}/portraits" \
    --new-only --for-tsubaki --server "${SERVER}" --quiet

  python3 "${RUN_DIR}/PADIconGenerator.py" \
    --input_dir="${FILE_DIR}/cards" \
    --data_dir="${RAW_DIR}" \
    --card_templates_file="${RUN_DIR}/attribute_frames.png" \
    --server=${SERVER} \
    --output_dir="${FILE_DIR}/icons"
done

# HQ Images are only in JP
mkdir -p "${IMG_DIR}/jp/hq_portraits"
python3 "${RUN_DIR}/PADHQImageDownload.py" \
  --raw_file_dir="${IMG_DIR}/jp/raw_data" \
  --db_config="${DB_CONFIG}" \
  --output_dir="${IMG_DIR}/jp/hq_portraits"

# Force a sync
${CRONJOBS_DIR}/sync_data.sh
