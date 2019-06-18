"""
Parses Dungeon and DungeonFloor data.
"""

import csv
import json
import os
from io import StringIO
from typing import List, Any

from pad.common import pad_util, dungeon_types

# The typical JSON file name for this data.
FILE_NAME = 'download_dungeon_data.json'


class DungeonFloor(pad_util.Printable):
    """A floor listed once you click into a Dungeon."""

    def __init__(self, raw: List[Any]):
        self.floor_number = int(raw[0])
        self.raw_name = raw[1]
        self.clean_name = pad_util.strip_colors(self.raw_name)
        self.waves = int(raw[2])
        self.rflags1 = raw[3]
        self.stamina = raw[4]
        self.bgm1 = raw[5]
        self.bgm2 = raw[6]
        self.rflags2 = int(raw[7])

        # This next loop runs through the elements from raw[8] until it hits a 0. The 0 indicates the end of the list
        # of drops for the floor, the following segments are the dungeon modifiers
        pos = 8
        while int(raw[pos]) is not 0:
            pos += 1
        pos += 1

        self.flags = int(raw[pos])
        self.remaining_fields = raw[pos + 1:]

        # Modifiers parsing doesn't seem to always work
        # Hacked up version for dungeon modifiers, needed for
        # enemy parsing.
        self.modifiers_clean = {
            'hp': 1.0,
            'atk': 1.0,
            'def': 1.0,
        }

        for field in self.remaining_fields:
            if 'hp:' in field or 'at:' in field or 'df:' in field:
                for mod in field.split('|'):
                    if mod.startswith('hp:'):
                        self.modifiers_clean['hp'] = float(mod[3:]) / 10000
                    elif mod.startswith('at:'):
                        self.modifiers_clean['atk'] = float(mod[3:]) / 10000
                    elif mod.startswith('df:'):
                        self.modifiers_clean['def'] = float(mod[3:]) / 10000
                break

        # Modifiers parsing also seems to skip fixed teams sometimes.
        # Hacked up version for just that here.
        self.fixed_team = {}

        for field in self.remaining_fields:
            if not 'fc1' in field:
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
        self.floors = []  # type: List[DungeonFloor]

        self.dungeon_id = int(raw[0])
        self.name = str(raw[1])
        self.unknown_002 = int(raw[2])

        self.clean_name = pad_util.strip_colors(self.name)

        # Temporary hack. The newly added 'Guerrilla' type doesn't seem to be correct, and that's
        # the only type actively in use. Using the old logic for now.
        self.dungeon_type = None # type: str

        # A more detailed dungeon type.
        self.full_dungeon_type = dungeon_types.RawDungeonType(int(raw[3]))

        # This will be a day of the week, or an empty string if it doesn't repeat regularly
        self.repeat_day = dungeon_types.RawRepeatDay(int(raw[4]))

        for prefix, dungeon_type in prefix_to_dungeontype.items():
            if self.clean_name.startswith(prefix):
                self.dungeon_type = dungeon_type
                self.clean_name = self.clean_name[len(prefix):]
                break

    def __str__(self):
        return 'Dungeon({} - {})'.format(self.dungeon_id, self.clean_name)


def load_dungeon_data(data_dir: str = None, dungeon_file: str = None) -> List[Dungeon]:
    """Converts dungeon JSON into an array of Dungeons."""
    if dungeon_file is None:
        dungeon_file = os.path.join(data_dir, FILE_NAME)

    with open(dungeon_file) as f:
        dungeon_json = json.load(f)

    dungeon_info = dungeon_json['dungeons']

    dungeons = []
    cur_dungeon = None

    for line in dungeon_info.split('\n'):
        info = line[0:2]
        data = line[2:]
        data_values = next(csv.reader(StringIO(data), quotechar="'"))
        if info == 'd;':
            cur_dungeon = Dungeon(data_values)
            dungeons.append(cur_dungeon)
        elif info == 'f;':
            floor = DungeonFloor(data_values)
            cur_dungeon.floors.append(floor)
        elif info == 'c;':
            pass
        else:
            raise ValueError('unexpected line: ' + line)

    return dungeons
