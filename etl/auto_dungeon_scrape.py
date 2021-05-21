import argparse
import json
import logging
import subprocess
import time

from pad.common.dungeon_types import RawDungeonType
from pad.common.shared_types import Server
from pad.db import db_util
from pad.raw.bonus import BonusType
from pad.raw_processor import merged_database
from pad_dungeon_pull import pull_data

fail_logger = logging.getLogger('human_fix')
fail_logger.disabled = True

# Dungeons in this list should have twice the minimum wave count.
# They just have too much variability to get by on a normal scrape size.
EXTRA_RUN_DUNGEONS = [
    110,  # Endless Corridors
    1625,  # Ultimate Descended Rush
    2660,  # Alt Ultimate Arena
    4247,  # All Days (gems)
    4267,  # Multiplayer UDR
    4268,  # Multiplayer Endless Coridors
    4269,  # Multiplayer Evo Rush (gems)
]


def parse_args():
    parser = argparse.ArgumentParser(description="Automatically scrape dungeons.", add_help=False)

    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--db_config", required=True, help="JSON database info")
    input_group.add_argument("--input_dir", required=True,
                             help="Path to a folder where the input data is")

    input_group.add_argument("--server", required=True, help="na or jp")
    input_group.add_argument("--group", required=True, help="guerrilla group (red/blue/green)")
    input_group.add_argument("--user_uuid", required=True, help="Account UUID")
    input_group.add_argument("--user_intid", required=True, help="Account code")

    input_group.add_argument("--minimum_wave_count", default=60, type=int,
                             help="Minimum stored wave count to skip loading wave data")
    input_group.add_argument("--maximum_wave_age", default=90, type=int,
                             help="Number of days before wave data becomes obsolete and needs to be reloaded")

    output_group = parser.add_argument_group("Output")
    output_group.add_argument("--doupdates", default=False,
                              action="store_true", help="Apply updates")

    help_group = parser.add_argument_group("Help")
    help_group.add_argument("-h", "--help", action="help",
                            help="Displays this help message and exits.")

    return parser.parse_args()


class Arg:
    pass


def do_dungeon_load(args, dungeon_id, floor_id):
    if not args.doupdates:
        print('skipping due to dry run')
        return

    dg_pull_arg = Arg()
    dg_pull_arg.db_config = args.db_config
    dg_pull_arg.server = args.server
    dg_pull_arg.user_uuid = args.user_uuid
    dg_pull_arg.user_intid = args.user_intid
    dg_pull_arg.floor_id = floor_id
    dg_pull_arg.dungeon_id = dungeon_id
    dg_pull_arg.loop_count = 20
    dg_pull_arg.logsql = False
    pull_data(dg_pull_arg)


CHECK_AGE_SQL = '''
SELECT
  SUM(CASE WHEN DATEDIFF(NOW(), pull_time) >= {age} THEN 1 ELSE 0 END) AS older,
  SUM(CASE WHEN DATEDIFF(NOW(), pull_time) < {age} THEN 1 ELSE 0 END) AS newer
FROM (
    SELECT entry_id, pull_time
    FROM wave_data
    WHERE dungeon_id={dungeon_id} AND floor_id={floor_id}
    GROUP BY 1, 2
) AS entry_id_pull_time
'''

MIGRATE_OLD_DATA_SQL = '''
INSERT INTO dadguide_wave_backup.wave_data
SELECT * FROM wave_data
WHERE dungeon_id={dungeon_id} AND floor_id={floor_id} AND DATEDIFF(NOW(), pull_time) >= {age};
'''

DELETE_OLD_DATA_SQL = '''
DELETE FROM wave_data
WHERE dungeon_id={dungeon_id} AND floor_id={floor_id} AND DATEDIFF(NOW(), pull_time) >= {age};
'''


