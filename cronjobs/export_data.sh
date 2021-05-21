#!/bin/bash
set -e
set -x

cd "$(dirname "$0")" || exit
source ./discord.sh
source ./shared.sh

echo "Exporting DG (NO WAVES) to sqlite"
DADGUIDE_DB_FILE=${DADGUIDE_GAME_DB_DIR}/dadguide.sqlite
DADGUIDE_DB_FILE_TMP=${DADGUIDE_DB_FILE}_tmp
rm -f "${DADGUIDE_DB_FILE_TMP}"
${SCHEMA_TOOLS_DIR}/mysql2sqlite.sh \
  -u ${MYSQL_USER} \
  -p${MYSQL_PASSWORD} \
  dadguide \
  --skip-triggers \
  --ignore-table=dadguide.wave_data |
  sqlite3 "${DADGUIDE_DB_FILE_TMP}"
mv "${DADGUIDE_DB_FILE_TMP}" "${DADGUIDE_DB_FILE}"

echo "Zipping/copying DB dump"
DADGUIDE_ZIP_DB_FILE="${DADGUIDE_GAME_DB_DIR}/v2_dadguide.sqlite.zip"
DADGUIDE_ZIP_DB_FILE_TMP="${DADGUIDE_ZIP_DB_FILE}_tmp"
rm -f "${DADGUIDE_ZIP_DB_FILE_TMP}"
zip -j "${DADGUIDE_ZIP_DB_FILE_TMP}" "${DADGUIDE_DB_FILE}"
mv "${DADGUIDE_ZIP_DB_FILE_TMP}" "${DADGUIDE_ZIP_DB_FILE}"

echo "Exporting DG (NO WAVES) to mysql"
DADGUIDE_MYSQL_FILE=${DADGUIDE_GAME_DB_DIR}/dadguide.mysql
DADGUIDE_MYSQL_ZIP_FILE=${DADGUIDE_GAME_DB_DIR}/dadguide.mysql.zip
rm -f "${DADGUIDE_MYSQL_FILE}" "${DADGUIDE_MYSQL_ZIP_FILE}"
mysqldump --default-character-set=utf8 \
  -u ${MYSQL_USER} \
  -p${MYSQL_PASSWORD} \
  dadguide \
  --ignore-table=dadguide.wave_data \
  >"${DADGUIDE_MYSQL_FILE}"
zip -j "${DADGUIDE_MYSQL_ZIP_FILE}" "${DADGUIDE_MYSQL_FILE}"

echo "Exporting zipped full DG+WAVES to mysql"
DADGUIDE_MYSQL_WAVE_DATA_FILE=/tmp/dadguide_wave_data.mysql
DADGUIDE_MYSQL_WAVE_DATA_ZIP_FILE=${DADGUIDE_GAME_DB_DIR}/dadguide_wave_data.mysql.zip
rm -f "${DADGUIDE_MYSQL_WAVE_DATA_FILE}" "${DADGUIDE_MYSQL_WAVE_DATA_ZIP_FILE}"
mysqldump --default-character-set=utf8 \
  -u ${MYSQL_USER} \
  -p${MYSQL_PASSWORD} \
  dadguide \
  >"${DADGUIDE_MYSQL_WAVE_DATA_FILE}"
zip -j "${DADGUIDE_MYSQL_WAVE_DATA_ZIP_FILE}" "${DADGUIDE_MYSQL_WAVE_DATA_FILE}"
rm -f "${DADGUIDE_MYSQL_WAVE_DATA_FILE}"

echo "Exporting zipped full DG+WAVES to sqlite"
DADGUIDE_WAVE_DATA_FILE=/tmp/dadguide_wave_data.sqlite
DADGUIDE_WAVE_DATA_ZIP_FILE=${DADGUIDE_GAME_DB_DIR}/dadguide_wave_data.sqlite.zip
rm -f "${DADGUIDE_WAVE_DATA_FILE}" "${DADGUIDE_WAVE_DATA_ZIP_FILE}"
${SCHEMA_TOOLS_DIR}/mysql2sqlite.sh \
  -u ${MYSQL_USER} \
  -p${MYSQL_PASSWORD} \
  dadguide \
  --skip-triggers |
  sqlite3 "${DADGUIDE_WAVE_DATA_FILE}"
zip -j "${DADGUIDE_WAVE_DATA_ZIP_FILE}" "${DADGUIDE_WAVE_DATA_FILE}"
rm -f "${DADGUIDE_WAVE_DATA_FILE}"

echo "Creating icon zip"
rm -f /tmp/icons.zip
# Spammy command
set +x
(cd "${DADGUIDE_MEDIA_DIR}" && zip -q -r -0 - icons/*.png awakenings/*.png latents/*/*.png types/*.png badges/*.png) >/tmp/icons.zip
set -x
mv /tmp/icons.zip "${DADGUIDE_GAME_DB_DIR}/icons.zip"

echo "{\"last_edited\": $(date +%s)}" >${DADGUIDE_GAME_DB_DIR}/version.json
