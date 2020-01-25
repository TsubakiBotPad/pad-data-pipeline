import argparse
import json
import os
import re
import sys
import urllib.request

from collections import defaultdict

import padtools

parser = argparse.ArgumentParser(
    description="Downloads P&D story files (and decodes them)", add_help=False)

inputGroup = parser.add_argument_group("Input")
inputGroup.add_argument("--server", required=True, help="na or jp")
inputGroup.add_argument("--data_dir", required=True, help="Path to processed pad data files")
inputGroup.add_argument("--tool_dir", required=True, help="Path to decoder tool")

outputGroup = parser.add_argument_group("Output")
outputGroup.add_argument("--output_dir", help="Path to a folder where output should be saved")

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


def decode_file(in_file, out_file):
    cmd = 'python3 {}/PADTextureTool.py {} --outfile {}'.format(args.tool_dir, in_file, out_file)
    print('running', cmd)
    os.system(cmd)

def decode_image(in_file, out_dir):
    cmd = 'python3 {}/PADTextureTool.py {} --outdir {}'.format(args.tool_dir, in_file, out_dir)
    print('running', cmd)
    os.system(cmd)


print('Found', len(extras), 'extras total')

raw_dir = os.path.join(output_dir, 'raw')
fixed_dir = os.path.join(output_dir, 'fixed')

raw_dir = os.path.join(raw_dir, server)
fixed_dir = os.path.join(fixed_dir, server)

raw_text_dir = os.path.join(raw_dir, 'text')
raw_image_dir = os.path.join(raw_dir, 'image')

fixed_text_dir = os.path.join(fixed_dir, 'text')
fixed_image_dir = os.path.join(fixed_dir, 'image')

os.makedirs(raw_image_dir, exist_ok=True)
os.makedirs(raw_text_dir, exist_ok=True)
os.makedirs(fixed_image_dir, exist_ok=True)
os.makedirs(fixed_text_dir, exist_ok=True)


for extra in extras:
    raw_file_name = extra.file_name
    if raw_file_name.startswith('st_') and raw_file_name.endswith('.txt'):
        raw_file_path = os.path.join(raw_text_dir, raw_file_name)
        fixed_file_path = os.path.join(fixed_text_dir, raw_file_name)
        fixed_file_dir = fixed_text_dir
        do_decode_file = True
    elif raw_file_name.startswith('st_mons') and raw_file_name.endswith('.bin'):
        raw_file_path = os.path.join(raw_image_dir, raw_file_name)
        fixed_file_path = os.path.join(fixed_image_dir, raw_file_name)
        fixed_file_dir = fixed_image_dir
        do_decode_file = False
    else:
        print('skipping', raw_file_name)
        continue

    if not os.path.exists(raw_file_path):
        print('downloading', extra.url, 'to', raw_file_path)
        download_file(extra.url, raw_file_path)
    else:
        print('raw file exists', raw_file_path)

    if not os.path.exists(fixed_file_path):
        print('decoding', raw_file_path, 'to', fixed_file_path)
        if do_decode_file:
            decode_file(raw_file_path, fixed_file_path)
        else:
            decode_image(raw_file_path, fixed_file_dir)
    else:
        print('fixed file exists', fixed_file_path)
    

print('done')
