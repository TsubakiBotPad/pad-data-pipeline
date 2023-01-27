import argparse
import os
import re
import time
import urllib.request

import padtools

parser = argparse.ArgumentParser(description="Downloads PAD BGM", add_help=False)

input_group = parser.add_argument_group("Input")
input_group.add_argument("--server", required=True, help="na or jp")
input_group.add_argument("--db_config", help="JSON database info")

output_group = parser.add_argument_group("Output")
output_group.add_argument("--extra_dir", help="Path to a folder where raw extras should be saved")
output_group.add_argument("--final_dir", help="Path to a folder where output should be saved")

settings_group = parser.add_argument_group("Settings")
settings_group.add_argument("--refresh", action="store_true", help="Refresh downloaded data")

help_group = parser.add_argument_group("Help")
help_group.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()

server = args.server.lower()

extras = []
if server == 'na':
    extras = padtools.regions.north_america.server.extras  # noqa
elif server == 'jp':
    extras = padtools.regions.japan.server.extras  # noqa
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
for extra in extras:
    file_name = extra.file_name
    if not (match := re.match(r'bgm_0*(\d+)\.caf', file_name)):
        print('skipping', file_name)
        continue

    in_file = os.path.join(raw_dir, file_name)
    if not refresh and os.path.exists(in_file):
        print('file exists', in_file)
        continue

    print('downloading', extra.url, 'to', in_file)
    download_file(extra.url, in_file)

    bgm_id = match.group(1)

    out_file = os.path.join(fixed_dir, '{}.mp3'.format(file_name.rstrip('.caf')))
    cmd = 'ffmpeg -i {} -hide_banner -loglevel warning -nostats -y -ac 1 {}'.format(in_file, out_file)
    print('running', cmd)
    out = os.system(cmd)
    if out != 0:
        print(out)
    time.sleep(.1)

print('done')
