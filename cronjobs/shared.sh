#!/bin/bash

set -e
set -x

declare -rx PAD_DATA_DIR="/home/tactical0retreat/pad_data"
declare -rx RAW_DIR="/home/tactical0retreat/pad_data/raw"
# This probably needs to move into pad_data.
declare -rx IMG_DIR="/home/tactical0retreat/image_data"

declare -rx ETL_DIR="/home/tactical0retreat/dadguide/dadguide-data/etl"
declare -rx MEDIA_ETL_DIR="/home/tactical0retreat/dadguide/dadguide-data/media_pipelines"
declare -rx UTILS_ETL_DIR="/home/tactical0retreat/dadguide/dadguide-data/utils"

declare -rx DADGUIDE_DATA_DIR="/home/tactical0retreat/dadguide/data"
declare -rx DADGUIDE_PROCESSED_DATA_DIR="/home/tactical0retreat/dadguide/data/processed"
declare -rx DADGUIDE_MEDIA_DIR="/home/tactical0retreat/dadguide/data/media"
declare -rx DADGUIDE_EXTRA_DIR="/home/tactical0retreat/dadguide/data/extra"
declare -rx DADGUIDE_GAME_DB_DIR="/home/tactical0retreat/dadguide/data/db"
declare -rx GAME_DATA_DIR="/home/tactical0retreat/dadguide/pad-game-data-slim"

declare -rx DB_CONFIG="/home/tactical0retreat/dadguide/dadguide-jobs/db_config.json"
declare -rx ACCOUNT_CONFIG="/home/tactical0retreat/dadguide/dadguide-jobs/account_config.csv"

declare -rx SCHEMA_TOOLS_DIR="/home/tactical0retreat/dadguide/dadguide-data/schema"
declare -rx ETL_IMAGES_DIR="/home/tactical0retreat/dadguide/dadguide-data/images"
declare -rx ES_DIR="/home/tactical0retreat/dadguide/pad-game-data-slim/behavior_data"

export PYTHONPATH="${ETL_DIR}"
