#!/usr/bin/env bash

set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared_roots.sh

declare -rx PAD_DATA_DIR="${REPO_ROOT}/pad_data"
declare -rx CRONJOBS_DIR="${REPO_ROOT}/cronjobs"
declare -rx RAW_DIR="${PAD_DATA_DIR}/raw"
declare -rx IMG_DIR="${PAD_DATA_DIR}/image_data"
declare -rx VENV_ROOT="${REPO_ROOT}"

declare -rx ETL_DIR="${REPO_ROOT}/etl"
declare -rx MEDIA_ETL_DIR="${REPO_ROOT}/media_pipelines"
declare -rx UTILS_ETL_DIR="${REPO_ROOT}/utils"

declare -rx DADGUIDE_DATA_DIR="${REPO_ROOT}/output"
declare -rx DADGUIDE_PROCESSED_DATA_DIR="${DADGUIDE_DATA_DIR}/processed"
declare -rx DADGUIDE_MEDIA_DIR="${DADGUIDE_DATA_DIR}/media"
declare -rx DADGUIDE_EXTRA_DIR="${DADGUIDE_DATA_DIR}/extra"
declare -rx DADGUIDE_GAME_DB_DIR="${DADGUIDE_DATA_DIR}/db"
declare -rx DADGUIDE_ILMINA_DIR="${DADGUIDE_DATA_DIR}/ilmina"

declare -rx DB_CONFIG="${REPO_ROOT}/cronjobs/db_config.json"
declare -rx ACCOUNT_CONFIG="${REPO_ROOT}/cronjobs/account_config.csv"
declare -rx SECRETS_CONFIG="${REPO_ROOT}/cronjobs/secrets.sh"

declare -rx SCHEMA_TOOLS_DIR="${REPO_ROOT}/schema"
declare -rx ETL_IMAGES_DIR="${REPO_ROOT}/images"
declare -rx ES_DIR="${GAME_DATA_DIR}/behavior_data"

source ${SECRETS_CONFIG}
export PYTHONPATH="${ETL_DIR}"
