import logging

from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.storage.dungeon import Dungeon, SubDungeon

logger = logging.getLogger('processor')

_ENCOUNTER_VISIBILITY_SQL = """
UPDATE dungeons 
SET visible = true, tstamp = UNIX_TIMESTAMP() 
WHERE dungeon_id IN (select dungeon_id  from encounters group by 1)
AND visible = false
"""


class DungeonProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.data = data

    def process(self, db: DbWrapper):
        logger.info('loading dungeon data')
        self._process_dungeons(db)
        self._process_subdungeons(db)
        logger.info('done loading dungeon data')

    def post_encounter_process(self, db: DbWrapper):
        logger.info('post-encounter processing')
        updated_rows = db.update_item(_ENCOUNTER_VISIBILITY_SQL)
        logger.info('Updated visibility of %s dungeons', updated_rows)

    def _process_dungeons(self, db: DbWrapper):
        logger.info('loading %s dungeons', len(self.data.dungeons))
        for dungeon in self.data.dungeons:
            item = Dungeon.from_csd(dungeon)
            db.insert_or_update(item)
        logger.info('done loading dungeons')

    def _process_subdungeons(self, db: DbWrapper):
        logger.info('loading sub_dungeons')
        for dungeon in self.data.dungeons:
            items = SubDungeon.from_csd(dungeon)
            for item in items:
                db.insert_or_update(item)
        logger.info('done loading subdungeons')
