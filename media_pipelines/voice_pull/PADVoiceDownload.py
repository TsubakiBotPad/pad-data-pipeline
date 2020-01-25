import argparse
import json
import os
import shutil
import urllib.request
from collections import defaultdict

import padtools

parser = argparse.ArgumentParser(
    description="Downloads P&D voices (and fixed them)", add_help=False)

inputGroup = parser.add_argument_group("Input")
inputGroup.add_argument("--server", required=True, help="na or jp")
inputGroup.add_argument("--data_dir", required=True, help="Path to processed pad data files")

outputGroup = parser.add_argument_group("Output")
outputGroup.add_argument("--output_dir", help="Path to a folder where output should be saved")
outputGroup.add_argument("--final_dir", help="Path to a folder where fixed output should be saved")

helpGroup = parser.add_argument_group("Help")
helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()

server = args.server.lower()

extras = []
if args.server == 'na':
    extras = padtools.regions.north_america.server.extras
elif args.server == 'jp':
    extras = padtools.regions.japan.server.extras

output_dir = args.output_dir


def download_file(url, file_path):
    response_object = urllib.request.urlopen(url)
    with response_object as response:
        file_data = response.read()
        with open(file_path, "wb") as f:
            f.write(file_data)


print('Found', len(extras), 'extras total')

raw_dir = os.path.join(output_dir, 'raw')
fixed_dir = os.path.join(output_dir, 'fixed')
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(fixed_dir, exist_ok=True)

raw_dir = os.path.join(raw_dir, server)
fixed_dir = os.path.join(fixed_dir, server)
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(fixed_dir, exist_ok=True)

for extra in extras:
    raw_file_name = extra.file_name
    if not raw_file_name.startswith('padv') or not raw_file_name.endswith('.wav'):
        print('skipping', raw_file_name)
        continue

    raw_file_path = os.path.join(raw_dir, raw_file_name)
    if os.path.exists(raw_file_path):
        print('file exists', raw_file_path)
        continue

    print('downloading', extra.url, 'to', raw_file_path)
    download_file(extra.url, raw_file_path)

data_file_path = os.path.join(args.data_dir, '{}_raw_cards.json'.format(server))
with open(data_file_path) as f:
    card_data = json.load(f)

voice_id_to_card_id = defaultdict(set)
for c in card_data:
    voice_id = c['voice_id']
    if voice_id:
        voice_id_to_card_id[voice_id].add(c['card_id'])

for file_name in os.listdir(raw_dir):
    file_id = int(file_name.lstrip('padv').lstrip('0').rstrip('.wav'))
    if file_id not in voice_id_to_card_id:
        print('skipping non-card file', file_name)
        continue
    in_file = os.path.join(raw_dir, file_name)
    for card_id in voice_id_to_card_id[file_id]:
        out_file = os.path.join(fixed_dir, '{}.wav'.format(card_id))
        if os.path.exists(out_file):
            continue

        cmd = 'sox -t ima -r 44100 -e ima-adpcm -v .5 {} -e signed-integer -b 16 {}'.format(in_file, out_file)
        print('running', cmd)
        os.system(cmd)

for file_name in os.listdir(fixed_dir):
    in_file = os.path.join(fixed_dir, file_name)

    out_file_name = file_name.zfill(9)  # 5 digits + .wav
    out_file_dir = os.path.join(args.final_dir, server)
    out_file = os.path.join(out_file_dir, out_file_name)
    if os.path.exists(out_file):
        continue
    shutil.copy2(in_file, out_file)

print('done')
