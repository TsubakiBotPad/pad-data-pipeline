import logging
from typing import List

from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.raw_processor.merged_data import MergedBonus
from pad.storage.schedule import ScheduleEvent

logger = logging.getLogger('processor')


class ScheduleProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.data = data

    def process(self, db: DbWrapper):
        logger.warning('loading JP events')
        self._process_schedule(db, self.data.jp_bonuses)
        logger.warning('loading NA events')
        self._process_schedule(db, self.data.na_bonuses)
        logger.warning('done loading schedule data')

    def _process_schedule(self, db: DbWrapper, bonuses: List[MergedBonus]):
        for bonus in bonuses:
            if not bonus.dungeon:
                continue
            # TODO: handle other events
            # TODO: handle dungeon events properly
            event = ScheduleEvent.from_mb(bonus)
            db.insert_or_update(event)
