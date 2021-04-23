import argparse
import os

from PIL import Image
import requests

parser = argparse.ArgumentParser(
    description="Downloads P&D images from the GungHo site.", add_help=False)

outputGroup = parser.add_argument_group("Output")
outputGroup.add_argument("--alt_input_dir", help="Optional path to input BC files")
outputGroup.add_argument("--output_dir", help="Path to a folder where output should be saved")

helpGroup = parser.add_argument_group("Help")
helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()

GUNGHO_TEMPLATE = 'https://pad.gungho.jp/member/img/graphic/illust/{}'

# The final padded image size (matches the rest of the miru images)
IMAGE_SIZE = (640, 388)

# The maximum size of the monster to be positioned within the image
IMAGE_SIZE_NO_PADDING = (640 - 70 * 2, 388 - 35 * 2)


def download_file(url, file_path):
    r = requests.get(url, allow_redirects=False)
    if r.status_code != 200:
        raise Exception('Bad status code:', r.status_code)

    with open(file_path, "wb") as f:
        f.write(r.content)


def generate_resized_image(source_file, dest_file):
    # Resizes the image so it has the correct padding
    img = Image.open(source_file)

    # These images are color-indexed, gross
    img = img.convert('RGBA')

    if img.size[0] > img.size[1]:
        max_size = IMAGE_SIZE_NO_PADDING[0] if img.size[0] > img.size[1] else IMAGE_SIZE_NO_PADDING[1]
    img.thumbnail((max_size, max_size), Image.ANTIALIAS)

    old_size = img.size

    new_img = Image.new("RGBA", IMAGE_SIZE)
    new_img.paste(img,
                  (int((IMAGE_SIZE[0] - old_size[0]) / 2),
                   int((IMAGE_SIZE[1] - old_size[1]) / 2)))

    new_img.save(dest_file)


output_dir = args.output_dir

# This mode is used for the version that attempts to download all the artwork
if args.alt_input_dir:
    raw_dir = args.alt_input_dir
    corrected_dir = output_dir
else:
    raw_dir = os.path.join(output_dir, 'raw_data')
    corrected_dir = os.path.join(output_dir, 'corrected_data')

for file_name in os.listdir(raw_dir):
    if 'mons' not in file_name or 'isanimated' in file_name:
        print('skipping', file_name)
        continue

    pad_id = file_name.rstrip('.bc').lstrip('mons_').lstrip('0')
    final_image_name = '{}.png'.format(pad_id)
    corrected_file_path = os.path.join(corrected_dir, final_image_name)

    if os.path.exists(corrected_file_path):
        print('skipping', corrected_file_path)
        continue

    print('processing', corrected_file_path)
    tmp_corrected_file_path = os.path.join(corrected_dir, 'tmp_' + final_image_name)

    try:
        gungho_url = GUNGHO_TEMPLATE.format(pad_id)
        download_file(gungho_url, tmp_corrected_file_path)
        generate_resized_image(tmp_corrected_file_path, corrected_file_path)
    except Exception as e:
        print('failed to download/resize', gungho_url, tmp_corrected_file_path, e)

    if os.path.exists(tmp_corrected_file_path):
        os.remove(tmp_corrected_file_path)

print('done')
