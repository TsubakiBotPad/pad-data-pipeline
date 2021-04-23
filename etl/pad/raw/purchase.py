"""
Parses monster purchase data.
"""

import json
import os
from typing import List

from pad.common import pad_util
from pad.common.pad_util import Printable
from pad.common.shared_types import Server

FILE_NAME = 'shop_item.json'


class Purchase(Printable):
    """Buyable monsters."""

    def __init__(self, raw: List[str], server: Server, tbegin: str, tend: str):
        self.server = server
        self.start_time_str = tbegin
        self.start_timestamp = pad_util.gh_to_timestamp_2(self.start_time_str, server)
        self.end_time_str = tend
        self.end_timestamp = pad_util.gh_to_timestamp_2(self.end_time_str, server)
        self.type = str(raw[0])  # Should be P

        # Trade monster ID
        self.monster_id = int(raw[1])

        # Cost of the monster in MP
        self.cost = int(raw[2])

        # Probably amount.  Always 1
        self.amount = int(raw[3])

        # A None and two 0s
        self.unknown = raw[4:]

    def __str__(self):
        return 'Purchase({} {} - {})'.format(self.server, self.monster_id, self.cost)


def load_data(server: Server, data_dir: str = None, json_file: str = None) -> List[Purchase]:
    """Load Card objects from PAD JSON file."""
    data_json = pad_util.load_raw_json(data_dir, json_file, FILE_NAME)
    start_time, end_time = None, None
    mpbuys = []
    for item in filter(None, data_json['d'].split('\n')):
        raw = item.split(',')
        if raw[0] == 'T':
            start_time = raw[1]
            end_time = raw[2]
        else:
            p = Purchase(raw, server, start_time, end_time)
            mpbuys.append(p)
    return mpbuys  # This will have a lot or repeats, but that shouldn't matter
