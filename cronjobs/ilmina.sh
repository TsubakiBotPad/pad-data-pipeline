#!/bin/bash
set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared.sh

cp -r ${RAW_DIR}/na/. $DADGUIDE_ILMINA_DIR
