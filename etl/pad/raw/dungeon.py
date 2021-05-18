"""
Parses Dungeon and DungeonFloor data.
"""

import csv
import re
from io import StringIO
from typing import List, Any

from pad.common import pad_util, dungeon_types
# The typical JSON file name for this data.
from pad.common.shared_types import DungeonId, SubDungeonId

FILE_NAME = 'download_dungeon_data.json'


class SubDungeon(pad_util.Printable):
    """A dungeon difficulty level."""

    def __init__(self, dungeon_id: DungeonId, raw: List[Any]):
        self.sub_dungeon_id = SubDungeonId(dungeon_id * 1000 + int(raw[0]))
        self.simple_sub_dungeon_id = int(raw[0])
        self.raw_name = self.name = raw[1]
        self.clean_name = pad_util.strip_colors(self.raw_name)
        self.floors = int(raw[2])
        self.rflags1 = int(raw[3])
        self.stamina = raw[4]
        self.bgm1 = raw[5]
        self.bgm2 = raw[6]
        self.rflags2 = int(raw[7])

        # If monsters can use skills in this dungeon.
        self.technical = self.rflags1 & 0x80 > 0

        # This next loop runs through the elements from raw[8] until it hits a 0. The 0 indicates the end of the list
        # of drops for the floor, the following segments are the dungeon modifiers
        pos = 8
        while int(raw[pos]) != 0:
            pos += 1
        pos += 1

        self.flags = int(raw[pos])
        self.remaining_fields = raw[pos + 1:]

        # Modifiers parsing doesn't seem to always work
        # Hacked up version for dungeon modifiers, needed for
        # enemy parsing.
        self.hp_mult = 1.0
        self.atk_mult = 1.0
        self.def_mult = 1.0

        for field in self.remaining_fields:
            if 'hp:' in field or 'at:' in field or 'df:' in field:
                for k, v in re.findall(r'(\w{2}):(\d+)', field):
                    if k == 'hp':
                        self.hp_mult = float(v) / 10000
                    elif k == 'at':
                        self.atk_mult = float(v) / 10000
                    elif k == 'df':
                        self.def_mult = float(v) / 10000
                break

        # Modifiers parsing also seems to skip fixed teams sometimes.
        # Hacked up version for just that here.
        self.fixed_team = {}

        for field in self.remaining_fields:
            if not 'fc1' in field:
                continue
            else:
                # TODO: this broke, look into re-enabling it
                continue
            for sub_field in field.split('|'):
                if not sub_field.startswith('fc'):
                    continue
                idx = int(sub_field[2])
                contents = sub_field[4:]
                details = contents.split(';')
                full_record = len(details) > 1
                self.fixed_team[idx] = {
                    'monster_id': details[0],
                    'hp_plus': details[1] if full_record else 0,
                    'atk_plus': details[2] if full_record else 0,
                    'rcv_plus': details[3] if full_record else 0,
                    'awakening_count': details[4] if full_record else 0,
                    'skill_level': details[5] if full_record else 0,
                }

        # This code imported from Rikuu, need to clean it up and merge
        # with the other modifiers parsing code. For now just importing
        # the score parsing, needed for dungeon loading.
        self.score = None
        i = 0

        if (self.flags & 0x1) != 0:
            i += 2
            # self.requirement = {
            #  dungeonId: Number(self.remaining_fields[i++]),
            #  floorId: Number(self.remaining_fields[i++])
            # };
        if (self.flags & 0x4) != 0:
            i += 1
            # self.beginTime = fromPADTime(self.remaining_fields[i++]);
        if (self.flags & 0x8) != 0:
            self.score = int(self.remaining_fields[i])
            i += 1
        if (self.flags & 0x10) != 0:
            i += 1
            # self.minRank = Number(self.remaining_fields[i++]);
        if (self.flags & 0x40) != 0:
            i += 1
            # self.properties = self.remaining_fields[i++].split('|');


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
        self.full_dungeon_type = dungeon_types.RawDungeonType(int(raw[3]))

        # This will be a day of the week, or an empty string if it doesn't repeat regularly
        self.repeat_day = dungeon_types.RawRepeatDay(int(raw[4]))

        # Seems to relate to dungeon type?
        self._unknown_5 = int(raw[5])

        # Might have to do with the 'badge' that is shown, e.g. 102 == 'collab'
        self._unknown_6 = int(raw[6])

        # Seems related to the ordering of dungeons, but only within their 'sub group'?
        self.order = int(raw[7]) if raw[7] else None

        self.remaining_fields = raw[8:]

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
