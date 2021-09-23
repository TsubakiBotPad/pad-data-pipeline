#!/usr/bin/env bash

set -e
set -x

declare -x REPO_ROOT="${PROJECT_ROOT}/pad-data-pipeline"
declare -x PAD_RESOURCES_ROOT="${PROJECT_ROOT}/pad-resources"
declare -x GAME_DATA_DIR="${PROJECT_ROOT}/pad-data-pipeline-export"

declare -x PAD_DATA_DIR="${REPO_ROOT}/pad_data"
declare -x CRONJOBS_DIR="${REPO_ROOT}/cronjobs"
declare -x RAW_DIR="${PAD_DATA_DIR}/raw"
declare -x IMG_DIR="${PAD_DATA_DIR}/image_data"
declare -x VENV_ROOT="${REPO_ROOT}"

declare -x ETL_DIR="${REPO_ROOT}/etl"
declare -x MEDIA_ETL_DIR="${REPO_ROOT}/media_pipelines"
declare -x UTILS_ETL_DIR="${REPO_ROOT}/utils"

declare -x DADGUIDE_DATA_DIR="${REPO_ROOT}/output"
declare -x DADGUIDE_PROCESSED_DATA_DIR="${DADGUIDE_DATA_DIR}/processed"
declare -x DADGUIDE_MEDIA_DIR="${DADGUIDE_DATA_DIR}/media"
declare -x DADGUIDE_EXTRA_DIR="${DADGUIDE_DATA_DIR}/extra"
declare -x DADGUIDE_GAME_DB_DIR="${DADGUIDE_DATA_DIR}/db"
declare -x DADGUIDE_ILMINA_DIR="${DADGUIDE_DATA_DIR}/ilmina"

declare -x DB_CONFIG="${REPO_ROOT}/cronjobs/db_config.json"
declare -x ACCOUNT_CONFIG="${REPO_ROOT}/cronjobs/account_config.csv"
declare -x SECRETS_CONFIG="${REPO_ROOT}/cronjobs/secrets.sh"

declare -x SCHEMA_TOOLS_DIR="${REPO_ROOT}/schema"
declare -x ETL_IMAGES_DIR="${REPO_ROOT}/images"
declare -x ES_DIR="${GAME_DATA_DIR}/behavior_data"

source ${SECRETS_CONFIG}
export PYTHONPATH="${ETL_DIR}"
