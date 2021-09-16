"""
Pulls data files for specified account/server.

Requires padkeygen which is not checked in.
"""
import argparse
import os

from pad.api import pad_api
from pad.common import pad_util
from pad.common.shared_types import Server
from pad.raw import bonus, extra_egg_machine

parser = argparse.ArgumentParser(description="Extracts PAD API data.", add_help=False)

inputGroup = parser.add_argument_group("Input")
inputGroup.add_argument("--server", required=True, help="One of [NA, JP, KR]")
inputGroup.add_argument("--user_uuid", required=True, help="Account UUID")
inputGroup.add_argument("--user_intid", required=True, help="Account code")
inputGroup.add_argument("--user_group", required=True, help="Expected user group")
inputGroup.add_argument("--only_bonus", action='store_true', help="Only populate bonus data")

outputGroup = parser.add_argument_group("Output")
outputGroup.add_argument("--output_dir", required=True,
                         help="Path to a folder where output should be saved")

helpGroup = parser.add_argument_group("Help")
helpGroup.add_argument("-h", "--help", action="help", help="Displays this help message and exits.")
args = parser.parse_args()

endpoint = None
server = None
if args.server == 'NA':
    endpoint = pad_api.ServerEndpoint.NA
    server = Server.na
elif args.server == 'JP':
    endpoint = pad_api.ServerEndpoint.JA
    server = Server.jp
elif args.server == 'KR':
    endpoint = pad_api.ServerEndpoint.KR
    server = Server.kr
else:
    raise Exception('unexpected server:' + args.server)

api_client = pad_api.PadApiClient(endpoint, args.user_uuid, args.user_intid)

user_group = args.user_group.lower()
output_dir = args.output_dir
os.makedirs(output_dir, exist_ok=True)

api_client.login()


def pull_and_write_endpoint(api_client, action, file_name_suffix=''):
    action_json = api_client.action(action)

    file_name = '{}{}.json'.format(action.value.name, file_name_suffix)
    output_file = os.path.join(output_dir, file_name)
    print('writing', file_name)
    with open(output_file, 'w') as outfile:
        pad_util.json_file_dump(action_json, outfile)


pull_and_write_endpoint(api_client, pad_api.EndpointAction.DOWNLOAD_LIMITED_BONUS_DATA,
                        file_name_suffix='_{}'.format(user_group))

if args.only_bonus:
    print('skipping other downloads')
    exit()

pull_and_write_endpoint(api_client, pad_api.EndpointAction.DOWNLOAD_CARD_DATA)
pull_and_write_endpoint(api_client, pad_api.EndpointAction.DOWNLOAD_DUNGEON_DATA)
pull_and_write_endpoint(api_client, pad_api.EndpointAction.DOWNLOAD_SKILL_DATA)
pull_and_write_endpoint(api_client, pad_api.EndpointAction.DOWNLOAD_ENEMY_SKILL_DATA)
pull_and_write_endpoint(api_client, pad_api.EndpointAction.DOWNLOAD_MONSTER_EXCHANGE)
pull_and_write_endpoint(api_client, pad_api.EndpointAction.SHOP_ITEM)

api_client.load_player_data()
player_data = api_client.player_data
bonus_data = bonus.load_bonus_data(data_dir=output_dir,
                                   data_group=user_group,
                                   server=server)

# Egg machine extraction
egg_machines = extra_egg_machine.load_from_player_data(data_json=player_data.egg_data, server=server)
egg_machines.extend(extra_egg_machine.machine_from_bonuses(server, bonus_data, 'rem_event', 'Rare Egg Machine'))
egg_machines.extend(extra_egg_machine.machine_from_bonuses(server, bonus_data, 'pem_event', 'Pal Egg Machine'))
egg_machines.extend(extra_egg_machine.machine_from_bonuses(server, bonus_data, 'fem_event', 'Free Egg Machine'))

for em in egg_machines:
    if not em.is_open():
        # Can only pull rates when the machine is live.
        continue

    grow = em.egg_machine_row
    gtype = em.egg_machine_type
    page = api_client.get_egg_machine_page(gtype, grow)
    extra_egg_machine.scrape_machine_contents(page, em)

output_file = os.path.join(output_dir, extra_egg_machine.FILE_NAME)
with open(output_file, 'w') as outfile:
    pad_util.json_file_dump(egg_machines, outfile, pretty=True)
