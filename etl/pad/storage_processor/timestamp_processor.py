import logging

from pad.db.db_util import DbWrapper
from pad.storage.awoken_skill import AwokenSkill
from pad.storage.dungeon import Dungeon, SubDungeon
from pad.storage.encounter import Encounter
from pad.storage.monster import Monster, ActiveSkill, LeaderSkill, Awakening, Evolution
from pad.storage.rank_reward import RankReward
from pad.storage.schedule import ScheduleEvent
from pad.storage.skill_tag import ActiveSkillTag, LeaderSkillTag

logger = logging.getLogger('processor')

_UPDATE_TABLES = [
    ActiveSkill.TABLE,
    ActiveSkillTag.TABLE,
    Awakening.TABLE,
    AwokenSkill.TABLE,
    Dungeon.TABLE,
    Encounter.TABLE,
    Evolution.TABLE,
    LeaderSkill.TABLE,
    LeaderSkillTag.TABLE,
    Monster.TABLE,
    RankReward.TABLE,
    ScheduleEvent.TABLE,
    SubDungeon.TABLE,
]


class TimestampProcessor(object):
    def __init__(self):
        pass

    def process(self, db: DbWrapper):
        logger.warning('timestamp update of %s tables', len(_UPDATE_TABLES))
        for table in _UPDATE_TABLES:
            max_tstamp_sql = 'SELECT MAX(tstamp) AS tstamp FROM `{}`'.format(table)
            tstamp = db.get_single_value(max_tstamp_sql, op=int)
            update_sql = "INSERT INTO timestamps (name, tstamp) values ('{}', {}) ON DUPLICATE KEY UPDATE tstamp = {}".format(
                table, tstamp, tstamp)
            rows_updated = db.update_item(update_sql)
            if rows_updated:
                logger.info('Updated tstamp for {} to {}'.format(table, tstamp))
        logger.warning('done updating timestamps')
