import argparse
import json
import subprocess

from pad.common.shared_types import Server
from pad.raw_processor import merged_database, crossed_data
from pad.scraper import active_dungeons
from pad.db import db_util
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

logger = logging.getLogger('scraper')
logger.setLevel(logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(description="Automatically scrape dungeons.", add_help=False)

    inputGroup = parser.add_argument_group("Input")
    inputGroup.add_argument("--input_dir", required=True,
                            help="Path to a folder where the input data is")
    # inputGroup.add_argument("--server", required=True, help="na or jp")
    # inputGroup.add_argument("--group", required=True, help="guerrilla group (red/blue/green)")
    # inputGroup.add_argument("--user_uuid", required=True, help="Account UUID")
    # inputGroup.add_argument("--user_intid", required=True, help="Account code")

    outputGroup = parser.add_argument_group("Output")
    outputGroup.add_argument("--doupdates", default=False,
                             action="store_true", help="Apply updates")

    helpGroup = parser.add_argument_group("Help")
    helpGroup.add_argument("-h", "--help", action="help",
                           help="Displays this help message and exits.")

    return parser.parse_args()



def main(args):
    input_dir = args.input_dir

    logger.info('Loading data')
    jp_database = merged_database.Database(Server.jp, input_dir)
    jp_database.load_database()

    na_database = merged_database.Database(Server.na, input_dir)
    na_database.load_database()

    csd = crossed_data.CrossServerDatabase(jp_database, na_database, na_database)
    current_dungeons = active_dungeons.extract_active_dungeons(csd)
    for cd in current_dungeons:
        print(cd.na_dungeon.clean_name)


if __name__ == '__main__':
    main(parse_args())



# processed_dir = '/home/tactical0retreat/pad_data/processed'
# bonuses_file = '{}/{}_bonuses.json'.format(processed_dir, parse_args().server)
#
# with open(bonuses_file) as f:
#     bonuses = json.load(f)
#
# current_dungeons = active_dungeons.filter_current_bonuses(
#     bonuses, parse_args().group, include_normals=False, include_multiplayer=False)
#
# db_config_prod = '/home/tactical0retreat/rpad-cogs-utils/pad_api_data/db_config.json'
# db_config_dev = '/home/tactical0retreat/rpad-cogs-utils/pad_api_data/db_config_dev.json'
# selected_db_config = db_config_prod if parse_args().doprod else db_config_dev
#
# with open(selected_db_config) as f:
#     db_config = json.load(f)
#
# dry_run = not parse_args().doupdates
# db_wrapper = db_util.DbWrapper(dry_run)
# db_wrapper.connect(db_config)
#
#
# def do_dungeon_load(dungeon_id,
#                     floor_id):
#     if not args.doupdates:
#         print('skipping due to dry run')
#         return
#     dungeon_script = '/home/tactical0retreat/rpad-cogs-utils/pad_api_data/pad_dungeon_pull.py'
#     process_args = [
#         'python3',
#         dungeon_script,
#         '--db_config={}'.format(selected_db_config),
#         '--server={}'.format(args.server),
#         '--dungeon_id={}'.format(dungeon_id),
#         '--floor_id={}'.format(floor_id),
#         '--user_uuid={}'.format(args.user_uuid),
#         '--user_intid={}'.format(args.user_intid),
#         '--loop_count=20',
#     ]
#     p = subprocess.run(process_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
#     print(str(p.stdout))
#     print(str(p.stderr))
#
#
# for dungeon in current_dungeons:
#     dungeon_id = int(dungeon['dungeon_id'])
#     print(dungeon['clean_name'], dungeon_id)
#
#     floor_ids = active_dungeons.filter_floors(dungeon['floors'])
#     for floor_id in floor_ids:
#         sql = 'select count(distinct entry_id) from wave_data where dungeon_id={} and floor_id={}'.format(
#             dungeon_id, floor_id)
#         wave_count = db_wrapper.get_single_value(sql, op=int)
#         print(wave_count, 'entries for', floor_id)
#         if wave_count >= 20:
#             print('skipping')
#         else:
#             print('entering', dungeon_id, floor_id)
#             do_dungeon_load(dungeon_id, floor_id)

