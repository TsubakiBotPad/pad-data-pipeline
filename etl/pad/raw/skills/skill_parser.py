import logging
from typing import List, Dict

from pad.raw.skill import MonsterSkill
from pad.raw.skills import active_skill_info, leader_skill_info
from pad.raw.skills.active_skill_info import ActiveSkill
from pad.raw.skills.leader_skill_info import LeaderSkill

human_fix_logger = logging.getLogger('human_fix')


class SkillParser(object):
    def __init__(self):
        self.active_skills = []  # type: List[ActiveSkill]
        self.leader_skills = []  # type: List[LeaderSkill]
        self.as_by_id = {}  # type: Dict[int, ActiveSkill]
        self.ls_by_id = {}  # type: Dict[int, LeaderSkill]

    def active(self, as_id: int) -> ActiveSkill:
        return self.as_by_id.get(as_id, None)

    def leader(self, ls_id: int) -> LeaderSkill:
        return self.ls_by_id.get(ls_id, None)

    def parse(self, skill_list: List[MonsterSkill]):
        self.active_skills = active_skill_info.convert(skill_list)
        self.leader_skills = leader_skill_info.convert(skill_list)
        self.as_by_id = {x.skill_id: x for x in self.active_skills}
        self.ls_by_id = {x.skill_id: x for x in self.leader_skills}

        for skill in skill_list:
            skill_id = skill.skill_id
            if skill.skill_type in [0, 89]:  # 0 is None, 89 is placeholder
                continue
            if self.active(skill_id) is None and self.leader(skill_id) is None:
                human_fix_logger.error('Skill not parsed into active/leader: %d %d %s',
                                       skill.skill_id, skill.skill_type, skill.data)

                skill.skill_type = -1
                active = ActiveSkill(skill)
                self.active_skills.append(active)
                self.as_by_id[skill_id] = active

                leader = LeaderSkill(-1, skill)
                self.leader_skills.append(leader)
                self.ls_by_id[skill_id] = leader
