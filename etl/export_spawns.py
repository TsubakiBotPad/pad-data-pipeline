import argparse
import json
import logging
import os

from pad.db.db_util import DbWrapper

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


ENCOUNTER_QUERY = """
SELECT
  sub_dungeons.sub_dungeon_id AS sdgid,
  sub_dungeons.name_en AS stage_name,
  encounters.enemy_id AS enemy_id,
  encounters.level AS level,
  encounters.stage AS floor
FROM
  encounters
  LEFT OUTER JOIN sub_dungeons ON encounters.sub_dungeon_id = sub_dungeons.sub_dungeon_id
"""


def parse_args():
    parser = argparse.ArgumentParser(description="Takes the spawns and exports them as a nice json.", add_help=False)

    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--db_config", required=True, help="JSON database info")

    output_group = parser.add_argument_group("Output")
    output_group.add_argument("--output_dir", required=True, help="Directory to save file in.")

    help_group = parser.add_argument_group("Help")
    help_group.add_argument("-h", "--help", action="help",
                            help="Displays this help message and exits.")
    return parser.parse_args()


def load_data(args):
    logger.info('Connecting to database')
    with open(args.db_config) as f:
        db_config = json.load(f)
    db_wrapper = DbWrapper()
    db_wrapper.connect(db_config)
    data = db_wrapper.fetch_data(ENCOUNTER_QUERY)
    output = {}
    for encounter in data:
        sdgid = encounter['sdgid']
        floor = encounter['floor']
        spawn = {'id': encounter['enemy_id'], 'lv': encounter['level']}
        if sdgid not in output:
            output[sdgid] = {'name': encounter['stage_name'], 'floors': {}}
        if floor not in output[sdgid]['floors']:
            output[sdgid]['floors'][floor] = {'spawns': []}
        if spawn not in output[sdgid]['floors'][floor]['spawns']:
            output[sdgid]['floors'][floor]['spawns'].append(spawn)
    with open(os.path.join(args.output_dir, "encounter_data.json"), 'w+') as f:
        json.dump(output, f)



if __name__ == '__main__':
    args = parse_args()
    load_data(args)
