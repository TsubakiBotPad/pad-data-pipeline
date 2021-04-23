from pad.db.db_util import DbWrapper
from pad.dungeon import wave_converter
from pad.raw.dungeon import Dungeon
from pad.raw_processor import crossed_data

# Finds any dungeon with no encounters set up that has an entry
# in the wave_data table.
from pad.raw_processor.crossed_data import CrossServerDungeon
from pad.storage.wave import WaveItem

FIND_DUNGEONS_SQL = """
SELECT dungeon_id
FROM dungeons
INNER JOIN encounters
  USING (dungeon_id)
WHERE icon_id IS NULL
AND dungeon_id IN (
  SELECT dungeon_id FROM padguide.wave_data GROUP BY 1
)
ORDER BY dungeon_id ASC
"""


# TODO: Consider renaming subdungeon to floor for consistency

class WaveProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.data = data

    def process(self, db: DbWrapper):
        ready_dungeons = db.fetch_data(FIND_DUNGEONS_SQL)
        for row in ready_dungeons:
            dungeon_id = row['dungeon_id']
            dungeon = self.data.dungeon_by_id(dungeon_id)

            self._process_dungeon(db, dungeon)

    def _process_dungeon(self, db: DbWrapper, dungeon: CrossServerDungeon):
        waves = db.load_multiple_objects(WaveItem, dungeon.dungeon_id)
        result_stage = wave_converter.process_waves(self.data, waves)
        print('finished computing results for', dungeon.dungeon_id, dungeon.na_dungeon.name)
