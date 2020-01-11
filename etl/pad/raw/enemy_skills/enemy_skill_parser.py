import logging
from typing import List, Dict, Optional

from pad.raw import EnemySkill
from pad.raw.skills.enemy_skill_info import ESBehavior, BEHAVIOR_MAP, ESUnknown, ESSkillSet

logger = logging.getLogger('processor')
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
                new_es = ESUnknown(es)

            self.enemy_behaviors.append(new_es)

        self.behaviors_by_id = {es.enemy_skill_id: es for es in self.enemy_behaviors}

        for es in self.enemy_behaviors:
            if isinstance(es, ESSkillSet):
                for sub_es_id in es.skill_ids:
                    if sub_es_id in self.behaviors_by_id:
                        es.skills.append(self.behaviors_by_id[sub_es_id])
                    else:
                        print('failed to look up enemy skill:', sub_es_id)

        if len(self.enemy_behaviors) != len(self.behaviors_by_id):
            human_fix_logger.error('Error, enemy behavior size does not match: %d - %d',
                                   len(self.enemy_behaviors), len(self.behaviors_by_id))
