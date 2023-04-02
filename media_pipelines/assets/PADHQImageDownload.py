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
bin_dir = args.raw_file_dir
output_dir = args.output_dir

GUNGHO_TEMPLATE = 'https://pad.gungho.jp/member/img/graphic/illust/{}'
HTTP_SEMAPHORE = asyncio.Semaphore(10)


async def download_file(url, file_path, monster_id, cursor):
    async with HTTP_SEMAPHORE:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=False) as response:
                if response.status == 302:
                    return
                if response.status != 200:
                    print(f"Invalid response code {response.status} for {monster_id}")
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

    for file_name in sorted(os.listdir(bin_dir)):
        if not (match := re.match(r'mons_0*(\d+).bin', file_name)):
            continue

        monster_id = int(match.group(1))
        final_image_name = f'{monster_id:05d}.png'
        corrected_file_path = os.path.join(output_dir, final_image_name)

        if os.path.exists(corrected_file_path):
            continue

        gungho_url = GUNGHO_TEMPLATE.format(monster_id)

        try:
            file_downloads.append(download_file(gungho_url, corrected_file_path, int(monster_id), cur))
        except Exception as e:
            print('Failed to download: ', e)

    await asyncio.gather(*file_downloads)

    cur.close()
    db.close()
    print('done')


if __name__ == "__main__":
    asyncio.run(main())
