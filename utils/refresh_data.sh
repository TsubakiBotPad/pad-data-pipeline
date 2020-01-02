#!/usr/bin/env bash
cd "$(dirname "$0")"
data_dir=../pad_data
mkdir ${data_dir}
mkdir ${data_dir}/raw
mkdir ${data_dir}/processed
gsutil -m rsync -r -c gs://mirubot-data/paddata/raw ${data_dir}/raw
