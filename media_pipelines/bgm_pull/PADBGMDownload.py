import argparse
import os
import time
import urllib.request

import padtools

parser = argparse.ArgumentParser(description="Downloads PAD BGM", add_help=False)

inputGroup = parser.add_argument_group("Input")
inputGroup.add_argument("--server", required=True, help="na or jp")

outputGroup = parser.add_argument_group("Output")
outputGroup.add_argument("--extra_dir", help="Path to a folder where raw extras should be saved")
outputGroup.add_argument("--final_dir", help="Path to a folder where output should be saved")

settingsGroup = parser.add_argument_group("Settings")
settingsGroup.add_argument("--refresh", action="store_true", help="Refresh downloaded data")

helpGroup = parser.add_argument_group("Help")
helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()

server = args.server.lower()

extras = []
if server == 'na':
    extras = padtools.regions.north_america.server.extras
elif server == 'jp':
    extras = padtools.regions.japan.server.extras
else:
    print('invalid server:', server)
    exit(1)


def download_file(url, file_path):
    response_object = urllib.request.urlopen(url)
    with response_object as response:
        file_data = response.read()
        with open(file_path, "wb") as f:
            f.write(file_data)


print('Found', len(extras), 'extras total')

raw_dir = args.extra_dir
fixed_dir = args.final_dir
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(fixed_dir, exist_ok=True)

raw_dir = os.path.join(raw_dir, server)
fixed_dir = os.path.join(fixed_dir, server)
os.makedirs(raw_dir, exist_ok=True)
os.makedirs(fixed_dir, exist_ok=True)

refresh = args.refresh

bgm_files = []
for extra in extras:
    raw_file_name = extra.file_name
    if not raw_file_name.startswith("bgm") or not raw_file_name.endswith('.caf'):
        print('skipping', raw_file_name)
        continue

    bgm_files.append(raw_file_name)
    raw_file_path = os.path.join(raw_dir, raw_file_name)
    if os.path.exists(raw_file_path) and not refresh:
        print('file exists', raw_file_path)
        continue

    print('downloading', extra.url, 'to', raw_file_path)
    download_file(extra.url, raw_file_path)

for file_name in bgm_files:
    in_file = os.path.join(raw_dir, file_name)
    out_file = os.path.join(fixed_dir, '{}.mp3'.format(file_name.rstrip('.caf')))
    cmd = 'ffmpeg -i {} -hide_banner -loglevel warning -nostats -y -ac 1 {}'.format(in_file, out_file)
    print('running', cmd)
    out = os.system(cmd)
    if out != 0:
        print(out)
    time.sleep(.1)

print('done')
