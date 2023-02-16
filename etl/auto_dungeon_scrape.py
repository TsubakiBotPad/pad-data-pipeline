import argparse
import json
import logging
import os
import time

from pad.api import pad_api
from pad.api.pad_api import BadResponseCode
from pad.common.dungeon_types import RawDungeonType
from pad.common.shared_types import Server
from pad.db import db_util
from pad.raw.bonus import BonusType
from pad.raw_processor import merged_database
from pad_dungeon_pull import pull_data

logger = logging.getLogger('autodungeon')
logger.setLevel(logging.INFO)

human_fix_logger = logging.getLogger('human_fix')
human_fix_logger.disabled = True

fail_logger = logging.getLogger('processor_failures')
logger.setLevel(logging.INFO)

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
    input_group.add_argument("--user_uuid", required=True, help="Account UUID")
    input_group.add_argument("--user_intid", required=True, help="Account code")

    input_group.add_argument("--minimum_wave_count", default=1000, type=int,
                             help="Minimum stored wave count to skip loading wave data")
    input_group.add_argument("--maximum_wave_age", default=90, type=int,
                             help="Number of days before wave data becomes obsolete and needs to be reloaded")

    output_group = parser.add_argument_group("Output")
    output_group.add_argument("--doupdates", default=False,
                              action="store_true", help="Apply updates")
    output_group.add_argument("--stream_safe", action="store_true", help="Don't use fancy progress bars")

    help_group = parser.add_argument_group("Help")
    help_group.add_argument("-h", "--help", action="help",
                            help="Displays this help message and exits.")

    return parser.parse_args()


class Arg:
    pass


def do_dungeon_load(args, dungeon_id, floor_id, api_client, db_wrapper, stam_adjust=False):
    if not args.doupdates:
        print('skipping due to dry run')
        return

    dg_pull_arg = Arg()
    dg_pull_arg.base_dir = args.input_dir
    dg_pull_arg.db_config = args.db_config
    dg_pull_arg.server = args.server
    dg_pull_arg.user_uuid = args.user_uuid
    dg_pull_arg.user_intid = args.user_intid
    dg_pull_arg.floor_id = floor_id
    dg_pull_arg.dungeon_id = dungeon_id
    dg_pull_arg.loop_count = 100
    dg_pull_arg.logsql = False
    dg_pull_arg.stream_safe = args.stream_safe
    dg_pull_arg.stam_adjust = stam_adjust
    pull_data(dg_pull_arg, api_client, db_wrapper)


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


