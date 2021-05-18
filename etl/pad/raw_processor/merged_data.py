"""
Data from the different sources in the same server, merged together.
"""
from datetime import datetime
from typing import List, Optional

import pytz

from pad.common import pad_util
from pad.common.monster_id_mapping import server_monster_id_fn
from pad.common.shared_types import Server, StarterGroup, MonsterNo, MonsterId
from pad.raw import Bonus, Card, Dungeon, Enemy
from pad.raw.skills.active_skill_info import ActiveSkill
from pad.raw.skills.enemy_skill_info import ESInstance
from pad.raw.skills.leader_skill_info import LeaderSkill


class MergedBonus(pad_util.Printable):
    def __init__(self, server: Server, bonus: Bonus, dungeon: Dungeon, group: StarterGroup):
        self.server = server
        self.bonus = bonus
        self.dungeon = dungeon
        self.group = group
        self.start_timestamp = pad_util.gh_to_timestamp_2(bonus.start_time_str, server)
        self.end_timestamp = pad_util.gh_to_timestamp_2(bonus.end_time_str, server)

    def __str__(self):
        return 'MergedBonus({} {} - {} - {})'.format(
            self.server, self.group, self.dungeon, self.bonus)

    def open_duration(self):
        open_datetime_utc = datetime.fromtimestamp(self.start_timestamp, pytz.UTC)
        close_datetime_utc = datetime.fromtimestamp(self.end_timestamp, pytz.UTC)
        return close_datetime_utc - open_datetime_utc


# class MergedEnemySkill(pad_util.Printable):
#     def __init__(self, enemy_skill_ref: ESRef, enemy_skill: EnemySkill):
#         self.enemy_skill_ref = enemy_skill_ref
#         self.enemy_skill = enemy_skill


class MergedEnemy(pad_util.Printable):
    def __init__(self, enemy_id: int, enemy: Enemy, enemy_skills: List[ESInstance]):
        self.enemy_id = enemy_id
        self.enemy = enemy
        self.enemy_skills = enemy_skills


class MergedCard(pad_util.Printable):
    def __init__(self,
                 server: Server,
                 card: Card,
                 active_skill: ActiveSkill,
                 leader_skill: LeaderSkill,
                 enemy_skills: List[ESInstance]):
        self.server = server
        self.id_mapper = server_monster_id_fn(self.server)
        self.monster_no = card.monster_no
        self.monster_id = self.no_to_id(card.monster_no)
        self.card = card

        self.linked_monster_id = None  # type: Optional[int]
        if self.card.linked_monster_no:
            self.linked_monster_id = self.no_to_id(card.linked_monster_no)

        self.active_skill_id = active_skill.skill_id if active_skill else None
        self.active_skill = active_skill

        self.leader_skill_id = leader_skill.skill_id if leader_skill else None
        self.leader_skill = leader_skill

        self.enemy_skills = enemy_skills

    def no_to_id(self, monster_no: MonsterNo) -> MonsterId:
        return server_monster_id_fn(self.server)(monster_no)

    def __str__(self):
        return 'MergedCard({} - {} - {} [es:{}])'.format(
            repr(self.card), repr(self.active_skill), repr(self.leader_skill), len(self.enemy_skills))

    def __copy__(self):
        return MergedCard(self.server, self.card, self.active_skill, self.leader_skill, self.enemy_skills[:])
