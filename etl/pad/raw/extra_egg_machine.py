"""
Parses the extra egg machine data.
"""

import json
import os
import time
from typing import Dict, List, Any

from bs4 import BeautifulSoup

from pad.api.pad_api import PadApiClient
from pad.common import pad_util

# The typical JSON file name for this data.
from pad.common.shared_types import Server, JsonType
from pad.raw.bonus import Bonus

FILE_NAME = 'egg_machines.json'


class ExtraEggMachine(pad_util.Printable):
    """Egg machines extracted from the player data json."""

    def __init__(self, raw: Dict[str, Any], server: Server, gtype: int):
        self.name = str(raw['name'])
        self.server = server
        self.clean_name = pad_util.strip_colors(self.name)

        # Start time as gungho time string
        self.start_time_str = str(raw['start'])
        self.start_timestamp = pad_util.gh_to_timestamp_2(self.start_time_str, server)

        # End time as gungho time string
        self.end_time_str = str(raw['end'])
        self.end_timestamp = pad_util.gh_to_timestamp_2(self.end_time_str, server)

        # TODO: extra egg machine parser needs to pull out comment
        self.comment = str(raw.get('comment', ''))
        self.clean_comment = pad_util.strip_colors(self.comment)

        # The egg machine ID used in the API call param grow
        self.egg_machine_row = int(raw['row'])

        # The egg machine ID used in the API call param gtype
        # Corresponds to the ordering of the item in egatya3
        self.egg_machine_type = gtype

        # Not sure exactly how this is used
        self.alt_egg_machine_type = int(raw['type'])

        # Stone or pal point cost
        self.cost = int(raw['pri'])

        # Monster ID to %
        self.contents = {}

    def is_open(self):
        current_time = int(time.time())
        return self.start_timestamp < current_time < self.end_timestamp

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return 'ExtraEggMachine({}/{} - {})'.format(self.egg_machine_row, self.egg_machine_type, self.clean_name)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def load_data(data_dir: str = None,
              json_file: str = None,
              data_json: JsonType = None,
              server: Server = None) -> List[ExtraEggMachine]:
    """Load ExtraEggMachine objects from the json file."""
    # We get some data from the player info struct instead of a file
    if data_json is None:
        data_json = pad_util.load_raw_json(data_dir, json_file, FILE_NAME)
    egg_machines = []
    # gtype starts at 52 and goes up by 10 for every egg machine slot.
    gtype = 52
    for outer in data_json:
        if outer:
            for em in outer:
                egg_machines.append(ExtraEggMachine(em, server, gtype))
        gtype += 10
    return egg_machines


def machine_from_bonuses(server: Server,
                         bonus_data: List[Bonus],
                         machine_code: str,
                         machine_name: str) -> List[ExtraEggMachine]:
    """Extracts pem and rem info from the bonus listing."""
    m_events = [x for x in bonus_data if x.bonus_name == machine_code and x.is_open()]
    # Probably should only be one of these
    em_events = []
    for event in m_events:
        em_events.append({
            'name': machine_name,
            'comment': event.message,
            'start': event.start_time_str,
            'end': event.end_time_str,
            'row': event.egg_machine_id,
            'type': 1 if event.bonus_name == 'pem_event' else 2,
            # pri can actually be found in another event but it's probably safe to fix it.
            'pri': 500 if event.bonus_name == 'pem_event' else 5,
        })

    return [ExtraEggMachine(em, server, em['type']) for em in em_events]


def scrape_machine_contents(api_client: PadApiClient, egg_machine: ExtraEggMachine):
    """Pulls the HTML page with egg machine contents and scrapes out the monsters/rates."""
    grow = egg_machine.egg_machine_row
    gtype = egg_machine.egg_machine_type
    has_rate = egg_machine.name != 'Pal Egg Machine'
    min_cols = 2 if has_rate else 1

    page = api_client.get_egg_machine_page(gtype, grow)
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.table

    if not table:
        print('Egg machine scrape failed:', gtype, grow)
        print(page)
        return

    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < min_cols:
            continue

        if has_rate:
            # Some rows can be size 3 (left header)
            name_chunk = cols[-2].a['href']
            rate_chunk = cols[-1].text.replace('%', '')
            rate = round(float(rate_chunk) / 100, 4)
        else:
            # Some rows can be size 2 (left header)
            name_chunk = cols[-1].a['href']
            rate = 0

        name_id = name_chunk[name_chunk.rfind('=') + 1:]
        egg_machine.contents[int(name_id)] = rate
