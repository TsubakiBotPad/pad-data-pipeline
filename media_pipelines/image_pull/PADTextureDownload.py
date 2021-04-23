import argparse
import os
import re
import sys
import urllib.request

from PIL import Image
import padtools


# The 'padtools' package did not work properly out of the box on linux. I had to go in
# and adjust the __init__.py files like so:
#
# OLD: Regions.load(os.path.join(__file__, "..", "data", "regions.json"))
# NEW: Regions.load(os.path.join(os.path.dirname(__file__), "data", "regions.json"))
#
# Did this for padtools/regions/__init__.py and padtools/servers/__init__.py


def getOutputFileName(suggestedFileName):
    outputFileName = suggestedFileName
    # If the file is a "monster file" then pad the ID out with extra zeroes.
    try:
        prefix, mId, suffix = getOutputFileName.monsterFileNameRegex.match(
            suggestedFileName).groups()
        outputFileName = prefix + mId.zfill(5) + suffix
    except AttributeError:
        pass

    return outputFileName


getOutputFileName.monsterFileNameRegex = re.compile(r'^(MONS_)(\d+)(\..+)$', flags=re.IGNORECASE)

parser = argparse.ArgumentParser(description="Downloads and extracts P&D textures.", add_help=False)

outputGroup = parser.add_argument_group("Output")
outputGroup.add_argument("--output_dir", help="Path to a folder where output should be saved")
outputGroup.add_argument("--server", help="One of [NA, JP]")

helpGroup = parser.add_argument_group("Help")
helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()

assets = []
if args.server == 'NA':
    assets = padtools.regions.north_america.server.assets
elif args.server == 'JP':
    assets = padtools.regions.japan.server.assets

output_dir = args.output_dir


def download_file(url, file_path):
    response_object = urllib.request.urlopen(url)
    with response_object as response:
        file_data = response.read()
        with open(file_path, "wb") as f:
            f.write(file_data)


print('Found', len(assets), 'assets total')

raw_dir = os.path.join(output_dir, 'raw_data')
extract_dir = os.path.join(output_dir, 'extract_data')
corrected_dir = os.path.join(output_dir, 'corrected_data')

os.makedirs(raw_dir, exist_ok=True)
os.makedirs(extract_dir, exist_ok=True)
os.makedirs(corrected_dir, exist_ok=True)

python_exec = sys.executable
cur_file_path = os.path.dirname(os.path.realpath(__file__))
tool_path = os.path.join(cur_file_path, 'PADTextureTool.py')

IMAGE_SIZE = (640, 388)

for asset in assets:
    asset_url = asset.url
    raw_file_name = os.path.basename(asset_url)

    if not raw_file_name.endswith('.bc'):
        print('skipping', raw_file_name)
        continue

    raw_file_path = os.path.join(raw_dir, raw_file_name)

    should_always_process = False
    if 'card' in raw_file_path.lower():
        num = int(raw_file_name.rstrip('.bc').lstrip('cards_'))
        if num >= 57:
            # Arbitrary cutoff; all the slots below here have been filled, no need to
            # keep downloading/processing
            should_always_process = True

    if os.path.exists(raw_file_path) and not should_always_process:
        # always redownload card files
        print('file exists', raw_file_path)
    else:
        print('downloading', asset.url, 'to', raw_file_path)
        download_file(asset_url, raw_file_path)

    extract_file_name = getOutputFileName(raw_file_name).upper().replace('BC', 'PNG')
    extract_file_path = os.path.join(extract_dir, extract_file_name)

    if os.path.exists(extract_file_path) and not should_always_process:
        print('skipping existing file', extract_file_path)
    else:
        # Disable trimming for the card files; screws up portrait generation
        no_trim = '-nt' if 'card' in extract_file_name.lower() else ''

        print('processing', raw_file_path, 'to', extract_dir, 'with name', extract_file_name)
        os.system('{python} {tool} {no_trim} -o={output} {input}'.format(
            python=python_exec,
            tool=tool_path,
            no_trim=no_trim,
            input=raw_file_path,
            output=extract_dir))

    corrected_file_name = extract_file_name.lower().strip('mons_').strip('0')
    corrected_file_path = os.path.join(corrected_dir, corrected_file_name)

    if os.path.exists(corrected_file_path):
        print('skipping existing file', corrected_file_path)
    elif not os.path.exists(extract_file_path):
        # Currently this is happening because of the new animated images, they
        # come in parts that are assembled by PAD.
        print('Error, could not find file:', extract_file_path)
    else:
        img = Image.open(extract_file_path)
        if img.size[1] > IMAGE_SIZE[1]:
            # this is a two-part image
            img = img.crop((0, 0, img.size[0], img.size[1] / 2))

        old_size = img.size

        new_img = Image.new("RGBA", IMAGE_SIZE)
        new_img.paste(img,
                      (int((IMAGE_SIZE[0] - old_size[0]) / 2),
                       int((IMAGE_SIZE[1] - old_size[1]) / 2)))

        new_img.save(corrected_file_path)
        print('done saving', corrected_file_path)
