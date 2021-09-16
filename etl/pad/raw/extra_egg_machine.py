"""
Parses the extra egg machine data.
"""

import time
from typing import Any, Dict, List

from bs4 import BeautifulSoup

from pad.common import pad_util
from pad.common.shared_types import Server
from pad.raw.bonus import Bonus

# The typical JSON file name for this data.
FILE_NAME = 'egg_machines.json'


class ExtraEggMachine(pad_util.Printable):
    """Egg machines extracted from the player data json."""

    def __init__(self, raw: Dict[str, Any], server: Server):
        self.name = str(raw['name'])
        self.clean_name = pad_util.strip_colors(self.name)

        # Start time as gungho time string
        self.start_time_str = str(raw.get('start', raw.get('start_time_str')))
        self.start_timestamp = pad_util.gh_to_timestamp_2(self.start_time_str, server)

        # End time as gungho time string
        self.end_time_str = str(raw.get('end', raw.get('end_time_str')))
        self.end_timestamp = pad_util.gh_to_timestamp_2(self.end_time_str, server)

        # TODO: extra egg machine parser needs to pull out comment
        self.comment = str(raw.get('comment', ''))
        self.clean_comment = pad_util.strip_colors(self.comment)

        # The egg machine ID used in the API call param grow
        self.egg_machine_row = int(raw.get('row', raw.get('egg_machine_row')))

        # The egg machine ID used in the API call param gtype
        # Corresponds to the ordering of the item in egatya3
        self.egg_machine_type = int(raw['egg_machine_type'])

        # Stone or pal point cost
        self.cost = int(raw.get('pri', raw.get('cost')))

        # Monster ID to %
        contents = raw.get('contents', {})
        self.contents = {int(k): v for k, v in contents.items()}

    def is_open(self):
        current_time = int(time.time())
        return self.start_timestamp < current_time < self.end_timestamp

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return 'ExtraEggMachine({}/{} - {})'.format(self.egg_machine_row, self.egg_machine_type, self.clean_name)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def load_from_player_data(
        data_json=None,
        server: Server = None) -> List[ExtraEggMachine]:
    """Load ExtraEggMachine objects from the player data json file."""
    egg_machines = []
    # gtype starts at 52 and goes up by 10 for every egg machine slot.
    gtype = 52
    for outer in data_json:
        if outer:
            for em in outer:
                em['egg_machine_type'] = gtype
                egg_machines.append(ExtraEggMachine(em, server))
        gtype += 10
    return egg_machines


def load_data(data_dir: str = None,
              json_file: str = None,
              server: Server = None) -> List[ExtraEggMachine]:
    """Load ExtraEggMachine objects from the saved json file."""
    data_json = pad_util.load_raw_json(data_dir, json_file, FILE_NAME)
    return [ExtraEggMachine(item, server) for item in data_json]


def machine_from_bonuses(server: Server,
                         bonus_data: List[Bonus],
                         machine_code: str,
                         machine_name: str) -> List[ExtraEggMachine]:
    """Extracts pem and rem info from the bonus listing."""
    m_events = [x for x in bonus_data if x.bonus_name == machine_code and x.is_open()]
    if machine_code == 'pem_event':
        em_type = 1
        price = 500
    elif machine_code == 'rem_event':
        em_type = 2
        price = 5
    elif machine_code == 'fem_event':
        em_type = 9
        price = 0
    else:
        raise ValueError("Invalid machine_code")

    # Probably should only be one of these
    em_events = []
    for event in m_events:
        em_events.append({
            'name': machine_name,
            'comment': event.message,
            'start': event.start_time_str,
            'end': event.end_time_str,
            'row': event.egg_machine_id,
            'egg_machine_type': em_type,
            # pri can actually be found in another event but it's probably safe to fix it.
            'pri': price,
        })

    return [ExtraEggMachine(em, server) for em in em_events]


def scrape_machine_contents(page: str, egg_machine: ExtraEggMachine):
    """Pulls the HTML page with egg machine contents and scrapes out the monsters/rates."""
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.table

    if not table:
        print('Egg machine scrape failed:', egg_machine.egg_machine_row, egg_machine.egg_machine_type)
        print(page)
        return

    has_rate = egg_machine.egg_machine_type not in (1, 9)
    min_cols = 2 if has_rate else 1

    rows = table.find_all('tr')
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < min_cols:
            continue

        if has_rate:
            # Some rows can be size 3 (left header) or size 4 (right remdra sublist)
            remdra = bool(cols[-1].a)

            name_chunk = cols[-2 - remdra].a['href']
            rate_chunk = cols[-1 - remdra].text.replace('%', '')
            rate = round(float(rate_chunk) / 100, 4)
        else:
            # Some rows can be size 2 (left header)
            name_chunk = cols[-1].a['href']
            rate = 0

        name_id = name_chunk[name_chunk.rfind('=') + 1:]
        egg_machine.contents[int(name_id)] = rate
