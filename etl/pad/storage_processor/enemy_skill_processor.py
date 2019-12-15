import json
import logging
import os

from dadguide_proto import enemy_skills_pb2
from dadguide_proto.enemy_skills_pb2 import MonsterBehavior
from pad.db.db_util import DbWrapper
from pad.raw.enemy_skills import enemy_skill_proto
from pad.raw.enemy_skills.enemy_skill_info import ESLogic
from pad.raw_processor import crossed_data
from pad.storage.enemy_skill import EnemySkill, EnemyData

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

logger = logging.getLogger('processor')


class EnemySkillProcessor(object):
    def __init__(self, db: DbWrapper, data: crossed_data.CrossServerDatabase):
        self.db = db
        self.data = data

        with open(os.path.join(__location__, 'enemy_skill.json')) as f:
            self.static_enemy_skills = json.load(f)

    def load_static(self):
        logger.warning('loading %d static skills', len(self.static_enemy_skills))
        for raw in self.static_enemy_skills:
            item = EnemySkill.from_json(raw)
            self.db.insert_or_update(item)

    def load_enemy_skills(self):
        used_skills = {}
        for csc in self.data.all_cards:
            for cseb in csc.enemy_behavior:
                # Skip fake skills (loaded via the static import) and logic
                if cseb.enemy_skill_id <= 0 or issubclass(cseb.jp_skill.btype, ESLogic):
                    continue

                used_skills[cseb.enemy_skill_id] = cseb

        logger.warning('loading %d enemy skills', len(used_skills))
        for cseb in used_skills.values():
            item = EnemySkill.from_cseb(cseb)
            self.db.insert_or_update(item)

    def load_enemy_data(self, base_dir: str):
        card_files = []
        logger.warning('scanning enemy data for %d cards', len(self.data.all_cards))
        for csc in self.data.all_cards:
            card_file = os.path.join(base_dir, '{}.textproto'.format(csc.monster_id))
            if not os.path.exists(card_file):
                continue
            card_files.append(card_file)

        logger.warning('loading enemy data for %d cards', len(card_files))
        count_not_approved = 0
        count_approved = 0
        for card_file in card_files:
            mbwo = enemy_skill_proto.load_from_file(card_file)
            mb = MonsterBehavior()
            mb.monster_id = mbwo.monster_id
            if mbwo.status == enemy_skills_pb2.MonsterBehaviorWithOverrides.NOT_APPROVED:
                mb.levels.extend(mbwo.levels)
                mb.approved = False
                count_not_approved += 1
            else:
                mb.levels.extend(mbwo.level_overrides)
                mb.approved = True
                count_approved += 1

            item = EnemyData.from_mb(mb, mbwo.status)
            self.db.insert_or_update(item)

        logger.warning('done, %d approved %d not approved', count_approved, count_not_approved)
