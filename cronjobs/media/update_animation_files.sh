#!/usr/bin/env bash
#
# Updates the local cache of full monster pics / portraits from the JP server.

cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh

set +x
export NVM_DIR="$([ -z "${XDG_CONFIG_HOME-}" ] && printf %s "${HOME}/.nvm" || printf %s "${XDG_CONFIG_HOME}/nvm")"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm use 16
set -x

# Animations
yarn --cwd=${PAD_RESOURCES_ROOT} update "${IMG_DIR}/jp/portrait/raw_data" \
  --for-tsubaki --new-only
yarn --cwd=${PAD_RESOURCES_ROOT} extract "${IMG_DIR}/jp/portrait/raw_data" "${IMG_DIR}/spine" \
  --animated-only --for-tsubaki --new-only
xvfb-run -s "-ac -screen 0 640x388x24" \
  yarn --cwd=${PAD_RESOURCES_ROOT} render "${IMG_DIR}/spine" \
  --animated-dir "${IMG_DIR}/animated" \
  --still-dir "${IMG_DIR}/jp/portrait/corrected_data" \
  --new-only --for-tsubaki
