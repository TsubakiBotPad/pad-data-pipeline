"""
Copies PAD media to the expected DadGuide locations.
"""
import argparse
import os
import shutil

from pad.common import monster_id_mapping
from pad.common.shared_types import MonsterNo


def parse_args():
    parser = argparse.ArgumentParser(
        description="Creates DadGuide image repository.", add_help=False)
    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--base_dir", required=True, help="Miru image base dir")
    input_group.add_argument("--alt_base_dir", required=True, help="Miru other files base dir")

    output_group = parser.add_argument_group("Output")
    output_group.add_argument("--output_dir", required=True,
                              help="Dir to write dadguide-formatted media to")

    return parser.parse_args()


def do_copy(src_dir, src_file, dest_dir, dest_file):
    src_path = os.path.join(src_dir, src_file)
    dest_path = os.path.join(dest_dir, dest_file)
    if os.path.exists(src_path) and not os.path.exists(dest_path):
        shutil.copy2(src_path, dest_path)


def copy_media(args):
    base_dir = args.base_dir
    alt_base_dir = args.alt_base_dir
    output_dir = args.output_dir

    jp_icon_input_dir = os.path.join(base_dir, 'jp', 'portrait', 'local')
    na_icon_input_dir = os.path.join(base_dir, 'na', 'portrait', 'local')

    jp_portrait_input_dir = os.path.join(base_dir, 'jp', 'full', 'corrected_data')
    na_portrait_input_dir = os.path.join(base_dir, 'na', 'full', 'corrected_data')

    hq_portrait_input_dir = os.path.join(base_dir, 'hq_images')
    animated_portrait_input_dir = os.path.join(base_dir, 'animated')

    orb_skins_input_dir = os.path.join(alt_base_dir, 'orb_styles', 'extract', 'jp')
    jp_voice_input_dir = os.path.join(alt_base_dir, 'voices', 'fixed', 'jp')
    na_voice_input_dir = os.path.join(alt_base_dir, 'voices', 'fixed', 'na')

    icon_output_dir = os.path.join(output_dir, 'icons')
    portrait_output_dir = os.path.join(output_dir, 'portraits')
    hq_portrait_output_dir = os.path.join(output_dir, 'hq_portraits')
    animated_portrait_output_dir = os.path.join(output_dir, 'animated_portraits')
    orb_skins_output_dir = os.path.join(output_dir, 'orb_skins')
    jp_voice_output_dir = os.path.join(output_dir, 'voices', 'jp')
    na_voice_output_dir = os.path.join(output_dir, 'voices', 'na')

    for jp_id in range(1, 9000):
        monster_id = jp_id
        monster_id_filled = str(monster_id).zfill(5)

        do_copy(jp_icon_input_dir, '{}.png'.format(monster_id),
                icon_output_dir, '{}.png'.format(monster_id_filled))

        do_copy(jp_portrait_input_dir, '{}.png'.format(monster_id),
                portrait_output_dir, '{}.png'.format(monster_id_filled))

        do_copy(hq_portrait_input_dir, '{}.png'.format(monster_id),
                hq_portrait_output_dir, '{}.png'.format(monster_id_filled))

        do_copy(animated_portrait_input_dir, '{}.mp4'.format(monster_id),
                animated_portrait_output_dir, '{}.mp4'.format(monster_id_filled))

        do_copy(animated_portrait_input_dir, '{}.gif'.format(monster_id),
                animated_portrait_output_dir, '{}.gif'.format(monster_id_filled))

        do_copy(jp_voice_input_dir, '{}.wav'.format(monster_id),
                jp_voice_output_dir, '{}.wav'.format(monster_id_filled))

    for na_id in range(1, 9000):
        monster_id = monster_id_mapping.nakr_no_to_monster_id(MonsterNo(na_id))
        monster_id_filled = str(monster_id).zfill(5)

        do_copy(na_icon_input_dir, '{}.png'.format(na_id),
                icon_output_dir, '{}.png'.format(monster_id_filled))

        do_copy(na_portrait_input_dir, '{}.png'.format(na_id),
                portrait_output_dir, '{}.png'.format(monster_id_filled))

        do_copy(na_voice_input_dir, '{}.wav'.format(na_id),
                na_voice_output_dir, '{}.wav'.format(monster_id_filled))

    for file_name in os.listdir(orb_skins_input_dir):
        clean_file_name = file_name.lower().lstrip('block')
        do_copy(orb_skins_input_dir, file_name,
                orb_skins_output_dir, clean_file_name)


if __name__ == '__main__':
    args = parse_args()
    copy_media(args)
