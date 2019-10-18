from typing import List, Dict

from pad.raw.skill import MonsterSkill
from pad.raw.skills import active_skill_info, leader_skill_info
from pad.raw.skills.active_skill_info import ActiveSkill
from pad.raw.skills.leader_skill_info import LeaderSkill


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

        for skill in skill_list:
            skill_id = skill.skill_id
            if self.active(skill_id) is None and self.leader(skill_id):
                print('Skill not parsed into active/leader:', skill.skill_id, skill.skill_type, skill.data)
