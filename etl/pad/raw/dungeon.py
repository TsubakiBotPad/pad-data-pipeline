"""
Parses Dungeon and DungeonFloor data.
"""

import csv
from io import StringIO
from typing import Any, Dict, List, Optional, Set, Union

from pad.common import pad_util
from pad.common.dungeon_types import RawDungeonType, RawRepeatDay
from pad.common.pad_util import ghtime
from pad.common.shared_types import DungeonId, SubDungeonId

# The typical JSON file name for this data.
FILE_NAME = 'download_dungeon_data.json'


def maybe_int(num: str) -> Union[str, int]:
    return int(num) if num.isnumeric() else num


def default_int(modifiers: dict, key: str, default: int) -> int:
    """This exists because there are so many god damn typos in GH data"""
    try:
        return int(modifiers.get(key, default))
    except ValueError:
        return default


def parse_modifiers(mod_str: str) -> Dict[str, Union[bool, str]]:
    mods = {}
    for mod in mod_str.split('|'):
        if ':' not in mod or mod.endswith(':'):
            mods[mod.split(':')[0]] = True
            continue
        k, v = mod.split(':', 1)
        mods[k] = v.strip()
    return mods


def merge_defaults(data, defaults):
    return list(data) + defaults[len(data):]


class FixedCard(pad_util.Printable):
    """A fixed card on a subdungeon team."""

    def __init__(self, data: str, order_idx):
        data = [maybe_int(v) for v in data.rstrip(';').split(';')]
        data = merge_defaults(data, [None, 99, 0, 0, 0, 99, 99])
        (self.monster_id, self.level,
         self.plus_hp, self.plus_atk, self.plus_rcv,
         self.awakening_count, self.skill_level,
         *rest) = data

        # If the monster_id is 0, we have to make it None to show there's no monster here
        self.monster_id = self.monster_id or None

        self.latents = [0, 0, 0, 0, 0, 0]
        self.assist = 0
        self.super_awakening_id = 0

        if not rest or rest[0] == 99:
            pass
        elif rest[0] == 'a':
            self.assist = rest[1]
        else:
            self.latents = merge_defaults(rest[:6], self.latents)
            if len(rest) > 6:
                self.super_awakening_id = rest[6]

        self.order_idx = order_idx


class SubDungeon(pad_util.Printable):
    """A dungeon difficulty level."""

    def __init__(self, dungeon_id: DungeonId, raw: List[Any]):
        # https://github.com/TsubakiBotPad/pad-data-pipeline/wiki/Subdungeon-Arguments
        self.sub_dungeon_id = SubDungeonId(dungeon_id * 1000 + int(raw[0]))
        self.simple_sub_dungeon_id = int(raw[0])
        self.raw_name = self.name = raw[1]
        self.clean_name = pad_util.strip_colors(self.raw_name)
        self.floors = int(raw[2])
        self.rflags1 = int(raw[3])
        self.stamina = raw[4]
        self.bgm1 = raw[5]
        self.bgm2 = raw[6]
        self.disables = int(raw[7])

        # If monsters can use skills in this dungeon.
        self.technical = self.rflags1 & 0x80 > 0

        # This next loop runs through the elements from raw[8] until it hits a 0. The 0 indicates the end of the list
        # of drops for the floor, the following segments are the dungeon modifiers
        pos = 8
        while int(raw[pos]) != 0:
            pos += 1
        pos += 1

        flags = int(raw[pos])
        pos += 1

        self.prev_dungeon_id = None
        self.prev_floor_id = None
        self.start_timestamp = None
        self.score = None
        self.unknown_f4 = None
        pipe_hell = ""
        self.end_timestamp = None

        if flags & 1 << 0:  # Prev Floor
            self.prev_dungeon_id = int(raw[pos])
            self.prev_floor_id = int(raw[pos + 1])
            pos += 2

        if flags & 1 << 2:  # Start Timestamp
            self.start_timestamp = ghtime(raw[pos], 'utc')
            pos += 1

        if flags & 1 << 3:  # S-Rank Score
            self.score = int(raw[pos])
            pos += 1

        if flags & 1 << 4:  # Unknown Value
            self.unknown_f4 = int(raw[pos])
            pos += 1

        if flags & 1 << 6:  # Pipe Hell
            pipe_hell = raw[pos]
            pos += 1

        if flags & 1 << 7:  # Start Timestamp
            self.end_timestamp = ghtime(raw[pos], 'utc')
            pos += 1

        self.restriction_type = int(raw[pos])
        self.restriction_args = raw[pos + 1:]

        modifiers = parse_modifiers(pipe_hell)
        self.hp_mult = default_int(modifiers, 'hp', 10000) / 10000
        self.atk_mult = default_int(modifiers, 'at', 10000) / 10000
        self.def_mult = default_int(modifiers, 'df', 10000) / 10000

        self.fixed_cards: Set[FixedCard] = set()
        for idx in range(1, 6 + 1):
            if not (fc := modifiers.get(f'fc{idx}')):
                # Not all dungeons have fixed cards in all slots
                continue
            self.fixed_cards.add(FixedCard(modifiers[f'fc{idx}'], idx))

    def __str__(self):
        return 'SubDungeon({} - {})'.format(self.sub_dungeon_id, self.clean_name)


