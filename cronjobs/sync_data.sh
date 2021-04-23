#!/bin/bash
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

source ${CRONJOBS_DIR}/discord.sh
source ${CRONJOBS_DIR}/shared.sh

echo "Copying media"
python3 "${ETL_DIR}/media_copy.py" \
  --base_dir="${IMG_DIR}" \
  --output_dir="${DADGUIDE_MEDIA_DIR}"

# Spammy commands
echo "Rsyncing from repo to images dir"
set +x
rsync -t "${ETL_IMAGES_DIR}"/latents/* "${DADGUIDE_MEDIA_DIR}/latents"
rsync -t "${ETL_IMAGES_DIR}"/awakenings/* "${DADGUIDE_MEDIA_DIR}/awakenings"
rsync -t "${ETL_IMAGES_DIR}"/badges/* "${DADGUIDE_MEDIA_DIR}/badges"
rsync -t "${ETL_IMAGES_DIR}"/types/* "${DADGUIDE_MEDIA_DIR}/types"
rsync -t "${ETL_IMAGES_DIR}"/icons/* "${DADGUIDE_MEDIA_DIR}/icons"
set -x

echo "Syncing raw data to AWS s3"
aws s3 sync --acl=private ${DADGUIDE_DATA_DIR} s3://tsubakibot-pad
aws s3 sync --acl=private ${IMG_DIR} s3://tsubakibot-pad/padimages
