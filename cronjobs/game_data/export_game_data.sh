#!/usr/bin/env bash

cd "$(dirname "$0")" || exit
source ../shared_root.sh
source ../shared.sh
source ../discord.sh

echo "Exporting Enemy Skills"
./export_enemy_skills.sh

echo "Exporting PAD Assets"
./export_pad_assets.sh

echo "Writing PAD Data"  # This doesn't export for some reason?  TODO: Find out why.
./export_pad_data.sh

hook_info "Game data export finished"
