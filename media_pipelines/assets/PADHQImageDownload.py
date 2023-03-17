import argparse
import json
import os
import re

import pymysql
import requests

parser = argparse.ArgumentParser(
    description="Downloads P&D images from the GungHo site.", add_help=False)

input_group = parser.add_argument_group("Input")
input_group.add_argument("--raw_file_dir", help="Path to input BC files")
input_group.add_argument("--db_config", help="JSON database info")

outputGroup = parser.add_argument_group("Output")
outputGroup.add_argument("--output_dir", help="Path to a folder where output should be saved")

helpGroup = parser.add_argument_group("Help")
helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()
raw_dir = args.raw_file_dir
corrected_dir = args.output_dir

GUNGHO_TEMPLATE = 'https://pad.gungho.jp/member/img/graphic/illust/{}'


def download_file(url, file_path):
    r = requests.get(url, allow_redirects=False)
    if r.status_code == 302:
        raise Exception("No HQ Image")
    if r.status_code != 200:
        raise Exception('Bad status code:', r.status_code)

    with open(file_path, "wb") as f:
        f.write(r.content)

    return len(r.content)

with open(args.db_config) as f:
    db_config = json.load(f)

db = pymysql.connect(**db_config, autocommit=True)
cur = db.cursor()

for file_name in sorted(os.listdir(raw_dir)):
    if not (match := re.match(r'mons_0*(\d+).bin', file_name)):
        print('skipping', file_name)
        continue

    pad_id = match.group(1)
    final_image_name = '{}.png'.format(pad_id.zfill(5))
    corrected_file_path = os.path.join(corrected_dir, final_image_name)

    if os.path.exists(corrected_file_path):
        print('skipping', corrected_file_path)
        continue

    print('processing', corrected_file_path)

    gungho_url = GUNGHO_TEMPLATE.format(pad_id)

    try:
        size = download_file(gungho_url, corrected_file_path)
    except Exception as e:
        print('Failed to download: ', e)
    else:
        cur.execute('''INSERT INTO monster_image_sizes (monster_id, hq_png_size, tstamp) 
                       VALUES (%s, %s, UNIX_TIMESTAMP()) 
                       ON DUPLICATE KEY 
                       UPDATE hq_png_size=%s, tstamp=UNIX_TIMESTAMP();''', (int(pad_id), size, size))

cur.close()
db.close()
print('done')
