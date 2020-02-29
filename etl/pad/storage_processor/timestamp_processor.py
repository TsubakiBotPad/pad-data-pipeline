import logging
import datetime

from pad.db.db_util import DbWrapper
from pad.storage.awoken_skill import AwokenSkill
from pad.storage.dungeon import Dungeon, SubDungeon
from pad.storage.egg_machine import EggMachine
from pad.storage.encounter import Encounter
from pad.storage.enemy_skill import EnemySkill, EnemyData
from pad.storage.monster import Monster, ActiveSkill, LeaderSkill, Awakening, Evolution
from pad.storage.rank_reward import RankReward
from pad.storage.schedule import ScheduleEvent
from pad.storage.series import Series
from pad.storage.skill_tag import ActiveSkillTag, LeaderSkillTag
from pad.storage.exchange import Exchange
from pad.storage.purchase import Purchase

logger = logging.getLogger('processor')

_UPDATE_TABLES = [
    ActiveSkill.TABLE,
    ActiveSkillTag.TABLE,
    Awakening.TABLE,
    AwokenSkill.TABLE,
    # This is a special table that gets populated when items are deleted from other tables.
    'deleted_rows',
    Dungeon.TABLE,
    Encounter.TABLE,
    EggMachine.TABLE,
    EnemySkill.TABLE,
    EnemyData.TABLE,
    Evolution.TABLE,
    Exchange.TABLE,
    Purchase.TABLE,
    LeaderSkill.TABLE,
    LeaderSkillTag.TABLE,
    Monster.TABLE,
    RankReward.TABLE,
    ScheduleEvent.TABLE,
    Series.TABLE,
    SubDungeon.TABLE,
]


class TimestampProcessor(object):
    def __init__(self):
        pass

    def process(self, db: DbWrapper):
        logger.info('timestamp update of %s tables', len(_UPDATE_TABLES))
        for table in _UPDATE_TABLES:
            max_tstamp_sql = 'SELECT MAX(tstamp) AS tstamp FROM `{}`'.format(table)
            tstamp = db.get_single_value(max_tstamp_sql, op=int, fail_on_empty=False)
            if tstamp is None:
                logger.error('Skipping tstamp update for {}'.format(table))
                continue
            update_sql = "INSERT INTO timestamps (name, tstamp) values ('{}', {}) ON DUPLICATE KEY UPDATE tstamp = {}".format(
                table, tstamp, tstamp)
            rows_updated = db.update_item(update_sql)
            if rows_updated:
                logger.info('Updated tstamp for {} to {}'.format(table, tstamp))
        logger.info('done updating timestamps')