prefix_to_dungeontype = {
    # #G#Ruins of the Star Vault 25
    '#G#': 'guerrilla',

    # #1#Star Treasure of the Night Sky 25
    '#1#': 'unknown-1',

    # #C#Rurouni Kenshin dung
    '#C#': 'collab',

    # Monthly and other quests
    '#Q#': 'quest',
}


class Dungeon(pad_util.Printable):
    """A top-level dungeon."""

    def __init__(self, raw: List[Any]):
        self.sub_dungeons = []  # type: List[SubDungeon]

        self.dungeon_id = DungeonId(int(raw[0]))
        self.name = str(raw[1])

        self.bitmap_2 = int(raw[2])
        self.one_time = self.bitmap_2 & 1 > 0
        self.bg_id = self.bitmap_2 >> 4

        self.clean_name = pad_util.strip_colors(self.name)

        # Basic dungeon type computed by scanning the name for flags.
        self.dungeon_type = None  # type: Optional[str]

        # A more detailed dungeon type.
        self.full_dungeon_type = RawDungeonType(int(raw[3]))

        # This will be a day of the week, or an empty string if it doesn't repeat regularly
        self.repeat_day = RawRepeatDay(int(raw[4]))

        # Seems to relate to dungeon type?
        self._unknown_5 = int(raw[5])

        # Might have to do with the 'badge' that is shown, e.g. 102 == 'collab'
        self._unknown_6 = int(raw[6])

        # Seems related to the ordering of dungeons, but only within their 'sub group'?
        self.order = int(raw[7]) if raw[7] else None

        self.display_monster_id = int(raw[8]) if len(raw) > 8 else None

        for prefix, dungeon_type in prefix_to_dungeontype.items():
            if self.clean_name.startswith(prefix):
                self.dungeon_type = dungeon_type
                self.clean_name = self.clean_name[len(prefix):]
                break

    def __str__(self):
        return 'Dungeon({} - {})'.format(self.dungeon_id, self.clean_name)


def load_dungeon_data(data_dir: str = None, json_file: str = None) -> List[Dungeon]:
    """Converts dungeon JSON into an array of Dungeons."""
    data_json = pad_util.load_raw_json(data_dir, json_file, FILE_NAME)
    dungeon_info = data_json['dungeons']

    dungeons = []
    cur_dungeon = None

    for line in dungeon_info.split('\n'):
        info = line[0:2]
        data = line[2:]
        data = data.replace("',", "`,").replace(",'", ",`")
        data_values = next(csv.reader(StringIO(data), quotechar="`", delimiter=','))
        if info == 'd;':
            cur_dungeon = Dungeon(data_values)
            dungeons.append(cur_dungeon)
        elif info == 'f;':
            floor = SubDungeon(cur_dungeon.dungeon_id, data_values)
            cur_dungeon.sub_dungeons.append(floor)
        elif info == 'c;':
            pass
        else:
            raise ValueError('unexpected line: ' + line)

    return dungeons
