import argparse
import json
import logging
import time

from pad.api import pad_api

from pad.db.db_util import DbWrapper
from pad.storage.wave import WaveItem


def parse_args():
    parser = argparse.ArgumentParser(description="Extracts PAD dungeon data.", add_help=False)

    input_group = parser.add_argument_group("Input")
    input_group.add_argument("--server", required=True, help="One of [NA, JP]")
    input_group.add_argument("--user_uuid", required=True, help="Account UUID")
    input_group.add_argument("--user_intid", required=True, help="Account code")

    input_group.add_argument("--dungeon_id", required=True, help="Dungeon ID")
    input_group.add_argument("--floor_id", required=True, help="Floor ID")
    input_group.add_argument("--loop_count", type=int, default=100, help="Number of entry attempts")

    output_group = parser.add_argument_group("Output")
    output_group.add_argument("--db_config", required=True, help="JSON database info")
    output_group.add_argument("--logsql", default=False,
                              action="store_true", help="Logs sql commands")

    help_group = parser.add_argument_group("Help")
    help_group.add_argument("-h", "--help", action="help",
                            help="Displays this help message and exits.")

    return parser.parse_args()


def pull_data(args):
    if args.logsql:
        logging.getLogger('database').setLevel(logging.DEBUG)

    server = args.server.upper()
    endpoint = None
    if server == 'NA':
        endpoint = pad_api.ServerEndpoint.NA
    elif server == 'JP':
        endpoint = pad_api.ServerEndpoint.JA
    else:
        raise Exception('unexpected server:' + args.server)

    api_client = pad_api.PadApiClient(endpoint, args.user_uuid, args.user_intid)

    print('login')
    api_client.login()

    print('load_player_data')
    api_client.load_player_data()

    friend_card = api_client.get_any_card_except_in_cur_deck()
    dungeon_id = args.dungeon_id
    floor_id = args.floor_id
    loop_count = args.loop_count
    pull_id = int(time.time())

    print('Connecting to database')
    with open(args.db_config) as f:
        db_config = json.load(f)

    dry_run = False
    db_wrapper = DbWrapper(dry_run)
    db_wrapper.connect(db_config)
    entry_id = int(db_wrapper.get_single_value("SELECT MAX(entry_id) FROM wave_data;"))

    print('entering dungeon', dungeon_id, 'floor', floor_id, loop_count, 'times')
    for e_idx in range(loop_count):
        print('entering', e_idx)
        entry_id += 1
        entry_json = api_client.enter_dungeon(dungeon_id, floor_id, self_card=friend_card)
        wave_response = pad_api.extract_wave_response_from_entry(entry_json)
        leaders = entry_json['entry_leads']

        for stage_idx, floor in enumerate(wave_response.floors):
            for monster_idx, monster in enumerate(floor.monsters):
                wave_item = WaveItem(pull_id=pull_id, entry_id=entry_id, server=server, dungeon_id=dungeon_id,
                                     floor_id=floor_id, stage=stage_idx, slot=monster_idx, monster=monster,
                                     leader_id=leaders[0], friend_id=leaders[1])
                db_wrapper.insert_item(wave_item.insert_sql())

        if server != 'NA':
            time.sleep(.5)


if __name__ == '__main__':
    input_args = parse_args()
    pull_data(input_args)