def load_dungeons(args, db_wrapper, current_dungeons):
    """Scrapes data for all current dungeons.

    If there is not enough 'new' data, we try to scrape data.
    If we have an acceptable amount of data and we have 'old' data, migrate it
    to a backup database and then purge it.

    We only purge if we have an acceptable amount of new data to prevent us from
    erasing useful data for dungeons we can't actually enter.
    """

    for dungeon in current_dungeons:
        dungeon_id = dungeon.dungeon_id
        print('processing', dungeon.clean_name, dungeon_id)

        minimum_wave_count = args.minimum_wave_count
        if dungeon_id in EXTRA_RUN_DUNGEONS:
            print('variable dungeon, doubling the wave count')
            minimum_wave_count *= 2

        for sub_dungeon in dungeon.sub_dungeons:
            floor_id = sub_dungeon.simple_sub_dungeon_id

            wave_info = db_wrapper.get_single_or_no_row(
                CHECK_AGE_SQL.format(age=args.maximum_wave_age, dungeon_id=dungeon_id, floor_id=floor_id))
            older_count = int(wave_info["older"] or 0)
            newer_count = int(wave_info["newer"] or 0)

            should_enter = newer_count < minimum_wave_count
            print('entries for {} : old={} new={} entering={}'.format(floor_id, older_count, newer_count, should_enter))
            if should_enter:
                do_dungeon_load(args, dungeon_id, floor_id)

            wave_info = db_wrapper.get_single_or_no_row(
                CHECK_AGE_SQL.format(age=args.maximum_wave_age, dungeon_id=dungeon_id, floor_id=floor_id))
            older_count = int(wave_info["older"] or 0)
            newer_count = int(wave_info["newer"] or 0)

            should_purge = older_count > 0 and newer_count >= minimum_wave_count
            print('entries for {} : old={} new={} purging={}'.format(floor_id, older_count, newer_count, should_purge))

            # This section cleans up 'old' data. We consider data to be out of date if approximately 3 months have
            # passed. If we have the opportunity to scrape a dungeon (e.g. a collab) that comes back, we will. It will
            # also ensure that the normal/technical data is up to date.
            if should_purge:
                try:
                    db_wrapper.connection.autocommit(False)
                    with db_wrapper.connection.cursor() as cursor:
                        sql = MIGRATE_OLD_DATA_SQL.format(age=args.maximum_wave_age,
                                                          dungeon_id=dungeon_id,
                                                          floor_id=floor_id)
                        db_wrapper.execute(cursor, sql)
                        migrate_count = cursor.rowcount
                        if migrate_count < older_count:  # The older_count is the number of entries, this is raw rows
                            db_wrapper.connection.rollback()
                            raise ValueError('wrong migrate count:', migrate_count, 'vs', older_count)

                        sql = DELETE_OLD_DATA_SQL.format(age=args.maximum_wave_age,
                                                         dungeon_id=dungeon_id,
                                                         floor_id=floor_id)
                        db_wrapper.execute(cursor, sql)
                        delete_count = cursor.rowcount
                        if delete_count != migrate_count:  # Compare what we migrated against what we deleted
                            db_wrapper.connection.rollback()
                            raise ValueError('wrong delete count:', delete_count, 'vs', migrate_count)

                        db_wrapper.connection.commit()
                        print('migration complete')
                except Exception as ex:
                    print('failed to migrate data:', ex)
                finally:
                    db_wrapper.connection.autocommit(True)


def identify_dungeons(database, group):
    selected_dungeons = []

    # Identify normals and technicals
    for dungeon in database.dungeons:
        if dungeon.one_time:
            continue
        if dungeon.full_dungeon_type in [RawDungeonType.NORMAL, RawDungeonType.TECHNICAL]:
            selected_dungeons.append(dungeon)

    # Identify special dungeons from bonuses
    current_time = int(time.time())
    for bonus in database.bonuses:
        start_time = bonus.start_timestamp
        end_time = bonus.end_timestamp

        if current_time < start_time or current_time > end_time:
            # Bonus not currently live
            continue

        if bonus.group and bonus.group.value != group:
            # Not the right color
            continue

        if bonus.dungeon is None:
            # Only check bonuses with dungeons
            continue

        bonus_type = bonus.bonus.bonus_info.bonus_type
        if bonus_type not in [
            BonusType.dungeon,  # This is the actual dungeon for an active bonus
            BonusType.tournament_active,  # This is an active ranking dungeon
        ]:
            continue

        selected_dungeons.append(bonus.dungeon)

    return selected_dungeons


def load_data(args):
    server = Server.from_str(args.server)

    pad_db = merged_database.Database(server, args.input_dir)
    pad_db.load_database(skip_skills=True, skip_extra=True)

    with open(args.db_config) as f:
        db_config = json.load(f)

    dry_run = not args.doupdates
    db_wrapper = db_util.DbWrapper(dry_run)
    db_wrapper.connect(db_config)

    dungeons = identify_dungeons(pad_db, args.group)

    load_dungeons(args, db_wrapper, dungeons)


if __name__ == '__main__':
    args = parse_args()
    load_data(args)
