#!/usr/bin/env python3
"""
Loads the raw data files for NA/JP into intermediate structures, saves them,
then updates the database with the new data.
"""
import argparse
import json
import logging
import os

from pad.common.shared_types import Server
from pad.db.db_util import DbWrapper
from pad.raw_processor import merged_database, crossed_data
from pad.storage_processor.awoken_skill_processor import AwakeningProcessor
from pad.storage_processor.dimension_processor import DimensionProcessor
from pad.storage_processor.dungeon_content_processor import DungeonContentProcessor
from pad.storage_processor.dungeon_processor import DungeonProcessor
from pad.storage_processor.enemy_skill_processor import EnemySkillProcessor
from pad.storage_processor.exchange_processor import ExchangeProcessor
from pad.storage_processor.egg_machine_processor import EggMachineProcessor
from pad.storage_processor.purchase_processor import PurchaseProcessor
from pad.storage_processor.monster_processor import MonsterProcessor
from pad.storage_processor.rank_reward_processor import RankRewardProcessor
from pad.storage_processor.schedule_processor import ScheduleProcessor
from pad.storage_processor.series_processor import SeriesProcessor
from pad.storage_processor.skill_tag_processor import SkillTagProcessor
from pad.storage_processor.timestamp_processor import TimestampProcessor
from pad.storage_processor.purge_data_processor import PurgeDataProcessor

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

type_name_to_processor = {
    'DungeonProcessor': DungeonProcessor,
    'DungeonContentProcessor': DungeonContentProcessor,
    'ScheduleProcessor': ScheduleProcessor,
}


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def parse_args():
    parser = argparse.ArgumentParser(description="Patches the DadGuide database.", add_help=False)
    parser.register('type', 'bool', str2bool)

    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--doupdates", default=False,
                             action="store_true", help="Enables actions")
    input_group.add_argument("--logsql", default=False,
                             action="store_true", help="Logs sql commands")
    input_group.add_argument("--skipintermediate", default=False,
                             action="store_true", help="Skips the slow intermediate storage")
    input_group.add_argument("--db_config", required=True, help="JSON database info")
    input_group.add_argument("--dev", default=False, action="store_true",
                             help="Should we run dev processes")
    input_group.add_argument("--input_dir", required=True,
                             help="Path to a folder where the input data is")
    input_group.add_argument("--es_dir",
                             help="Path to a folder where the enemy skills data protos are")
    input_group.add_argument("--es_only", default=False, action="store_true",
                             help="If true, only load ES and then quit")
    input_group.add_argument("--media_dir", required=False,
                             help="Path to the root folder containing images, voices, etc")
    input_group.add_argument("--processors", required=False,
                             help="Comma-separated specific processors to run.")
    input_group.add_argument("--server", default="COMBINED", help="Server to build for")

    output_group = parser.add_argument_group("Output")
    output_group.add_argument("--output_dir", required=True,
                              help="Path to a folder where output should be saved")
    output_group.add_argument("--pretty", default=False, action="store_true",
                              help="Controls pretty printing of results")
    output_group.add_argument("--skip_long", default=False, action="store_true",
                              help="Skip slow-running loaders")

    help_group = parser.add_argument_group("Help")
    help_group.add_argument("-h", "--help", action="help",
                            help="Displays this help message and exits.")
    return parser.parse_args()


def load_es_quick_and_die(args):
    with open(args.db_config) as f:
        db_config = json.load(f)

    jp_database = merged_database.Database(Server.jp, args.input_dir)
    jp_database.load_database()
    cs_database = crossed_data.CrossServerDatabase(jp_database, jp_database, jp_database)

    db_wrapper = DbWrapper(False)
    db_wrapper.connect(db_config)

    es_processor = EnemySkillProcessor(db_wrapper, cs_database)
    es_processor.load_enemy_data(args.es_dir)

    logger.info('done loading ES')
    exit(0)


