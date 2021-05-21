import argparse
import ast
import json
import logging
import os

from pad.db.db_util import DbWrapper
from pad.storage.egg_machines_monsters import EggMachinesMonster

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

logger = logging.getLogger('processor')
logger.setLevel(logging.INFO)

fail_logger = logging.getLogger('processor_failures')
fail_logger.setLevel(logging.INFO)

db_logger = logging.getLogger('database')
db_logger.setLevel(logging.INFO)

human_fix_logger = logging.getLogger('human_fix')
human_fix_logger.setLevel(logging.INFO)


def parse_args():
    parser = argparse.ArgumentParser(description="Reads existing egg machines and add its contents.", add_help=False)

    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--db_config", required=True, help="JSON database info")
    input_group.add_argument("--doupdates", default=False,
                             action="store_true", help="Enables actions")

    help_group = parser.add_argument_group("Help")
    help_group.add_argument("-h", "--help", action="help",
                            help="Displays this help message and exits.")
    return parser.parse_args()


def load_data(args):
    logger.info('Connecting to database')
    with open(args.db_config) as f:
        db_config = json.load(f)
    dry_run = not args.doupdates
    db_wrapper = DbWrapper(dry_run)
    db_wrapper.connect(db_config)
    data = db_wrapper.fetch_data("SELECT * FROM egg_machines")
    for machine_sql in data:
        egg_machine_id = machine_sql['egg_machine_id']
        contents = ast.literal_eval(machine_sql['contents'])
        for monster_id in contents.keys():
            real_monster_id = int(monster_id.strip("()"))
            emm = EggMachinesMonster(egg_machine_monster_id=None, monster_id=real_monster_id,
                                     roll_chance=contents.get(monster_id),
                                     egg_machine_id=egg_machine_id)
            db_wrapper.insert_or_update(emm)


if __name__ == '__main__':
    args = parse_args()
    load_data(args)
