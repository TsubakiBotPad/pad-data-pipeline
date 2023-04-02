import argparse
import asyncio
import json
import os
import re
import aiohttp

import pymysql

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


async def download_file(url, file_path, monster_id, cursor):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, allow_redirects=False) as response:
            if response.status == 302:
                return
            if response.status != 200:
                return
            image_data = await response.content.read()

    with open(file_path, "wb") as f:
        f.write(image_data)

    cursor.execute('''INSERT INTO monster_image_sizes (monster_id, hq_png_size, tstamp) 
                               VALUES (%s, %s, UNIX_TIMESTAMP()) 
                               ON DUPLICATE KEY 
                               UPDATE hq_png_size=%s, tstamp=UNIX_TIMESTAMP();''',
                   (monster_id, len(image_data), len(image_data)))
    print("finished downloading monster", monster_id)


async def main():
    with open(args.db_config) as f:
        db_config = json.load(f)
        
    db = pymysql.connect(**db_config, autocommit=True)
    cur = db.cursor()
    file_downloads = []

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
            file_downloads.append(download_file(gungho_url, corrected_file_path, int(pad_id), cur))
        except Exception as e:
            print('Failed to download: ', e)

    await asyncio.gather(*file_downloads)

    cur.close()
    db.close()
    print('done')


if __name__ == "__main__":
    asyncio.run(main())

