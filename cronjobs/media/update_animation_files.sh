#!/usr/bin/env bash
#
# Updates the local cache of full monster pics / portraits from the JP server.

cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh
source ../discord.sh

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

set +x
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 16
set -x

# Animations
yarn --cwd=${PAD_RESOURCES_ROOT} update "${PAD_RESOURCES_ROOT}/data/bin" \
  --for-tsubaki --new-only
yarn --cwd=${PAD_RESOURCES_ROOT} extract "${PAD_RESOURCES_ROOT}/data/bin" "${IMG_DIR}/spine" \
  --animated-only --for-tsubaki --new-only
xvfb-run -s "-ac -screen 0 640x388x24" \
  yarn --cwd=${PAD_RESOURCES_ROOT} render "${IMG_DIR}/spine" "${IMG_DIR}/jp/portrait/local" \
  --single --for-tsubaki # --new-only
xvfb-run -s "-ac -screen 0 640x388x24" \
  yarn --cwd=${PAD_RESOURCES_ROOT} render "${IMG_DIR}/spine" "${IMG_DIR}/animated" \
  --for-tsubaki --new-only

# Force a sync
${CRONJOBS_DIR}/sync_data.sh
