import argparse
import logging
import os

from PIL import Image

from pad.common.shared_types import Server
from pad.raw_processor import merged_database

fail_logger = logging.getLogger('human_fix')
fail_logger.disabled = True

parser = argparse.ArgumentParser(description="Generates P&D icons.", add_help=False)

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
attr1_imgs = {}
attr2_imgs = {}
attr3_imgs = {}
psize = 100
for idx, t in enumerate(['r', 'b', 'g', 'l', 'd', 'x']):
    xstart = idx * (psize + 2)
    ystart = 0
    for attr_img_dict in (attr1_imgs, attr2_imgs, attr3_imgs):
        attr_img_dict[t] = templates_img.crop(box=(xstart, ystart, xstart + psize, ystart + psize))
        ystart += psize + 4

card_types = []
attr_map = {
    -1: 'x',
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
        attr_map[card.attr1_id],
        attr_map[card.attr2_id],
        attr_map[card.attr3_id]
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


def get_icon_img(file_name):
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


for card_id, card_attr1, card_attr2, card_attr3 in card_types:
    output_file = os.path.join(output_dir, f'{card_id:05d}.png')
    if os.path.exists(output_file):
        continue

    card_file, row, col = idx_for_id(card_id)
    portraits = get_icon_img(card_file)
    if portraits is None:
        # This can happen since JP gets ahead of NA and it's not easy to
        # confirm that a card is in JP but not NA
        print('skipping {} because CARDS file does not exist: {}'.format(card_id, card_file))
        continue

    card_img = get_card_img(portraits, row, col)
    if is_entirely_transparent(card_img):
        print('skipping {} because it is missing in {} (row {}, col {})'.format(card_id, card_file, row, col))
        continue

    # Create a grey image to overlay the portrait on, filling in the background
    grey_img = Image.new("RGBA", card_img.size, color=(68, 68, 68, 255))
    card_img = Image.alpha_composite(grey_img, card_img)

    # Adjust the card image to fit the portrait
    merged_img = Image.new("RGBA", (100, 100))
    merged_img.paste(card_img, (2, 2))

    # Merge the attribute border on to the portrait
    merged_img = Image.alpha_composite(merged_img, attr1_imgs[card_attr1])
    merged_img = Image.alpha_composite(merged_img, attr2_imgs[card_attr2])
    merged_img = Image.alpha_composite(merged_img, attr3_imgs[card_attr3])

    # Save
    merged_img.save(output_file, 'PNG')
