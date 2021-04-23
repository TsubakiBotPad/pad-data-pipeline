import argparse
import json
import os

from PIL import Image

from pad.raw_processor import merged_database
from pad.common.shared_types import Server

import logging

fail_logger = logging.getLogger('human_fix')
fail_logger.disabled = True

parser = argparse.ArgumentParser(description="Generates P&D portraits.", add_help=False)

inputGroup = parser.add_argument_group("Input")
inputGroup.add_argument("--input_dir", help="Path to a folder where CARD files are")
inputGroup.add_argument("--data_dir", required=True, help="Path to raw pad data files")
inputGroup.add_argument("--server", help="Either na or jp")
inputGroup.add_argument("--card_templates_file", help="Path to card templates png")

outputGroup = parser.add_argument_group("Output")
outputGroup.add_argument("--output_dir", help="Path to a folder where output should be saved")

helpGroup = parser.add_argument_group("Help")
helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()

card_templates_file = args.card_templates_file
output_dir = args.output_dir

templates_img = Image.open(card_templates_file)
attr_imgs = {}
sattr_imgs = {}
for idx, t in enumerate(['r', 'b', 'g', 'l', 'd', 'x']):
    pwidth = 100
    pheight = 100
    xstart = idx * (pwidth + 2)
    ystart = 0

    xend = xstart + pwidth
    yend = ystart + pheight

    attr_imgs[t] = templates_img.crop(box=(xstart, ystart, xend, yend))

    ystart = ystart + pheight + 5
    yend = ystart + pheight - 1 - 1  # Stops one short of full height

    sattr_imgs[t] = templates_img.crop(box=(xstart, ystart, xend, yend))

card_types = []

attr_map = {
    -1: '',
    0: 'r',
    1: 'b',
    2: 'g',
    3: 'l',
    4: 'd',
    6: 'x'
}

server = Server.from_str(args.server)
pad_db = merged_database.Database(server, args.data_dir)
pad_db.load_database(skip_skills=True, skip_extra=True)

for merged_card in pad_db.cards:
    card = merged_card.card
    card_id = card.monster_no
    released = card.released_status

    # Prevent loading junk entries (fake enemies) and also limit to data which has
    # been officially released.
    if card_id > 9999 or not released:
        continue

    card_types.append([
        card_id,
        attr_map[card.attr_id],
        attr_map[card.sub_attr_id]
    ])


def idx_for_id(card_id: int):
    """Computes the (card_file, row, col) for a card."""
    card_id -= 1  # offset to 0
    card_file_idx = int(card_id / 100) + 1

    sub_idx = card_id % 100
    col = sub_idx % 10
    row = int(sub_idx / 10)

    card_file = 'CARDS_{}.PNG'.format(str(card_file_idx).zfill(3))
    return (card_file, row, col)


card_imgs = {}


def get_portraits_img(file_name):
    if file_name not in card_imgs:
        file_path = os.path.join(args.input_dir, file_name)
        if not os.path.exists(file_path):
            return None
        card_imgs[file_name] = Image.open(file_path)
    return card_imgs[file_name]


def get_card_img(portraits, row, col):
    card_dim = 96
    spacer = 6
    xstart = (card_dim + spacer) * col
    ystart = (card_dim + spacer) * row

    xend = xstart + card_dim
    yend = ystart + card_dim
    return portraits.crop(box=(xstart, ystart, xend, yend))


def is_entirely_transparent(img):
    return img.getextrema() == ((0, 0), (0, 0), (0, 0), (0, 0))


for card_id, card_attr, card_sattr in card_types:
    output_file = os.path.join(output_dir, '{}.png'.format(card_id))
    if os.path.exists(output_file):
        continue

    card_file, row, col = idx_for_id(card_id)
    portraits = get_portraits_img(card_file)
    if portraits is None:
        # This can happen since JP gets ahead of NA and it's not easy to
        # confirm that a card is in JP but not NA
        print('skipping {} because CARDS file does not exist: {}'.format(card_id, card_file))
        continue

    card_img = get_card_img(portraits, row, col)
    if is_entirely_transparent(card_img):
        print('skipping {} because it is missing'.format(card_id))
        continue

    # Create a grey image to overlay the portrait on, filling in the background
    grey_img = Image.new("RGBA", card_img.size, color=(68, 68, 68, 255))
    card_img = Image.alpha_composite(grey_img, card_img)

    attr_img = attr_imgs[card_attr]

    # Adjust the card image to fit the portrait
    new_card_img = Image.new("RGBA", attr_img.size)
    new_card_img.paste(card_img, (2, 2))

    # Merge the attribute border on to the portrait
    merged_img = Image.alpha_composite(new_card_img, attr_img)

    if card_sattr:
        sattr_img = sattr_imgs[card_sattr]
        # Adjust the subattribute image to the attribute image size
        new_sattr_img = Image.new("RGBA", attr_img.size)
        # There's a slight offset needed for the subattribute border
        new_sattr_img.paste(sattr_img, (0, 1))

        # Merge the subattribute on top
        merged_img = Image.alpha_composite(merged_img, new_sattr_img)

    # Save
    merged_img.save(os.path.join(output_dir, '{}.png'.format(card_id)), 'PNG')
