import logging
from typing import List, Dict, Optional

from pad.raw import EnemySkill
from pad.raw.enemy_skills.enemy_skill_info import ESBehavior, BEHAVIOR_MAP, EnemySkillUnknown

human_fix_logger = logging.getLogger('human_fix')


class BehaviorParser(object):
    def __init__(self):
        self.enemy_behaviors = []  # type: List[ESBehavior]
        self.behaviors_by_id = {}  # type: Dict[int, ESBehavior]

    def behavior(self, es_id: int) -> Optional[ESBehavior]:
        return self.behaviors_by_id.get(es_id, None)

    def parse(self, enemy_skill_list: List[EnemySkill]):
        for es in enemy_skill_list:
            es_id = es.enemy_skill_id
            es_type = es.type
            if es_type in BEHAVIOR_MAP:
                new_es = BEHAVIOR_MAP[es_type](es)
            else:
                human_fix_logger.error('Failed to parse enemy skill: %d/%d: %s', es_id, es_type, es.name)
                new_es = EnemySkillUnknown(es)

            # TODO: This got left out in port, what do?
            # inject_implicit_onetime(card, behavior)

            self.enemy_behaviors.append(new_es)
            self.behaviors_by_id[es_id] = new_es

        if len(self.enemy_behaviors) != len(self.behaviors_by_id):
            human_fix_logger.error('Error, enemy behavior size does not match: %d - %d',
                                   len(self.enemy_behaviors), len(self.behaviors_by_id))
