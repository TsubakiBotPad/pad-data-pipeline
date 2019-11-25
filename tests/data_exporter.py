"""
Dumps all the pad data for na/kr/jp plus the combined data.
"""

import argparse
import os
import pathlib

from pad.common import pad_util
from pad.common.shared_types import Server
from pad.raw.enemy_skills.debug_utils import simple_dump_obj
from pad.raw_processor import merged_database
from pad.raw_processor.crossed_data import CrossServerDatabase
from pad.raw_processor.merged_database import Database


def parse_args():
    parser = argparse.ArgumentParser(description="Runs the integration test.", add_help=False)
    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--input_dir", required=True,
                             help="Path to a folder where the input data is")

    output_group = parser.add_argument_group("Output")
    output_group.add_argument("--output_dir", required=True,
                              help="Path to a folder where output should be saved")

    help_group = parser.add_argument_group("Help")
    help_group.add_argument("-h", "--help", action="help",
                            help="Displays this help message and exits.")
    return parser.parse_args()


def dump_data(args):
    input_dir = args.input_dir
    output_dir = args.output_dir

    print('Processing JP')
    jp_db = merged_database.Database(Server.jp, input_dir)
    jp_db.load_database(skip_extra=True)
    save_database(output_dir, jp_db)

    print('Processing NA')
    na_db = merged_database.Database(Server.na, input_dir)
    na_db.load_database(skip_extra=True)
    save_database(output_dir, na_db)

    print('Processing KR')
    kr_db = merged_database.Database(Server.kr, input_dir)
    kr_db.load_database(skip_extra=True)
    save_database(output_dir, kr_db)

    print('Merging and saving')
    cross_db = CrossServerDatabase(jp_db, na_db, kr_db)
    save_cross_database(output_dir, cross_db)


def save_cross_database(output_dir: str, db: CrossServerDatabase):
    output_dir = os.path.join(output_dir, 'combined')

    raw_card_dir = os.path.join(output_dir, 'cards')
    for c in db.all_cards:
        card_dir = os.path.join(raw_card_dir, str(c.monster_id))
        pathlib.Path(card_dir).mkdir(parents=True, exist_ok=True)
        save_object(card_dir, 'card.json', c)
        with open(os.path.join(card_dir, 'es_dump.txt'), 'w') as f:
            f.write('#{}  - {}\n'.format(c.monster_id, c.na_card.card.name))
            f.write('{} : use_new_ai\n'.format(c.jp_card.card.use_new_ai))
            f.write('{} : starting/max counter\n'.format(c.jp_card.card.enemy_skill_max_counter))
            f.write('{} : counter increment\n'.format(c.jp_card.card.enemy_skill_counter_increment))
            f.write('\n')
            for b in c.enemy_behavior:
                f.write(simple_dump_obj(b) + '\n\n')

    leader_dir = os.path.join(output_dir, 'leader_skills')
    pathlib.Path(leader_dir).mkdir(parents=True, exist_ok=True)
    for leader_skill in db.leader_skills:
        save_object(leader_dir, '{}.json'.format(leader_skill.skill_id), leader_skill)

    active_dir = os.path.join(output_dir, 'active_skills')
    pathlib.Path(active_dir).mkdir(parents=True, exist_ok=True)
    for active_skill in db.active_skills:
        save_object(active_dir, '{}.json'.format(active_skill.skill_id), active_skill)

    dungeons_dir = os.path.join(output_dir, 'dungeons')
    pathlib.Path(dungeons_dir).mkdir(parents=True, exist_ok=True)
    for dungeon in db.dungeons:
        save_object(dungeons_dir, '{}.json'.format(dungeon.dungeon_id), dungeon)

    enemy_skills_dir = os.path.join(output_dir, 'enemy_skills')
    pathlib.Path(enemy_skills_dir).mkdir(parents=True, exist_ok=True)
    for es in db.enemy_skills:
        save_object(enemy_skills_dir, '{}_combined.json'.format(es.enemy_skill_id), es)


def save_database(output_dir: str, db: Database):
    output_dir = os.path.join(output_dir, db.server.name)

    raw_card_dir = os.path.join(output_dir, 'cards')
    for c in db.raw_cards:
        card_dir = os.path.join(raw_card_dir, str(c.monster_no))
        pathlib.Path(card_dir).mkdir(parents=True, exist_ok=True)

        # Basic card info
        save_object(card_dir, 'raw_card.json', c)
        save_object(card_dir, 'parsed_card.json', db.card_by_monster_no(c.monster_no))

        # Leader skill info
        if c.leader_skill_id:
            leader = db.skill_id_to_skill[c.leader_skill_id]
            if leader:
                save_object(card_dir, 'raw_leader.json', leader)
            leader = db.leader_skill_by_id(c.leader_skill_id)
            if leader:
                save_object(card_dir, 'parsed_leader.json', leader)

        # Active skill info
        if c.active_skill_id:
            active = db.skill_id_to_skill[c.active_skill_id]
            if active:
                save_object(card_dir, 'raw_active.json', active)
            active = db.leader_skill_by_id(c.active_skill_id)
            if active:
                save_object(card_dir, 'parsed_active.json', active)

        # Enemy info
        save_object(card_dir, 'raw_enemy.json', c.enemy())
        save_object(card_dir, 'parsed_enemy.json', db.enemy_by_id(c.monster_no))

    dungeon_dir = os.path.join(output_dir, 'dungeons')
    pathlib.Path(dungeon_dir).mkdir(parents=True, exist_ok=True)
    for d in db.dungeons:
        save_object(dungeon_dir, '{}.json'.format(d.dungeon_id), d)

    skill_dir = os.path.join(output_dir, 'skills')
    pathlib.Path(skill_dir).mkdir(parents=True, exist_ok=True)
    for s in db.skills:
        save_object(skill_dir, '{}_raw.json'.format(s.skill_id), s)
        parsed = db.leader_skill_by_id(s.skill_id) or db.leader_skill_by_id(s.skill_id)
        if parsed:
            save_object(skill_dir, '{}_parsed.json'.format(s.skill_id), parsed)

    enemy_skill_dir = os.path.join(output_dir, 'enemy_skills')
    pathlib.Path(enemy_skill_dir).mkdir(parents=True, exist_ok=True)
    for es in db.raw_enemy_skills:
        save_object(enemy_skill_dir, '{}_raw.json'.format(es.enemy_skill_id), es)
        parsed = db.enemy_skill_by_id(es.enemy_skill_id)
        if parsed:
            save_object(skill_dir, '{}_parsed.json'.format(es.enemy_skill_id), parsed)

    for b in db.bonuses:
        if b.dungeon:
            # We don't want to save the whole dungeon with the bonus, it's excessive
            b.dungeon = b.dungeon.clean_name
    save_single_file(output_dir, 'bonuses', db.bonuses)

    save_single_file(output_dir, 'exchanges', db.exchange)
    save_single_file(output_dir, 'egg_machines', db.egg_machines)


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
