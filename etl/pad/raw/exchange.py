"""
Parses monster exchange data.
"""

import json
import os
from typing import List

from pad.common import pad_util
from pad.common.pad_util import Printable

# The typical JSON file name for this data.
from pad.common.shared_types import Server

FILE_NAME = 'mdatadl.json'


class Exchange(Printable):
    """Exchangeable monsters, options to exhange, and any event text."""

    def __init__(self, raw: List[str], server: Server):
        self.unknown_000 = str(raw[0])  # Seems to always be 'A'

        # Seems to be the unique ID for the trade?
        self.trade_id = int(raw[1])

        # Seems to be an order field, with lower values towards the top?
        self.display_order = int(raw[2])

        # 1-indexed menu this appears in
        self.menu_idx = int(raw[3])

        # Trade monster ID
        self.monster_id = int(raw[4])

        self.unknown_005 = int(raw[5])  # 1 (all examples checked)
        self.unknown_006 = int(raw[6])  # 0 (all examples checked)

        # Trade availability start time string
        self.start_time_str = str(raw[7])
        self.start_timestamp = pad_util.gh_to_timestamp_2(self.start_time_str, server)

        # Trade availability end time string
        self.end_time_str = str(raw[8])
        self.end_timestamp = pad_util.gh_to_timestamp_2(self.end_time_str, server)

        # Start time string for the announcement text, probably?
        self.announcement_start_time_str = str(raw[9])
        self.announcement_start_timestamp = pad_util.gh_to_timestamp_2(
            self.announcement_start_time_str, server) if self.announcement_start_time_str else ''

        # End time string for the announcement text, probably?
        self.announcement_end_time_str = str(raw[10])
        self.announcement_end_timestamp = pad_util.gh_to_timestamp_2(
            self.announcement_end_time_str, server) if self.announcement_end_time_str else ''

        # Optional text that appears above monster name, for limited time events
        self.announcement_text = str(raw[11])

        # Clean version of the announcement text without formatting
        self.announcement_text_clean = pad_util.strip_colors(self.announcement_text)

        # Number of required monsters for the trade
        self.required_count = int(raw[12])

        # Seems to be the 'flag' type, e.g. 'restricted'?
        # If so, 0=No Flag, 2='Restricted'.
        self.flag_type = int(raw[13])

        # Options for trading the monster
        self.required_monsters = list(map(int, raw[14:]))

    def __str__(self):
        return 'Exchange({} - {} - {}/{})'.format(self.monster_id, len(self.required_monsters),
                                                  self.start_time_str, self.end_time_str)


def load_data(server: Server, data_dir: str = None, json_file: str = None) -> List[Exchange]:
    """Load Card objects from PAD JSON file."""
    data_json = pad_util.load_raw_json(data_dir, json_file, FILE_NAME)
    return [Exchange(item.split(','), server) for item in data_json['d'].split('\n')]