def load_dungeons(args, db_wrapper, current_dungeons, api_client):
    """Scrapes data for all current dungeons.

    If there is not enough 'new' data, we try to scrape data.
    If we have an acceptable amount of data and we have 'old' data, migrate it
    to a backup database and then purge it.

    We only purge if we have an acceptable amount of new data to prevent us from
    erasing useful data for dungeons we can't actually enter.
    """

    for dungeon in current_dungeons:
        dungeon_id = dungeon.dungeon_id
        print(f'Processing {dungeon.clean_name} ({dungeon_id})')
        if dungeon.full_dungeon_type == RawDungeonType.EIGHT_PLAYER:
            print('Skipping 8 player dungeon.')
            continue

        minimum_wave_count = args.minimum_wave_count
        if dungeon_id in EXTRA_RUN_DUNGEONS:
            print('Variable dungeon. Increasing the wave count')
            minimum_wave_count *= 10

        for sub_dungeon in dungeon.sub_dungeons:
            floor_id = sub_dungeon.simple_sub_dungeon_id

            wave_info = db_wrapper.get_single_or_no_row(
                CHECK_AGE_SQL.format(age=args.maximum_wave_age, dungeon_id=dungeon_id, floor_id=floor_id))
            older_count = int(wave_info["older"] or 0)
            newer_count = int(wave_info["newer"] or 0)

            should_enter = newer_count < minimum_wave_count
            print(f'Entries for floor {floor_id} ({sub_dungeon.clean_name}):'
                  f' old={older_count} new={newer_count} entering={should_enter}')

            relogged = False
            stam_adjust = False
            while should_enter:
                try:
                    do_dungeon_load(args, dungeon_id, floor_id, api_client, db_wrapper, stam_adjust)
                except BadResponseCode as brc:
                    if brc.code == 2 and not relogged:
                        relogged = True
                        print("Attempting Relog...")
                        api_client.login()
                        api_client.load_player_data()
                        continue
                    elif brc.code == 8:
                        print(f"Failed to enter. Skipping dungeon. ({brc})")
                        fail_logger.debug(f"Failed to enter dungeon {dungeon.clean_name} ({dungeon_id})"
                                          f" on floor {floor_id}.\n{brc}")
                    elif brc.code == 54:
                        if not stam_adjust:
                            stam_adjust = True
                            print("Trying 0 stamina...")
                            continue
                        else:
                            print(f"Could not enter dungeon. ({brc})")
                    elif brc.code != 0:
                        raise
                break

            wave_info = db_wrapper.get_single_or_no_row(
                CHECK_AGE_SQL.format(age=args.maximum_wave_age, dungeon_id=dungeon_id, floor_id=floor_id))
            older_count = int(wave_info["older"] or 0)
            newer_count = int(wave_info["newer"] or 0)

            should_purge = older_count > 0 and newer_count >= minimum_wave_count
            print(f'Entries for floor {floor_id}: old={older_count} new={newer_count} purging={should_purge}')

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


def identify_dungeons(database, bonuses=None):
    selected_dungeons = []

    # Identify normals and technicals
    for dungeon in database.dungeons:
        if dungeon.one_time:
            continue
        if dungeon.full_dungeon_type in (RawDungeonType.NORMAL, RawDungeonType.TECHNICAL):
            selected_dungeons.append(dungeon)

    # Identify special dungeons from bonuses
    current_time = int(time.time())
    for bonus in database.bonuses:
        start_time = bonus.bonus.start_timestamp
        end_time = bonus.bonus.end_timestamp

        if current_time < start_time or current_time > end_time:
            # Bonus not currently live
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

    if bonuses is not None:
        bonuses = [b for b in bonuses if b.start_timestamp <= time.time() <= b.end_timestamp]
        bonus_dgs = {b.dungeon_id for b in bonuses if b.dungeon_id is not None}
        bonus_dgs.update(b.sub_dungeon_id // 1000 for b in bonuses if b.sub_dungeon_id is not None)
        print(bonus_dgs)
        print([b for b in bonuses if b.dungeon_id == 10])
        selected_dungeons = [d for d in selected_dungeons if d.dungeon_id in bonus_dgs]

    return selected_dungeons


def load_data(args):
    server = Server.from_str(args.server)

    if os.name != 'nt':
        fail_logger.addHandler(logging.FileHandler('/tmp/autodungeon_processor_issues.txt', mode='w'))

    pad_db = merged_database.Database(server, args.input_dir)
    pad_db.load_database(skip_skills=True, skip_extra=True)

    with open(args.db_config) as f:
        db_config = json.load(f)

    dry_run = not args.doupdates
    db_wrapper = db_util.DbWrapper(dry_run)
    db_wrapper.connect(db_config)

    bonuses = [b.bonus for b in pad_db.bonuses]
    dungeons = identify_dungeons(pad_db, bonuses)

    if server == Server.na:
        endpoint = pad_api.ServerEndpoint.NA
    elif server == Server.jp:
        endpoint = pad_api.ServerEndpoint.JA
    else:
        raise Exception('unexpected server:' + args.server)

    api_client = pad_api.PadApiClient(endpoint, args.user_uuid, args.user_intid)
    api_client.login()
    print('load_player_data')
    api_client.load_player_data()

    load_dungeons(args, db_wrapper, dungeons, api_client)


if __name__ == '__main__':
    arguments = parse_args()
    load_data(arguments)
