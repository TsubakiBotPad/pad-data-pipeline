"""
Parses the extra egg machine data.
"""

import json
import os
import time
from typing import Dict, List, Any

from pad.common import pad_util

# The typical JSON file name for this data.
from pad.common.shared_types import Server, JsonType

FILE_NAME = 'extra_egg_machines.json'


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
