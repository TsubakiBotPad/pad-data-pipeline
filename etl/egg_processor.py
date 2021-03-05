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

    help_group = parser.add_argument_group("Help")
    help_group.add_argument("-h", "--help", action="help",
                            help="Displays this help message and exits.")
    return parser.parse_args()

def load_data(args):
    logger.info('Connecting to database')
    with open(args.db_config) as f:
        db_config = json.load(f)

    db_wrapper = DbWrapper(False)
    db_wrapper.connect(db_config)
    data = db_wrapper.fetch_data("SELECT * FROM dadguide.egg_machines")
    for machine_sql in data:
        egg_machine_id = machine_sql['egg_machine_id']
        contents = ast.literal_eval(machine_sql['contents'])
        for monster_id in contents.keys():
            real_monster_id = int(monster_id.strip("()"))
            emm = EggMachinesMonster(emm_id=None, monster_id=real_monster_id, roll_chance=contents.get(monster_id),
                                     egg_machine_id=egg_machine_id)
            db_wrapper.insert_or_update(emm)

if __name__ == '__main__':
    args = parse_args()
    # This is a hack to make loading ES easier and more frequent.
    # Remove this once we're done with most of the ES processing.

    # This needs to be done after the es_quick check otherwise it will consistently overwrite the fixes file.
    if os.name != 'nt':
        human_fix_logger.addHandler(logging.FileHandler('/tmp/dadguide_pipeline_human_fixes.txt', mode='w'))

    load_data(args)

