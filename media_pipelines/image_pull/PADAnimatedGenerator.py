import argparse
import os
import tempfile

from PIL import Image

parser = argparse.ArgumentParser(
    description="Generates static frames for animated images.", add_help=False)

inputGroup = parser.add_argument_group("Input")
inputGroup.add_argument("--raw_dir", required=True, help="Path to input BC files")
inputGroup.add_argument("--working_dir", required=True, help="Path to pad-resources project")

outputGroup = parser.add_argument_group("Output")
outputGroup.add_argument("--output_dir", required=True,
                         help="Path to a folder where output should be saved")

helpGroup = parser.add_argument_group("Help")
helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()

# The final padded image size (matches the rest of the miru images)
IMAGE_SIZE = (640, 388)

# The maximum size of the monster to be positioned within the image
IMAGE_SIZE_NO_PADDING = (640 - 70 * 2, 388 - 35 * 2)


def blacken_image(image):
    pixel_data = image.load()
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            # Check if it's completely transparent
            if pixel_data[x, y][3] == 0:
                # Set the color to black
                pixel_data[x, y] = (0, 0, 0, 0)


def generate_resized_image(source_file, dest_file):
    # Resizes the image so it has the correct padding
    img = Image.open(source_file)

    # Ensure RGBA
    img = img.convert('RGBA')

    # Blacken any fully-transparent pixels
    blacken_image(img)

    # Trim transparent edges
    img = img.crop(img.getbbox())

    max_size = IMAGE_SIZE_NO_PADDING[0] if img.size[0] > img.size[1] else IMAGE_SIZE_NO_PADDING[1]
    img.thumbnail((max_size, max_size), Image.ANTIALIAS)

    old_size = img.size

    new_img = Image.new("RGBA", IMAGE_SIZE)
    new_img.paste(img,
                  (int((IMAGE_SIZE[0] - old_size[0]) / 2),
                   int((IMAGE_SIZE[1] - old_size[1]) / 2)))

    new_img.save(dest_file)


def process_animated(working_dir, pad_id, file_path):
    bin_file = 'mons_{}.bin'.format(pad_id)
    bin_path = os.path.join('data', 'HT', 'bin', bin_file)
    xvfb_prefix = 'xvfb-run -s "-ac -screen 0 640x640x24"'
    yarn_cmd = 'yarn --cwd={} render --bin {} --out {} --nobg'.format(
        working_dir, bin_path, file_path)

    full_cmd = '{} {}'.format(xvfb_prefix, yarn_cmd)
    print('running', full_cmd)
    os.system(full_cmd)
    print('done')


raw_dir = args.raw_dir
working_dir = args.working_dir
output_dir = args.output_dir

for file_name in sorted(os.listdir(raw_dir)):
    if 'mons' not in file_name or 'isanimated' in file_name:
        print('skipping', file_name)
        continue

    pad_id = file_name.rstrip('.bc').lstrip('mons_').lstrip('0')
    final_image_name = '{}.png'.format(pad_id)
    corrected_file_path = os.path.join(output_dir, final_image_name)

    if os.path.exists(corrected_file_path):
        print('skipping', corrected_file_path)
        continue

    print('processing', corrected_file_path)
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            tmp_corrected_file_path = os.path.join(temp_dir, final_image_name)
            process_animated(working_dir, pad_id, tmp_corrected_file_path)
            generate_resized_image(tmp_corrected_file_path, corrected_file_path)
        except:
            print('error skipping', corrected_file_path)
            continue

print('done')
