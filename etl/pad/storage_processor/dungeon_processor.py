import logging

from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.storage.dungeon import Dungeon
from pad.storage.monster import LeaderSkill, ActiveSkill, Monster, Awakenings, Evolution

logger = logging.getLogger('processor')


class DungeonProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.data = data

    def process(self, db: DbWrapper):
        logger.warning('loading dungeon data')
        self._process_dungeons(db)
        self._process_subdungeons(db)
        logger.warning('done loading dungeon data')

    def _process_dungeons(self, db: DbWrapper):
        logger.warning('loading %s dungeons', len(self.data.dungeons))
        for dungeon in self.data.dungeons:
            item = Dungeon.from_csd(dungeon)
            db.insert_or_update(item)

        logger.warning('done loading dungeons')

    def _process_subdungeons(self, db):
        logger.warning('loading subdungeons')
        for dungeon in self.data.dungeons:
            pass
        logger.warning('done loading subdungeons')
