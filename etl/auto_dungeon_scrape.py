import argparse
import json
import subprocess
import time

from pad.common.dungeon_types import RawDungeonType
from pad.common.shared_types import Server
from pad.db import db_util
from pad.raw.bonus import BonusType
from pad.raw_processor import merged_database


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

    output_group = parser.add_argument_group("Output")
    output_group.add_argument("--doupdates", default=False,
                              action="store_true", help="Apply updates")

    help_group = parser.add_argument_group("Help")
    help_group.add_argument("-h", "--help", action="help",
                            help="Displays this help message and exits.")

    return parser.parse_args()


def do_dungeon_load(args, dungeon_id, floor_id):
    if not args.doupdates:
        print('skipping due to dry run')
        return
    dungeon_script = '/home/tactical0retreat/dadguide/dadguide-data/etl/pad_dungeon_pull.py'
    process_args = [
        'python3',
        dungeon_script,
        '--db_config={}'.format(args.db_config),
        '--server={}'.format(args.server),
        '--dungeon_id={}'.format(dungeon_id),
        '--floor_id={}'.format(floor_id),
        '--user_uuid={}'.format(args.user_uuid),
        '--user_intid={}'.format(args.user_intid),
        '--loop_count=20',
    ]
    p = subprocess.run(process_args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print(str(p.stdout))
    print(str(p.stderr))


def load_dungeons(args, db_wrapper, current_dungeons):
    for dungeon in current_dungeons:
        dungeon_id = dungeon.dungeon_id
        print(dungeon.clean_name, dungeon_id)

        for sub_dungeon in dungeon.sub_dungeons:
            floor_id = sub_dungeon.simple_sub_dungeon_id
            sql = 'select count(distinct entry_id) from wave_data where dungeon_id={} and floor_id={}'.format(
                dungeon_id, floor_id)
            wave_count = db_wrapper.get_single_value(sql, op=int)
            print(wave_count, 'entries for', floor_id)
            if wave_count >= 20:
                print('skipping')
            else:
                print('entering', dungeon_id, floor_id)
                do_dungeon_load(args, dungeon_id, floor_id)


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

        if bonus.bonus.bonus_info.bonus_type != BonusType.dungeon:
            # Filter farther to just the actual dungeon entry
            continue

        selected_dungeons.append(bonus.dungeon)

    return selected_dungeons


def load_data(args):
    if args.server == 'jp':
        server = Server.jp
    elif args.server == 'na':
        server = Server.na
    elif args.server == 'kr':
        server = Server.kr
    else:
        raise ValueError('unexpected argument: ' + args.server)

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
