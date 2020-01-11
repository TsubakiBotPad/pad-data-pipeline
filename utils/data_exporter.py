"""
Dumps all the pad data for na/kr/jp plus the combined data.
"""

import argparse
import os
import pathlib

import padtools

from pad.common import pad_util
from pad.common.shared_types import Server
from pad.raw.skills.en.active_skill_text import EnASTextConverter
from pad.raw.skills.en.leader_skill_text import EnLSTextConverter
from pad.raw_processor import merged_database
from pad.raw_processor.crossed_data import CrossServerDatabase


def parse_args():
    parser = argparse.ArgumentParser(description="Runs the integration test.", add_help=False)
    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--input_dir", required=True,
                             help="Path to a folder where the input data is")

    output_group = parser.add_argument_group("Output")
    output_group.add_argument("--output_dir", required=True,
                              help="Path to a folder where output should be saved")
    input_group.add_argument("--image_data_only", default=False, action="store_true",
                             help="Should we only dump image availability")

    help_group = parser.add_argument_group("Help")
    help_group.add_argument("-h", "--help", action="help",
                            help="Displays this help message and exits.")
    return parser.parse_args()


def save_region_files(output_dir, server: Server, pad_server):
    output_dir = os.path.join(output_dir, server.name)

    def clean_asset(input):
        return {
            'file_name': input.file_name,
            'compressed_size': input.compressed_size,
        }

    def clean_extra(input):
        return {
            'file_name': input.file_name,
        }

    save_single_file(output_dir, 'assets', [clean_asset(x) for x in pad_server.assets])
    save_single_file(output_dir, 'extras', [clean_extra(x) for x in pad_server.extras])


def dump_data(args):
    input_dir = args.input_dir
    output_dir = args.output_dir

    save_region_files(output_dir, Server.jp, padtools.regions.japan.server)
    save_region_files(output_dir, Server.kr, padtools.regions.north_america.server)
    save_region_files(output_dir, Server.na, padtools.regions.korea.server)

    if args.image_data_only:
        exit(0)

    print('Processing JP')
    jp_db = merged_database.Database(Server.jp, input_dir)
    jp_db.load_database(skip_extra=True)

    print('Processing NA')
    na_db = merged_database.Database(Server.na, input_dir)
    na_db.load_database(skip_extra=True)

    print('Processing KR')
    kr_db = merged_database.Database(Server.kr, input_dir)
    kr_db.load_database(skip_extra=True)

    print('Merging and saving')
    cross_db = CrossServerDatabase(jp_db, na_db, kr_db)
    save_cross_database(output_dir, cross_db)


def save_cross_database(output_dir: str, db: CrossServerDatabase):
    raw_card_dir = os.path.join(output_dir, 'cards')
    pathlib.Path(raw_card_dir).mkdir(parents=True, exist_ok=True)

    for c in db.ownable_cards:
        card_file = os.path.join(raw_card_dir, '{}.txt'.format(c.monster_id))
        with open(card_file, 'w', encoding='utf-8') as f:
            # Write top level info for the monster
            f.write('#{} {}\n'.format(c.monster_id, c.na_card.card.name))
            card_info = c.jp_card.card
            f.write('HP: {} ATK: {} RCV: {} LB: {}\n'.format(card_info.max_hp,
                                                             card_info.max_atk,
                                                             card_info.max_rcv,
                                                             card_info.limit_mult))
            f.write('AWK: {}\n'.format(','.join(map(str, card_info.awakenings))))
            f.write('SAWK: {}\n'.format(','.join(map(str, card_info.super_awakenings))))
            f.write('\n')

            if c.active_skill:
                dump_skill(f, c.active_skill, EnASTextConverter())

            if c.leader_skill:
                dump_skill(f, c.leader_skill, EnLSTextConverter())

    as_file = os.path.join(output_dir, 'active_skills.txt')
    with open(as_file, 'w', encoding='utf-8') as f:
        converter = EnASTextConverter()
        for css in db.active_skills:
            dump_skill(f, css, converter)

    ls_file = os.path.join(output_dir, 'leader_skills.txt')
    with open(ls_file, 'w', encoding='utf-8') as f:
        converter = EnLSTextConverter()
        for css in db.leader_skills:
            dump_skill(f, css, converter)

    # TODO: write ES
    # es_file = os.path.join(output_dir, 'enemy_skills.txt')
    # TODO: write dungeons, exchanges, egg machines?


# Write active skill id/type, english name, raw english description, then computed descriptions for
# english, japanese, and korean
def dump_skill(f, css, converter):
    jp_skill = css.jp_skill
    na_skill = css.na_skill
    f.write('# {}/{} - {}\n'.format(jp_skill.skill_id, jp_skill.skill_type, na_skill.name))
    f.write('Tags: {}\n'.format(','.join(map(lambda x: x.name, css.skill_type_tags))))
    f.write('Game: {}\n'.format(na_skill.raw_description))
    f.write('EN: {}\n'.format(jp_skill.full_text(converter)))
    # TODO: add JP/KR text converters
    f.write('\n')


# def save_database(output_dir: str, db: Database):
#     output_dir = os.path.join(output_dir, db.server.name)
#
#     dungeon_dir = os.path.join(output_dir, 'dungeons')
#     pathlib.Path(dungeon_dir).mkdir(parents=True, exist_ok=True)
#     for d in db.dungeons:
#         save_object(dungeon_dir, '{}.json'.format(d.dungeon_id), d)
#
#
#     save_single_file(output_dir, 'exchanges', db.exchange)
#     save_single_file(output_dir, 'egg_machines', db.egg_machines)


def save_single_file(output_dir, name, obj):
    obj_dir = os.path.join(output_dir, name)
    pathlib.Path(obj_dir).mkdir(parents=True, exist_ok=True)
    save_object(obj_dir, '{}.json'.format(name), obj)


def save_object(dir_path, file_name, obj):
    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        pad_util.json_file_dump(obj, f, pretty=True)


if __name__ == '__main__':
    args = parse_args()
    dump_data(args)
