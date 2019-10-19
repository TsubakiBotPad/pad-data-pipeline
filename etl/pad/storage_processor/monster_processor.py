import logging

from pad.common import pad_util
from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.storage.monster import LeaderSkill, ActiveSkill, Monster, Awakening, Evolution

logger = logging.getLogger('processor')
human_fix_logger = logging.getLogger('human_fix')


class MonsterProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.data = data

    def process(self, db: DbWrapper):
        logger.warning('loading monster data')
        self._process_skills(db)
        self._process_monsters(db)
        self._process_awakenings(db)
        self._process_evolutions(db)
        logger.warning('done loading monster data')

    def _process_skills(self, db: DbWrapper):
        logger.warning('loading skills for %s cards', len(self.data.ownable_cards))
        ls_count = 0
        as_count = 0
        for m in self.data.ownable_cards:
            if m.jp_card.leader_skill:
                ls_count += 1
                db.insert_or_update(
                    LeaderSkill.from_ls(m.jp_card.leader_skill, m.na_card.leader_skill, m.kr_card.leader_skill))
            if m.jp_card.active_skill:
                as_count += 1
                db.insert_or_update(
                    ActiveSkill.from_as(m.jp_card.active_skill, m.na_card.active_skill, m.kr_card.active_skill))

        logger.warning('loaded %s leader skills and %s active skills', ls_count, as_count)

    def _process_monsters(self, db):
        logger.warning('loading %s monsters', len(self.data.ownable_cards))
        for m in self.data.ownable_cards:
            item = Monster.from_csm(m)
            db.insert_or_update(item)

    def _process_awakenings(self, db):
        logger.warning('loading awakenings')
        for m in self.data.ownable_cards:
            items = Awakening.from_csm(m)
            for item in items:
                try:
                    db.insert_or_update(item)
                except:
                    human_fix_logger.fatal('Failed to insert item (probably new awakening): %s',
                                           pad_util.json_string_dump(item, pretty=True))

    def _process_evolutions(self, db):
        logger.warning('loading evolutions')
        for m in self.data.ownable_cards:
            if not m.jp_card.card.ancestor_id:
                continue

            ancestor_id = m.jp_card.no_to_id(m.jp_card.card.ancestor_id)
            ancestor = self.data.card_by_monster_id(ancestor_id)
            item = Evolution.from_csm(m, ancestor)
            if item:
                db.insert_or_update(item)
