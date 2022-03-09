#!/usr/bin/env bash
set -e
set -x

cd "$(dirname "$0")" || exit
source ./shared_root.sh
source ./shared.sh
source ./discord.sh

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
DADGUIDE_ZIP_DB_FILE="${DADGUIDE_GAME_DB_DIR}/dadguide.sqlite.zip"
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

echo "{\"last_edited\": $(date +%s)}" >${DADGUIDE_GAME_DB_DIR}/version.json
