import argparse
import json
import os
from typing import Tuple, Dict

import pymysql
from PIL import Image


NO_TO_ATTR_SQL = """
SELECT monster_no, 
       monsters.monster_id,
       attribute_1_id AS attr1,
       COALESCE(attribute_2_id, 6) AS attr2, 
       COALESCE(attribute_3_id, 6) AS attr3
 FROM canonical_monster_ids
  JOIN monsters USING (monster_id)
 WHERE server_id = %s;
"""


class CardMissingError(Exception):
    ...


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generates P&D icons.", add_help=False)

    inputGroup = parser.add_argument_group("Input")
    inputGroup.add_argument("--card_dir", help="Path to a folder where CARD files are")
    inputGroup.add_argument("--db_config", required=True, help="Path to raw pad data files")
    inputGroup.add_argument("--server", help="The current server")
    inputGroup.add_argument("--card_templates_file", help="Path to card templates png")

    outputGroup = parser.add_argument_group("Output")
    outputGroup.add_argument("--output_dir", help="Path to a folder where output should be saved")

    settingsGroup = parser.add_argument_group("Settings")
    settingsGroup.add_argument("--verbose", action='store_true', help="Give more output")
    settingsGroup.add_argument("--regenerate", action='store_true', help="Regenerate already-existing cards")

    helpGroup = parser.add_argument_group("Help")
    helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
    args = parser.parse_args()

    if args.server.upper() not in ('JP', 'NA', 'KR'):
        raise ValueError("Server must be in JP, NA, KR.")

    return args


def calculate_position(card_no: int) -> Tuple[str, int, int]:
    """Computes the (card_file, row, col) for a card."""
    card_no -= 1  # offset to 0
    card_file_idx = int(card_no / 100) + 1

    sub_idx = card_no % 100
    col = sub_idx % 10
    row = int(sub_idx / 10)

    card_file_name = 'CARDS_{}.PNG'.format(str(card_file_idx).zfill(3))
    return card_file_name, row, col


def get_card_file(input_dir: str, card_filepath: str) -> Image.Image:
    file_path = os.path.join(input_dir, card_filepath)
    if not os.path.exists(file_path):
        raise CardMissingError()
    return Image.open(file_path)


def crop_card_file(card_file: Image.Image, row: int, col: int) -> Image.Image:
    card_dim = 96
    spacer = 6
    xstart = (card_dim + spacer) * col
    ystart = (card_dim + spacer) * row

    xend = xstart + card_dim
    yend = ystart + card_dim
    return card_file.crop(box=(xstart, ystart, xend, yend))


def get_card_icon(card_no: int, card_dir: str) -> Image.Image:
    card_filepath, row, col = calculate_position(card_no)
    card_file = get_card_file(card_dir, card_filepath)
    return crop_card_file(card_file, row, col)


def get_attr_frames(attribute_frame_png: str) \
        -> Tuple[Dict[int, Image.Image], Dict[int, Image.Image], Dict[int, Image.Image]]:
    templates_img = Image.open(attribute_frame_png)
    attr_imgs = ({}, {}, {})
    psize = 100
    for idx, t in enumerate((0, 1, 2, 3, 4, 6)):
        xstart = idx * (psize + 2)
        ystart = 0
        for attr_img_dict in attr_imgs:
            attr_img_dict[t] = templates_img.crop(box=(xstart, ystart, xstart + psize, ystart + psize))
            ystart += psize + 4
    return attr_imgs


def apply_attribute_frames(plain_img: Image, card_attrs: Tuple[int, int, int],
                           attr_frames: Tuple[Dict[int, Image.Image],
                                              Dict[int, Image.Image],
                                              Dict[int, Image.Image]]) \
        -> Image:
    # Create a grey image to overlay the portrait on, filling in the background
    grey_img = Image.new("RGBA", plain_img.size, color=(68, 68, 68, 255))
    card_img = Image.alpha_composite(grey_img, plain_img)

    # Adjust the card image to fit the portrait
    merged_img = Image.new("RGBA", (100, 100))
    merged_img.paste(card_img, (2, 2))

    # Merge the attribute border on to the portrait
    merged_img = Image.alpha_composite(merged_img, attr_frames[0][card_attrs[0]])
    merged_img = Image.alpha_composite(merged_img, attr_frames[1][card_attrs[1]])
    merged_img = Image.alpha_composite(merged_img, attr_frames[2][card_attrs[2]])

    return merged_img


def get_monster_no_maps(server: str, db_config_path: str) -> \
        Tuple[Dict[int, Tuple[int, int, int]], Dict[int, int]]:
    server_id = ('JP', 'NA', 'KR').index(server.upper())
    with open(db_config_path) as f:
        db = pymysql.connect(**json.load(f), autocommit=True)
    cur = db.cursor()

    no_to_attrs = {}
    no_to_id = {}
    cur.execute(NO_TO_ATTR_SQL, (server_id,))
    for row in cur:
        no_to_attrs[row[0]] = row[2:]
        no_to_id[row[0]] = row[1]

    cur.close()
    db.close()
    return no_to_attrs, no_to_id


def main(args: argparse.Namespace):
    no_to_attrs, no_to_id = get_monster_no_maps(args.server, args.db_config)
    attr_frames = get_attr_frames(args.card_templates_file)
    for monster_no, card_attrs in no_to_attrs.items():
        output_fname = os.path.join(args.output_dir, f'{no_to_id[monster_no]:05d}.png')
        if os.path.exists(output_fname) and not args.regenerate:
            continue
        try:
            plain_icon = get_card_icon(monster_no, args.card_dir)
        except CardMissingError:
            print(f"Skipping {monster_no} (Card file missing)")
            continue

        if plain_icon.getextrema() == ((0, 0), (0, 0), (0, 0), (0, 0)):
            print(f"Skipping {monster_no} (Icon is empty)")
            continue

        icon = apply_attribute_frames(plain_icon, card_attrs, attr_frames)
        if args.verbose:
            print(f"Saving monster with no. {args.server.upper()} {monster_no} to {no_to_id[monster_no]:05d}.png")
        icon.save(output_fname, 'PNG')


if __name__ == "__main__":
    main(parse_args())
