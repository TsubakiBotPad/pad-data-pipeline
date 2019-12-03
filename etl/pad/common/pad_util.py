import datetime
import json
import os
import re
from typing import Union

import pytz

from pad.common.shared_types import JsonType, Printable, Server, dump_helper, ListJsonType

# Re-exporting these types; should fix imports
Printable = Printable
dump_helper = dump_helper


def strip_colors(message: str) -> str:
    return re.sub(r'(?i)[$^][a-f0-9]{6}[$^]', '', message)


def ghmult(x: int) -> str:
    """Normalizes multiplier to a human-readable number."""
    mult = x / 10000
    if int(mult) == mult:
        mult = int(mult)
    return '%sx' % mult


def ghmult_plain(x: int) -> str:
    """Normalizes multiplier to a human-readable number (without decorations)."""
    mult = x / 10000
    if int(mult) == mult:
        mult = int(mult)
    return '{}'.format(mult)


def ghchance(x: int) -> str:
    """Normalizes percentage to a human-readable number."""
    assert x % 100 == 0
    return '%d%%' % (x // 100)


def ghchance_plain(x: int) -> str:
    """Normalizes percentage to a human-readable number (without decorations)."""
    assert x % 100 == 0
    return '%d%%' % (x // 100)


# TODO: Change this to take Server
def ghtime(time_str: str, server: str) -> datetime.datetime:
    """Converts a time string into a datetime."""
    # <  151228000000
    # >  2015-12-28 00:00:00
    server = server.lower()
    server = 'jp' if server == 'ja' else server
    tz_offsets = {
        'na': '-0800',
        'jp': '+0900',
        'kr': '+0900',
    }
    timezone_str = '{} {}'.format(time_str, tz_offsets[server])
    return datetime.datetime.strptime(timezone_str, '%y%m%d%H%M%S %z')


def gh_to_timestamp_2(time_str: str, server: Server) -> int:
    """Converts a time string to a timestamp."""
    dt = ghtime(time_str, server.name)
    return int(dt.timestamp())


def datetime_to_gh(dt):
    # Assumes timezone is set properly
    return dt.strftime('%y%m%d%H%M%S')


class NoDstWestern(datetime.tzinfo):
    def utcoffset(self, *dt):
        return datetime.timedelta(hours=-8)

    def tzname(self, dt):
        return "NoDstWestern"

    def dst(self, dt):
        return datetime.timedelta(hours=-8)


def cur_gh_time(server):
    server = server.lower()
    server = 'jp' if server == 'ja' else server
    tz_offsets = {
        'na': NoDstWestern(),
        'jp': pytz.timezone('Asia/Tokyo'),
        'kr': pytz.timezone('Asia/Tokyo'),
    }
    return datetime_to_gh(datetime.datetime.now(tz_offsets[server]))


def internal_id_to_display_id(i_id: int) -> str:
    """Permutes internal PAD ID to the displayed form."""
    i_id = str(i_id).zfill(9)
    return ''.join(i_id[x - 1] for x in [1, 5, 9, 6, 3, 8, 2, 4, 7])


def display_id_to_group(d_id: str) -> str:
    """Converts the display ID into the group name (a,b,c,d,e)."""
    return chr(ord('a') + (int(d_id[2]) % 5))


def internal_id_to_group(i_id: str) -> str:
    """Converts the internal ID into the group name (a,b,c,d,e)."""
    return chr(ord('a') + (int(i_id) % 5))


def identify_server(json_file: str, server: str) -> str:
    """Determine the proper server."""
    if server:
        return server.lower()
    for st in ['na', 'jp', 'kr']:
        if '/{}/'.format(st) in json_file or '\\{}\\'.format(st) in json_file:
            return st
    raise Exception('Server not supplied and not automatically detected from path')


def load_raw_json(data_dir: str = None, json_file: str = None, file_name: str = None) -> Union[JsonType, ListJsonType]:
    """Load JSON file."""
    if json_file is None:
        json_file = os.path.join(data_dir, file_name)

    with open(json_file, encoding='utf-8') as f:
        return json.load(f)


def json_string_dump(obj, pretty=False):
    indent = 4 if pretty else None
    return json.dumps(obj, indent=indent, sort_keys=True, default=dump_helper, ensure_ascii=False)


def json_file_dump(obj, f, pretty=False):
    indent = 4 if pretty else None
    json.dump(obj, f, indent=indent, sort_keys=True, default=dump_helper, ensure_ascii=False)
