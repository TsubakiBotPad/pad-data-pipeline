#!/usr/bin/env bash
data_dir=../pad_data
mkdir ${data_dir}
mkdir ${data_dir}/raw
mkdir ${data_dir}/processed
gsutil -m rsync -r -c gs://mirubot-data/paddata/raw ${data_dir}/raw
gsutil -m rsync -x "(?!^wave_summary.csv$)" gs://mirubot-data/paddata/processed ${data_dir}/processed
gsutil -m rsync -x "(?!^jp_calc_skills.json)" gs://mirubot-data/paddata/processed ${data_dir}/processed
