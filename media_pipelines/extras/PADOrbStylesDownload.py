import argparse
import os
import shutil
import sys
import urllib.request

import padtools
from PIL import Image

parser = argparse.ArgumentParser(
    description="Downloads P&D Orb Styles (alternate skins)", add_help=False)

inputGroup = parser.add_argument_group("Input")
inputGroup.add_argument("--server", required=True, help="na or jp")

outputGroup = parser.add_argument_group("Output")
inputGroup.add_argument("--cache_dir", required=True, help="Path to a folder where output should be saved")
outputGroup.add_argument("--output_dir", required=True, help="Path to a folder where output should be saved")

helpGroup = parser.add_argument_group("Help")
helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()

server = args.server.lower()
cache_dir = args.cache_dir
output_dir = args.output_dir

extras = []
if args.server == 'na':
    extras = padtools.regions.north_america.server.extras
elif args.server == 'jp':
    extras = padtools.regions.japan.server.extras


def download_file(url, file_path):
    response_object = urllib.request.urlopen(url)
    with response_object as response:
        file_data = response.read()
        with open(file_path, "wb") as f:
            f.write(file_data)


print('Found', len(extras), 'extras total')

cache_dir = os.path.join(cache_dir, server)
cache_raw_dir = os.path.join(cache_dir, 'raw')
cache_extract_dir = os.path.join(cache_dir, 'extract')
output_dir = os.path.join(output_dir, server)
os.makedirs(cache_raw_dir, exist_ok=True)
os.makedirs(cache_extract_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

python_exec = sys.executable
cur_file_path = os.path.dirname(os.path.realpath(__file__))
tool_path = os.path.join(cur_file_path, '..', 'assets', 'PADTextureTool.py')

should_always_process = False

for extra in extras:
    raw_file_name = extra.file_name
    if not raw_file_name.startswith('block') or not raw_file_name.endswith('.btex'):
        continue

    raw_file_path = os.path.join(cache_raw_dir, raw_file_name)
    if os.path.exists(raw_file_path) and not should_always_process:
        print('file exists', raw_file_path)
    else:
        print('downloading', extra.url, 'to', raw_file_path)
        download_file(extra.url, raw_file_path)

    extract_file_name = raw_file_name.upper().replace('BTEX', 'PNG')
    extract_file_path = os.path.join(cache_extract_dir, extract_file_name)

    if os.path.exists(extract_file_path) and not should_always_process:
        print('skipping existing file', extract_file_path)
    else:
        print('processing', raw_file_path, 'to', cache_extract_dir, 'with name', extract_file_name)
        os.system('{python} {tool} -o={output} {input}'.format(
            python=python_exec,
            tool=tool_path,
            input=raw_file_path,
            output=cache_extract_dir))

    final_file_name = extract_file_name.replace('BLOCK', '').lower()
    final_file_path = os.path.join(output_dir, final_file_name)

    if os.path.exists(final_file_path) and not should_always_process:
        print('skipping existing file', final_file_path)
    else:
        print('copying', extract_file_path, 'to', final_file_path)
        shutil.copy2(extract_file_path, final_file_path)

        img = Image.open(final_file_path)
        orb_width, spacer = 100, 4

        x, y = 0, 0
        orb_path = final_file_path.replace('.png', '_00.png')
        img.crop(box=(x, y, x + orb_width, y + orb_width)).save(orb_path)

        x += orb_width + spacer
        orb_path = final_file_path.replace('.png', '_01.png')
        img.crop(box=(x, y, x + orb_width, y + orb_width)).save(orb_path)

        x += orb_width + spacer
        orb_path = final_file_path.replace('.png', '_02.png')
        img.crop(box=(x, y, x + orb_width, y + orb_width)).save(orb_path)

        x += orb_width + spacer
        orb_path = final_file_path.replace('.png', '_03.png')
        img.crop(box=(x, y, x + orb_width, y + orb_width)).save(orb_path)

        y += orb_width + spacer
        x = 0
        orb_path = final_file_path.replace('.png', '_04.png')
        img.crop(box=(x, y, x + orb_width, y + orb_width)).save(orb_path)

print('done')
