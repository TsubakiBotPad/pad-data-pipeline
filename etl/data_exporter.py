"""
Dumps all the pad data for na/kr/jp plus the combined data.
"""
import argparse
import os
import pathlib

import padtools

from pad.common import pad_util
from pad.common.shared_types import Server
from pad.raw.skills import skill_text_typing
from pad.raw.skills.emoji_en.enemy_skill_text import EnEmojiESTextConverter
from pad.raw.skills.en.active_skill_text import EnASTextConverter
from pad.raw.skills.en.enemy_skill_text import EnESTextConverter
from pad.raw.skills.en.leader_skill_text import EnLSTextConverter
from pad.raw.skills.enemy_skill_info import BEHAVIOR_MAP
from pad.raw.skills.jp.active_skill_text import JpASTextConverter
from pad.raw.skills.jp.enemy_skill_text import JpESTextConverter
from pad.raw.skills.jp.leader_skill_text import JpLSTextConverter
from pad.raw.skills.leader_skill_info import LeaderSkill
from pad.raw_processor import merged_database
from pad.raw_processor.crossed_data import CrossServerDatabase, CrossServerEnemySkill, CrossServerDungeon

AS_CONVERTERS = (JpASTextConverter(), EnASTextConverter(), EnASTextConverter())
LS_CONVERTERS = (JpLSTextConverter(), EnLSTextConverter(), EnLSTextConverter())
ES_CONVERTERS = (JpESTextConverter(), EnESTextConverter(), EnESTextConverter(), EnEmojiESTextConverter())


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
    input_group.add_argument("--server", default="JP", help="Server to build for")

    help_group = parser.add_argument_group("Help")
    help_group.add_argument("-h", "--help", action="help",
                            help="Displays this help message and exits.")
    return parser.parse_args()


