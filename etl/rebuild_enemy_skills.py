"""
Regenerates the flattened enemy skill list for all monsters.
"""

import argparse
import logging
import os

from dadguide_proto.enemy_skills_pb2 import MonsterBehavior
from pad.common.shared_types import Server
from pad.raw.enemy_skills import enemy_skillset_processor, debug_utils, enemy_skill_proto
from pad.raw.enemy_skills.debug_utils import save_monster_behavior, save_behavior_plain
from pad.raw.enemy_skills.enemy_skill_info import ESAction
from pad.raw.enemy_skills.enemy_skill_proto import safe_save_to_file, clean_monster_behavior
from pad.raw_processor import merged_database
from pad.raw_processor.crossed_data import CrossServerDatabase, CrossServerCard

fail_logger = logging.getLogger('processor_failures')
fail_logger.disabled = True


def parse_args():
    parser = argparse.ArgumentParser(description="Runs the integration test.", add_help=False)
    inputGroup = parser.add_argument_group("Input")
    inputGroup.add_argument("--input_dir", required=True,
                            help="Path to a folder where the raw input data is")
    inputGroup.add_argument("--card_id", required=False,
                            help="Process only this card")
    inputGroup.add_argument("--interactive", required=False,
                            help="Lets you specify a card id on the command line")

    outputGroup = parser.add_argument_group("Output")
    outputGroup.add_argument("--output_dir", required=True,
                             help="Path to a folder where the results go")

    helpGroup = parser.add_argument_group("Help")
    helpGroup.add_argument("-h", "--help", action="help",
                           help="Displays this help message and exits.")
    return parser.parse_args()


def process_card(csc: CrossServerCard) -> MonsterBehavior:
    enemy_behavior = [x.na_skill for x in csc.enemy_behavior]
    card = csc.na_card.card
    if not enemy_behavior:
        return None

    levels = enemy_skillset_processor.extract_levels(enemy_behavior)
    skill_listings = []
    used_actions = []
    for level in sorted(levels):
        try:
            skillset = enemy_skillset_processor.convert(card, enemy_behavior, level)
            if not skillset.has_actions():
                continue
            flattened = enemy_skill_proto.flatten_skillset(level, skillset)
            used_actions.extend(debug_utils.extract_used_skills(skillset))
            skill_listings.append(flattened)
        except Exception as ex:
            if 'No loop' not in str(ex):
                raise ex
            else:
                # TODO: some monsters have whacked out behavior (they aren't real monsters)
                # Should start ignoring those (e.g. pixel yuna).
                print('\tLoop detection failure for', card.monster_no, card.name)

    if not skill_listings:
        return None

    unused_actions = []
    for b in enemy_behavior:
        try:
            if issubclass(b.btype, ESAction) and b not in used_actions and b not in unused_actions:
                unused_actions.append(b)
        except:
            print('oops')

    # TODO: add unused actions and store them

    result = MonsterBehavior()
    result.monster_id = csc.monster_id
    result.levels.extend(skill_listings)

    return result


def run(args):
    behavior_data_dir = os.path.join(args.output_dir, 'behavior_data')
    os.makedirs(behavior_data_dir, exist_ok=True)
    behavior_text_dir = os.path.join(args.output_dir, 'behavior_text')
    os.makedirs(behavior_text_dir, exist_ok=True)
    behavior_plain_dir = os.path.join(args.output_dir, 'behavior_plain')
    os.makedirs(behavior_plain_dir, exist_ok=True)

    jp_db = merged_database.Database(Server.jp, args.input_dir)
    na_db = merged_database.Database(Server.na, args.input_dir)

    jp_db.load_database(skip_skills=True, skip_bonus=True, skip_extra=True)
    na_db.load_database(skip_skills=True, skip_bonus=True, skip_extra=True)

    print('merging data')
    # Skipping KR database; we don't need it to compute ES
    cross_db = CrossServerDatabase(jp_db, na_db, na_db)

    combined_cards = cross_db.all_cards

    fixed_card_id = args.card_id
    if args.interactive:
        fixed_card_id = input("enter a card id:").strip()

    count = 0
    for csc in combined_cards:
        merged_card = csc.na_card
        card = merged_card.card
        if fixed_card_id and csc.monster_id != int(fixed_card_id):
            continue
        try:
            count += 1
            if count % 100 == 0:
                print('processing {} of {}'.format(count, len(combined_cards)))
            monster_behavior = process_card(csc)
            if monster_behavior is None:
                continue

            # Do some sanity cleanup on the behavior
            monster_behavior = clean_monster_behavior(monster_behavior)

            behavior_data_file = os.path.join(behavior_data_dir, '{}.textproto'.format(csc.monster_id))
            safe_save_to_file(behavior_data_file, monster_behavior)

            behavior_text_file = os.path.join(behavior_text_dir, '{}.txt'.format(csc.monster_id))
            save_monster_behavior(behavior_text_file, csc, monster_behavior)

            enemy_behavior = [x.na_skill for x in csc.enemy_behavior]
            behavior_plain_file = os.path.join(behavior_plain_dir, '{}.txt'.format(csc.monster_id))
            save_behavior_plain(behavior_plain_file, csc, enemy_behavior)

            # TODO: Add raw behavior dump

        except Exception as ex:
            print('failed to process', csc.monster_id, card.name)
            print(ex)
            # if 'unsupported operation' not in str(ex):
            import traceback
            traceback.print_exc()
            exit(0)


if __name__ == '__main__':
    args = parse_args()
    run(args)
