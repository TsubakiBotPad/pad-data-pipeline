import logging

from pad.db.db_util import DbWrapper
from pad.db.sql_item import SimpleSqlItem
from pad.storage.awoken_skill import AwokenSkill
from pad.storage.monster import Monster, ActiveSkill, LeaderSkill, Awakenings, Evolution

logger = logging.getLogger('processor')

_UPDATE_TABLES = [
    AwokenSkill.TABLE,
    # Monster.TABLE,
    # ActiveSkill.TABLE,
    # LeaderSkill.TABLE,
    # Awakenings.TABLE,
    # Evolution.TABLE,
]


class Timestamp(SimpleSqlItem):
    """Table update timestamp."""
    TABLE = 'timestamps'
    KEY_COL = 'name'

    def __init__(self, name: str = None, tstamp: int = None):
        self.name = name
        self.tstamp = tstamp


class TimestampProcessor(object):
    def __init__(self):
        pass

    def process(self, db: DbWrapper):
        logger.warning('timestamp update of %s tables', len(_UPDATE_TABLES))
        for table in _UPDATE_TABLES:
            max_tstamp_sql = 'SELECT MAX(tstamp) AS tstamp FROM `{}`'.format(table)
            tstamp = db.get_single_value(max_tstamp_sql, op=int)

            db.insert_or_update(Timestamp(table, tstamp))
        logger.warning('done updating timestamps')
