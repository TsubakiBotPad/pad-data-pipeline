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
        logger.info('done loading dungeon data')

    def post_encounter_process(self, db: DbWrapper):
        logger.info('post-encounter processing')
        updated_rows = db.update_item(_ENCOUNTER_VISIBILITY_SQL)
        logger.info('Updated visibility of %s dungeons', updated_rows)

    def _process_dungeons(self, db: DbWrapper):
        logger.info('loading %s dungeons', len(self.data.dungeons))
        for dungeon in self.data.dungeons:
            db.insert_or_update(Dungeon.from_csd(dungeon))
            for subdungeon in dungeon.sub_dungeons:
                db.insert_or_update(SubDungeon.from_cssd(subdungeon, dungeon.dungeon_id))
                if not subdungeon.cur_sub_dungeon.fixed_monsters:
                    continue
                db.insert_or_update(FixedTeam.from_cssd(subdungeon))
                for fcid in range(6):
                    fixed = subdungeon.cur_sub_dungeon.fixed_monsters.get(fcid)
                    db.insert_or_update(FixedTeamMonster.from_fc(fixed, fcid, subdungeon))
