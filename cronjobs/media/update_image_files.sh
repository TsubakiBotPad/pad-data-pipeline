#!/usr/bin/env bash
#
# Updates the local cache of full monster pics / portraits from the JP server.

cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh
source ../discord.sh
source "${VENV_ROOT}/bin/activate"

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

# Portraits
for server in na jp; do
  python3 "${RUN_DIR}/PADTextureDownload.py" \
    --animated_dir="${IMG_DIR}/animated" \
    --output_dir="${IMG_DIR}/${server}/portrait" \
    --server=${server}

  python3 "${RUN_DIR}/PADIconGenerator.py" \
    --input_dir="${IMG_DIR}/${server}/portrait/extract_data" \
    --data_dir="${RAW_DIR}" \
    --card_templates_file="${RUN_DIR}/attribute_frames.png" \
    --server=${server} \
    --output_dir="${IMG_DIR}/${server}/icon/local"
done

# Animations
flock -xn /tmp/animation.lck "${CRONJOBS_DIR}/media/update_animation_files.sh"

# HQ Images
python3 "${RUN_DIR}/PADHQImageDownload.py" \
  --raw_file_dir="${IMG_DIR}/jp/portrait/raw_data" \
  --db_config="${DB_CONFIG}" \
  --output_dir="${IMG_DIR}/hq_images"

# Force a sync
${CRONJOBS_DIR}/sync_data.sh
