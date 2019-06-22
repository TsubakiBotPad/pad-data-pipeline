"""
Loads the raw data files for NA/JP into intermediate structures, saves them,
then updates the database with the new data.
"""
import argparse
from collections import defaultdict
from datetime import timedelta
import json
import logging
import os
import time

# import feedparser
# from pad.common import monster_id_mapping
from pad.common.shared_types import Server
from pad.db.db_util import DbWrapper
from pad.raw_processor import merged_database, crossed_data

# from pad.processor import skill_info, merged_data
# from pad.storage import egg
# from pad.storage import egg_processor
# from pad.storage import monster
# from pad.storage import monster_skill
# from pad.storage import skill_data
# from pad.storage import timestamp_processor
#
# from pad.storage.db_util import DbWrapper
# from pad.storage.news import NewsItem
# from pad.storage.schedule_item import ScheduleItem
from pad.storage_processor.awoken_skill_processor import AwakeningProcessor
from pad.storage_processor.dimension_processor import DimensionProcessor
from pad.storage_processor.timestamp_processor import TimestampProcessor

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

logger = logging.getLogger('processor')
logger.setLevel(logging.DEBUG)

fail_logger = logging.getLogger('processor_failures')
fail_logger.setLevel(logging.INFO)

db_logger = logging.getLogger('database')
db_logger.setLevel(logging.INFO)

human_fix_logger = logging.getLogger('human_fix')
if os.name != 'nt':
    human_fix_logger.addHandler(logging.FileHandler('/tmp/pipeline_human_fixes.txt', mode='w'))
human_fix_logger.setLevel(logging.INFO)


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def parse_args():
    parser = argparse.ArgumentParser(description="Patches the DadGuide database.", add_help=False)
    parser.register('type', 'bool', str2bool)

    inputGroup = parser.add_argument_group("Input")
    inputGroup.add_argument("--doupdates", default=False,
                            action="store_true", help="Enables actions")
    inputGroup.add_argument("--logsql", default=False,
                            action="store_true", help="Logs sql commands")
    inputGroup.add_argument("--skipintermediate", default=False,
                            action="store_true", help="Skips the slow intermediate storage")
    inputGroup.add_argument("--db_config", required=True, help="JSON database info")
    inputGroup.add_argument("--dev", default=False, action="store_true",
                            help="Should we run dev processes")
    inputGroup.add_argument("--input_dir", required=True,
                            help="Path to a folder where the input data is")

    outputGroup = parser.add_argument_group("Output")
    outputGroup.add_argument("--output_dir", required=True,
                             help="Path to a folder where output should be saved")
    outputGroup.add_argument("--pretty", default=False, action="store_true",
                             help="Controls pretty printing of results")

    helpGroup = parser.add_argument_group("Help")
    helpGroup.add_argument("-h", "--help", action="help",
                           help="Displays this help message and exits.")
    return parser.parse_args()



def load_data(args):
    if args.logsql:
        logging.getLogger('database').setLevel(logging.DEBUG)
    dry_run = not args.doupdates

    input_dir = args.input_dir
    output_dir = args.output_dir

    logger.info('Loading data')
    jp_database = merged_database.Database(Server.JP, input_dir)
    jp_database.load_database()

    na_database = merged_database.Database(Server.NA, input_dir)
    na_database.load_database()

    cs_database = crossed_data.CrossServerDatabase(jp_database, na_database, na_database)

    logger.info('Connecting to database')
    with open(args.db_config) as f:
        db_config = json.load(f)

    dry_run = False
    db_wrapper = DbWrapper(dry_run)
    db_wrapper.connect(db_config)

    # Load dimension tables
    DimensionProcessor().process(db_wrapper)

    # Ensure awakenings
    AwakeningProcessor().process(db_wrapper)

    # Update timestamps
    TimestampProcessor().process(db_wrapper)

    # cs_database.dungeon_diagnostics()
    # cs_database.card_diagnostics()

    print('done')

    # if not args.skipintermediate:
    #     logger.info('Storing intermediate data')
    #     jp_database.save_all(output_dir, args.pretty)
    #     na_database.save_all(output_dir, args.pretty)
    #
    # logger.info('Connecting to database')
    # with open(args.db_config) as f:
    #     db_config = json.load(f)
    #
    # db_wrapper = DbWrapper(dry_run)
    # db_wrapper.connect(db_config)
    #
    # cross_server_dungeons = merged_data.build_cross_server_dungeons(jp_database, na_database)
    # logger.info('Starting JP event diff')
    # database_diff_events(db_wrapper, jp_database, cross_server_dungeons)
    #
    # logger.info('Starting NA event diff')
    # database_diff_events(db_wrapper, na_database, cross_server_dungeons)
    #
    # logger.info('Starting card diff')
    # database_diff_cards(db_wrapper, jp_database, na_database)
    #
    # logger.info('Starting egg machine update')
    # try:
    #     database_update_egg_machines(db_wrapper, jp_database, na_database)
    # except Exception as ex:
    #     print('updating egg machines failed', str(ex))
    #
    # logger.info('Starting news update')
    # try:
    #     database_update_news(db_wrapper)
    # except Exception as ex:
    #     print('updating news failed', str(ex))
    #
    # logger.info('Starting tstamp update')
    # timestamp_processor.update_timestamps(db_wrapper)
    #
    # print('done')


if __name__ == '__main__':
    args = parse_args()
    load_data(args)