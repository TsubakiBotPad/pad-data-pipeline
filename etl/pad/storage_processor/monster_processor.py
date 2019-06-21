from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.storage.monster import MonsterLS, MonsterAS, Monster


class MonsterProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.data = data

    def process(self, db: DbWrapper):
        self._process_skills(db)
        self._process_monsters(db)
        self._process_awakenings(db)

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

        print('loading', len(ls_in_use), 'ls in use')
        for ls_skill_id in ls_in_use:
            ls_css = skill_id_to_crossed_skills[ls_skill_id]
            ls_item = MonsterLS.from_css(ls_css)
            db.insert_or_update(ls_item)

        print('loading', len(as_in_use), 'as in use')
        for as_skill_id in as_in_use:
            as_css = skill_id_to_crossed_skills[as_skill_id]
            as_item = MonsterAS.from_css(as_css)
            db.insert_or_update(as_item)

    def _process_monsters(self, db):
        print('loading', len(self.data.ownable_cards), 'cards')
        for m in self.data.ownable_cards:
            item = Monster.from_csm(m)
            db.insert_or_update(item)

    def _process_awakenings(self, db):
        pass
