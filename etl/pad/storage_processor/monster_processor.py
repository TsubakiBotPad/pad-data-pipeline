import logging

from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.storage.monster import LeaderSkill, ActiveSkill, Monster, Awakenings, Evolution

logger = logging.getLogger('processor')


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
        skill_id_to_crossed_skills = {css.skill_id: css for css in self.data.skills}

        # Identify every skill ID currently in use across all servers.
        ls_in_use = set()
        as_in_use = set()
        for m in self.data.ownable_cards:
            ls_in_use.update(filter(None, [
                m.jp_card.leader_skill_id,
                m.na_card.leader_skill_id,
                m.kr_card.leader_skill_id,
            ]))
            as_in_use.update(filter(None, [
                m.jp_card.active_skill_id,
                m.na_card.active_skill_id,
                m.kr_card.active_skill_id,
            ]))

        logger.warning('loading %s in-use leader skills', len(ls_in_use))
        for ls_skill_id in ls_in_use:
            ls_css = skill_id_to_crossed_skills[ls_skill_id]
            db.insert_or_update(LeaderSkill.from_css(ls_css))

        logger.warning('loading %s in-use active skills', len(as_in_use))
        for as_skill_id in as_in_use:
            as_css = skill_id_to_crossed_skills[as_skill_id]
            db.insert_or_update(ActiveSkill.from_css(as_css))

    def _process_monsters(self, db):
        logger.warning('loading %s monsters', len(self.data.ownable_cards))
        for m in self.data.ownable_cards:
            item = Monster.from_csm(m)
            db.insert_or_update(item)

    def _process_awakenings(self, db):
        print('loading awakenings')
        for m in self.data.ownable_cards:
            items = Awakenings.from_csm(m)
            for item in items:
                db.insert_or_update(item)

    def _process_evolutions(self, db):
        print('loading evolutions')
        for m in self.data.ownable_cards:
            item = Evolution.from_csm(m)
            if item:
                db.insert_or_update(item)