def load_data(args):
    if args.logsql:
        logging.getLogger('database').setLevel(logging.DEBUG)
    dry_run = not args.doupdates

    logger.info('Loading data')
    jp_database = merged_database.Database(Server.jp, args.input_dir)
    jp_database.load_database()

    na_database = merged_database.Database(Server.na, args.input_dir)
    na_database.load_database()

    kr_database = merged_database.Database(Server.kr, args.input_dir)
    kr_database.load_database()

    if input_args.server.lower() == "combined":
        cs_database = crossed_data.CrossServerDatabase(jp_database, na_database, kr_database, Server.jp)
    elif input_args.server.lower() == "jp":
        cs_database = crossed_data.CrossServerDatabase(jp_database, jp_database, jp_database, Server.jp)
    elif input_args.server.lower() == "na":
        cs_database = crossed_data.CrossServerDatabase(na_database, na_database, na_database, Server.na)
    elif input_args.server.lower() == "kr":
        cs_database = crossed_data.CrossServerDatabase(kr_database, kr_database, kr_database, Server.kr)
    else:
        raise ValueError()

    if args.media_dir:
        cs_database.load_extra_image_info(args.media_dir)

    if not args.skipintermediate:
        logger.info('Storing intermediate data')
        # This is supported for https://pad.chesterip.cc/ and PadSpike, until we can support it better in the dg db
        jp_database.save_all(args.output_dir, args.pretty)
        na_database.save_all(args.output_dir, args.pretty)
        # kr_database.save_all(args.output_dir, args.pretty)

    logger.info('Connecting to database')
    with open(args.db_config) as f:
        db_config = json.load(f)

    db_wrapper = DbWrapper(dry_run)
    db_wrapper.connect(db_config)

    if args.processors:
        for processor in args.processors.split(","):
            processor = processor.strip()
            logger.info('Running specific processor {}'.format(processor))
            class_type = type_name_to_processor[processor]
            processor = class_type(cs_database)
            processor.process(db_wrapper)
        logger.info('done')
        return

    # Load dimension tables
    DimensionProcessor().process(db_wrapper)

    # # Load rank data
    RankRewardProcessor().process(db_wrapper)

    # # Ensure awakenings
    AwakeningProcessor().process(db_wrapper)

    # # Ensure tags
    SkillTagProcessor().process(db_wrapper)

    # # Load enemy skills
    es_processor = EnemySkillProcessor(db_wrapper, cs_database)
    es_processor.load_static()
    es_processor.load_enemy_skills()
    if args.es_dir:
        es_processor.load_enemy_data(args.es_dir)

    # Load basic series data
    series_processor = SeriesProcessor(cs_database)
    series_processor.pre_process(db_wrapper)

    # # Load monster data
    MonsterProcessor(cs_database).process(db_wrapper)

    # Auto-assign monster series
    series_processor.post_process(db_wrapper)

    # Egg machines
    EggMachineProcessor(cs_database).process(db_wrapper)

    # Load dungeon data
    dungeon_processor = DungeonProcessor(cs_database)
    dungeon_processor.process(db_wrapper)
    if not args.skip_long:
        # Load dungeon data derived from wave info
        DungeonContentProcessor(cs_database).process(db_wrapper)

    # Toggle any newly-available dungeons visible
    dungeon_processor.post_encounter_process(db_wrapper)

    # Load event data
    ScheduleProcessor(cs_database).process(db_wrapper)

    # Load exchange data
    ExchangeProcessor(cs_database).process(db_wrapper)

    # Load purchase data
    PurchaseProcessor(cs_database).process(db_wrapper)

    # Update timestamps
    TimestampProcessor().process(db_wrapper)

    PurgeDataProcessor().process(db_wrapper)

    logger.info('done')


if __name__ == '__main__':
    try:
        input_args = parse_args()

        os.environ['CURRENT_PIPELINE_SERVER'] = input_args.server.strip()

        if input_args.server.lower() not in ("combined", "jp", "na", "kr"):
            raise ValueError("Server must be COMBINED, JP, NA, KR.")

        # This is a hack to make loading ES easier and more frequent.
        # Remove this once we're done with most of the ES processing.
        if input_args.es_dir and input_args.es_only:
            load_es_quick_and_die(input_args)

        # This needs to be done after the es_quick check otherwise it will consistently overwrite the fixes file.
        if os.name != 'nt':
            human_fix_logger.addHandler(logging.FileHandler('/tmp/dadguide_pipeline_human_fixes.txt', mode='w'))

        load_data(input_args)
    finally:
        del os.environ['CURRENT_PIPELINE_SERVER']
