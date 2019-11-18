"""
Regenerates the flattened enemy skill list for all monsters.
"""

import argparse
import logging
import os

from pad.common.shared_types import Server
from pad.raw.enemy_skills import enemy_skillset_processor, enemy_skillset_dump, debug_utils
from pad.raw.enemy_skills.enemy_skill_info import ESAction, inject_implicit_onetime
from pad.raw_processor import merged_database
from pad.raw_processor.crossed_data import CrossServerDatabase, CrossServerCard

fail_logger = logging.getLogger('processor_failures')
fail_logger.disabled = True


def parse_args():
    parser = argparse.ArgumentParser(description="Runs the integration test.", add_help=False)
    inputGroup = parser.add_argument_group("Input")
    inputGroup.add_argument("--input_dir", required=True,
                            help="Path to a folder where the input data is")
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


def process_card(mcard: CrossServerCard):
    enemy_behavior = mcard.enemy_behavior
    card = mcard.na_card.card
    if not enemy_behavior:
        return

    inject_implicit_onetime(card, enemy_behavior)

    levels = enemy_skillset_processor.extract_levels(enemy_behavior)
    skill_listings = []
    used_actions = []
    for level in sorted(levels):
        try:
            skillset = enemy_skillset_processor.convert(card, enemy_behavior, level)
            flattened = enemy_skillset_dump.flatten_skillset(level, skillset)
            if not flattened.records:
                continue
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
        return

    unused_actions = []
    for b in enemy_behavior:
        if issubclass(b.btype, ESAction) and b not in used_actions and b not in unused_actions:
            unused_actions.append(b)

    entry_info = enemy_skillset_dump.EntryInfo(
        card.monster_no, card.name, 'not yet populated')
    if unused_actions:
        entry_info.warnings.append('Found {} unused actions'.format(len(unused_actions)))

    summary = enemy_skillset_dump.EnemySummary(entry_info, skill_listings)
    # TODO: turn this on
    # summary = enemy_skillset_dump.load_and_merge_summary(summary)

    enemy_skillset_dump.dump_summary_to_file(card, summary, enemy_behavior, unused_actions)

    return len(unused_actions)


def run(args):
    enemy_skillset_dump.set_data_dir(args.output_dir)

    raw_input_dir = os.path.join(args.input_dir, 'raw')
    jp_db = merged_database.Database(Server.jp, raw_input_dir)
    na_db = merged_database.Database(Server.na, raw_input_dir)

    jp_db.load_database(skip_skills=True, skip_bonus=True, skip_extra=True)
    na_db.load_database(skip_skills=True, skip_bonus=True, skip_extra=True)

    print('merging data')
    cross_db = CrossServerDatabase(jp_db, na_db, na_db)

    combined_cards = cross_db.all_cards

    fixed_card_id = args.card_id
    if args.interactive:
        fixed_card_id = input("enter a card id:").strip()

    count = 0
    for csc in combined_cards:
        merged_card = csc.na_card
        card = merged_card.card
        if fixed_card_id and card.monster_no != int(fixed_card_id):
            continue
        try:
            count += 1
            if count % 100 == 0:
                print('processing {} of {}'.format(count, len(combined_cards)))
            process_card(csc)

        except Exception as ex:
            print('failed to process', card.name)
            print(ex)
            # if 'unsupported operation' not in str(ex):
            import traceback
            traceback.print_exc()
            exit(0)


if __name__ == '__main__':
    args = parse_args()
    run(args)
