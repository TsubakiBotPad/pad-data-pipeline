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
source ./discord.sh
source ./shared.sh

echo "Copying media"
python3 "${ETL_DIR}/media_copy.py" \
  --base_dir=/home/tactical0retreat/image_data \
  --output_dir="${DADGUIDE_MEDIA_DIR}"

# Spammy commands
echo "Rsyncing from repo to images dir"
set +x
rsync -t "${ETL_IMAGES_DIR}"/latents/*    "${DADGUIDE_MEDIA_DIR}/latents"
rsync -t "${ETL_IMAGES_DIR}"/awakenings/* "${DADGUIDE_MEDIA_DIR}/awakenings"
rsync -t "${ETL_IMAGES_DIR}"/badges/* "${DADGUIDE_MEDIA_DIR}/badges"
rsync -t "${ETL_IMAGES_DIR}"/types/*      "${DADGUIDE_MEDIA_DIR}/types"
rsync -t "${ETL_IMAGES_DIR}"/icons/*      "${DADGUIDE_MEDIA_DIR}/icons"
set -x

echo "Syncing raw data to GCS"
gsutil -m rsync -r -c /home/tactical0retreat/pad_data/raw gs://mirubot-data/paddata/raw

echo "Syncing db, media, and extra data to B2"
b2 sync --compareVersions size "${DADGUIDE_GAME_DB_DIR}" b2://dadguide-data/db
b2 sync --compareVersions size "${DADGUIDE_MEDIA_DIR}" b2://dadguide-data/media
b2 sync --compareVersions size "${DADGUIDE_EXTRA_DIR}" b2://dadguide-data/extra

# Temporary for padspike
b2 sync --compareVersions size "${DADGUIDE_DATA_DIR}/processed" b2://dadguide-data/processed