def save_region_files(output_dir, server: Server, pad_server):
    output_dir = os.path.join(output_dir, server.name)

    def clean_asset(asset):
        return {
            'file_name': asset.file_name,
            'compressed_size': asset.compressed_size,
        }

    def clean_extra(asset):
        return {
            'file_name': asset.file_name,
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
    if args.server.lower() == "jp":
        server = Server.jp
    elif args.server.lower() == "na":
        server = Server.na
    elif args.server.lower() == "kr":
        server = Server.kr
    else:
        raise ValueError("Server must be JP, NA, or KR")

    cross_db = CrossServerDatabase(jp_db, na_db, kr_db, server)
    save_cross_database(output_dir, cross_db)


def save_cross_database(output_dir: str, db: CrossServerDatabase):
    raw_card_dir = os.path.join(output_dir, 'cards')
    pathlib.Path(raw_card_dir).mkdir(parents=True, exist_ok=True)

    for c in db.ownable_cards:
        card_file = os.path.join(raw_card_dir, '{}.txt'.format(c.monster_id))
        with open(card_file, 'w', encoding='utf-8') as f:
            dump_monster(f, c)

    as_file = os.path.join(output_dir, 'active_skills.txt')
    with open(as_file, 'w', encoding='utf-8') as f:
        for css in db.active_skills:
            dump_skill(f, css, AS_CONVERTERS, skill_text_typing.parse_as_conditions)

    ls_file = os.path.join(output_dir, 'leader_skills.txt')
    with open(ls_file, 'w', encoding='utf-8') as f:
        for css in db.leader_skills:
            dump_skill(f, css, LS_CONVERTERS, skill_text_typing.parse_ls_conditions)

    es_file = os.path.join(output_dir, 'enemy_skills.txt')
    with open(es_file, 'w', encoding='utf-8') as f:
        for css in db.enemy_skills:
            dump_enemy_skill(f, css, ES_CONVERTERS)

    dungeon_file = os.path.join(output_dir, 'dungeons.txt')
    with open(dungeon_file, 'w', encoding='utf-8') as f:
        for csd in db.dungeons:
            dump_dungeon(f, csd)


# Write top level info for the monster
def dump_monster(f, c):
    f.write('#{} {}\n'.format(c.monster_id, c.na_card.card.name))
    card_info = c.cur_card.card
    f.write('HP: {} ATK: {} RCV: {} LB: {}\n'.format(card_info.max_hp,
                                                     card_info.max_atk,
                                                     card_info.max_rcv,
                                                     card_info.limit_mult))
    f.write('AWK: {}\n'.format(','.join(map(str, card_info.awakenings))))
    f.write('SAWK: {}\n'.format(','.join(map(str, card_info.super_awakenings))))
    f.write('\n')

    if c.active_skill:
        dump_skill(f, c.active_skill, AS_CONVERTERS, skill_text_typing.parse_as_conditions)

    if c.leader_skill:
        dump_skill(f, c.leader_skill, LS_CONVERTERS, skill_text_typing.parse_ls_conditions)


# Write active skill id/type, english name, raw english description, then computed descriptions for
# english, japanese, and korean
def dump_skill(f, css, converter, tag_extractor_fn):
    jp_skill = css.jp_skill
    na_skill = css.na_skill
    kr_skill = css.kr_skill
    cur_skill = css.cur_skill
    skill_type_tags = tag_extractor_fn(css)

    f.write('# {}/{} - {}\n'.format(cur_skill.skill_id, cur_skill.skill_type, na_skill.name))
    f.write('Tags: {}\n'.format(','.join(map(lambda x: x.name, skill_type_tags))))
    if isinstance(cur_skill, LeaderSkill):
        if cur_skill.extra_combos:
            f.write('Stats: [{}, {}, {}, {}, +{}]\n'.format(
                cur_skill.hp, cur_skill.atk, cur_skill.rcv, cur_skill.shield, cur_skill.extra_combos))
        else:
            f.write('Stats: [{}, {}, {}, {}]\n'.format(cur_skill.hp, cur_skill.atk, cur_skill.rcv, cur_skill.shield))

    f.write('Game: {}\n'.format(na_skill.raw_description))
    f.write('JP: {}\n'.format(cur_skill.full_text(converter[0]) or jp_skill.raw_description))
    f.write('EN: {}\n'.format(cur_skill.full_text(converter[1]) or na_skill.raw_description))
    f.write('KR: {}\n'.format(cur_skill.full_text(converter[2]) or kr_skill.raw_description))
    f.write('\n')


def dump_enemy_skill(f, css: CrossServerEnemySkill, converter):
    jp_skill = css.jp_skill
    na_skill = css.na_skill
    kr_skill = css.kr_skill
    cur_skill = css.cur_skill
    f.write('# {}/{} - {}\n'.format(cur_skill.enemy_skill_id, cur_skill.type, na_skill.name))
    if cur_skill.type not in BEHAVIOR_MAP:
        f.write('Error: Skill Type not in JP Skill Map\n')
        return
    skill = BEHAVIOR_MAP[cur_skill.type](cur_skill)
    f.write('JP: {}\n'.format(skill.description(converter[0])))
    f.write('EN: {}\n'.format(skill.description(converter[1])))
    f.write('KR: {}\n'.format(skill.description(converter[2])))
    f.write('Emoji: {}\n'.format(skill.description(converter[3])))
    f.write('\n')


def dump_dungeon(f, csd: CrossServerDungeon):
    na_dungeon = csd.na_dungeon

    f.write('# {} {}\n'.format(csd.dungeon_id, na_dungeon.clean_name))
    for sd in csd.sub_dungeons:
        sd_na = sd.na_sub_dungeon
        f.write('#{} {} -> {}:{} {},{},{}\n'.format(sd_na.sub_dungeon_id, sd_na.clean_name,
                                                    sd_na.floors, sd_na.stamina,
                                                    sd_na.hp_mult, sd_na.atk_mult, sd_na.def_mult))
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
    input_args = parse_args()
    dump_data(input_args)
