#!/bin/bash
#
# Updates the local cache of full monster pics / portraits from the JP server.

cd "$(dirname "$0")" || exit
source /home/bot/pad-data-pipeline/bin/activate
source ../shared.sh

RUN_DIR="${MEDIA_ETL_DIR}/image_pull"

yarn --cwd=${PAD_RESOURCES_ROOT} update

# Full pictures
python3 "${RUN_DIR}/PADTextureDownload.py" \
  --output_dir="${IMG_DIR}/na/full" \
  --server=NA

python3 "${RUN_DIR}/PADAnimatedGenerator.py" \
  --raw_dir="${IMG_DIR}/na/full/raw_data" \
  --working_dir="${PAD_RESOURCES_ROOT}" \
  --output_dir="${IMG_DIR}/na/full/corrected_data"

python3 "${RUN_DIR}/PADTextureDownload.py" \
  --output_dir="${IMG_DIR}/jp/full" \
  --server=JP

python3 "${RUN_DIR}/PADAnimatedGenerator.py" \
  --raw_dir="${IMG_DIR}/jp/full/raw_data" \
  --working_dir="${PAD_RESOURCES_ROOT}" \
  --output_dir="${IMG_DIR}/jp/full/corrected_data"

# Portraits
python3 ${RUN_DIR}/PADPortraitsGenerator.py \
  --input_dir="${IMG_DIR}/na/full/extract_data" \
  --data_dir="${RAW_DIR}" \
  --card_templates_file="${RUN_DIR}/wide_cards.png" \
  --server=na \
  --output_dir="${IMG_DIR}/na/portrait/local"

python3 ${RUN_DIR}/PADPortraitsGenerator.py \
  --input_dir="${IMG_DIR}/jp/full/extract_data" \
  --data_dir="${RAW_DIR}" \
  --card_templates_file="${RUN_DIR}/wide_cards.png" \
  --server=jp \
  --output_dir="${IMG_DIR}/jp/portrait/local"

# Animations
python3 "${RUN_DIR}/PADAnimationGenerator.py" \
  --raw_dir="${IMG_DIR}/jp/full/raw_data" \
  --working_dir="${PAD_RESOURCES_ROOT}" \
  --output_dir="${IMG_DIR}/animated"

# Force a sync
../sync_data.sh
