#!/usr/bin/env bash
#
# Copies the portraits/icons from the cache into the DadGuide image dir using
# the DadGuide ID space.
#
# Copies the awakenings, latents, and type icons out of the dadguide-data git
# repo into the DadGuide image dir.
#
# Finally, syncs the raw data files up to GCS, and the DadGuide data into B2.

set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared_root.sh
source ./shared.sh
source ./discord.sh

echo "Copying media"
python3 "${ETL_DIR}/media_copy.py" \
  --base_dir="${IMG_DIR}" \
  --output_dir="${DADGUIDE_MEDIA_DIR}"

# Spammy commands
echo "Rsyncing from repo to images dir"
set +x
rsync -tr "${ETL_IMAGES_DIR}"/latents/* "${DADGUIDE_MEDIA_DIR}/latents"
rsync -tr "${ETL_IMAGES_DIR}"/awakenings/* "${DADGUIDE_MEDIA_DIR}/awakenings"
rsync -tr "${ETL_IMAGES_DIR}"/badges/* "${DADGUIDE_MEDIA_DIR}/badges"
rsync -tr "${ETL_IMAGES_DIR}"/types/* "${DADGUIDE_MEDIA_DIR}/types"
rsync -tr "${ETL_IMAGES_DIR}"/icons/* "${DADGUIDE_MEDIA_DIR}/icons"
rsync -tr "${PAD_DATA_DIR}"/raw/* "${DADGUIDE_RAW_DIR}"
set -x

echo "Syncing raw data to AWS s3"
aws s3 sync --acl=private ${DADGUIDE_DATA_DIR} s3://tsubakibotpad
