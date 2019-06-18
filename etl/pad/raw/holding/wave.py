import csv
import os
from typing import List

from pad.common.pad_util import Printable


class WaveResponse(Printable):
    def __init__(self, wave_data):
        """Converts the raw enemy dungeon wave response into an object."""
        self.floors = [WaveFloor(floor) for floor in wave_data]


class WaveFloor(Printable):
    def __init__(self, floor_data):
        """Converts the raw stage response data into an object."""
        self.monsters = [WaveMonster(monster) for monster in floor_data]


class WaveMonster(Printable):
    def __init__(self, monster_data):
        """Converts the raw spawn response data into an object."""
        self.spawn_type = monster_data[0]  # Dungeon trigger maybe? Mostly 0, last is 1
        self.monster_id = monster_data[1]
        self.monster_level = monster_data[2]
        self.drop_monster_id = monster_data[3]
        self.drop_monster_level = monster_data[4]
        self.plus_amount = monster_data[5]


class WaveSummary(Printable):
    def __init__(self,
                 dungeon_id: int = 0,
                 floor_id: int = 0,
                 stage: int = 0,
                 spawn_type: int = 0,
                 monster_id: int = 0,
                 monster_level: int = 0,
                 row_count: int = 0):
        self.dungeon_id = dungeon_id
        self.floor_id = floor_id
        self.stage = stage
        self.spawn_type = spawn_type
        self.monster_id = monster_id
        self.monster_level = monster_level
        self.row_count = row_count


def load_wave_summary(processed_input_dir) -> List[WaveSummary]:
    wave_summary_file = os.path.join(processed_input_dir, 'wave_summary.csv')
    results = []
    with open(wave_summary_file) as f:
        csvreader = csv.reader(f, delimiter=',', quotechar='"')
        next(csvreader)
        for row in csvreader:
            results.append(WaveSummary(
                dungeon_id=int(row[0]),
                floor_id=int(row[1]),
                stage=int(row[2]),
                spawn_type=int(row[3]),
                monster_id=int(row[4]),
                monster_level=int(row[5]),
                row_count=int(row[6])))
    return results
