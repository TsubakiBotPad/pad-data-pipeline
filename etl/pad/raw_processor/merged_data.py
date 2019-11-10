"""
Data from the different sources in the same server, merged together.
"""

from datetime import datetime
from typing import List

import pytz

from pad.common import pad_util
from pad.common.monster_id_mapping import nakr_no_to_monster_id, jp_no_to_monster_id
from pad.common.shared_types import Server, StarterGroup, MonsterNo, MonsterId
from pad.raw import Bonus, Card, Dungeon, ESRef, EnemySkill, Enemy
from pad.raw.skills.active_skill_info import ActiveSkill
from pad.raw.skills.leader_skill_info import LeaderSkill


class MergedBonus(pad_util.Printable):
    def __init__(self, server: Server, bonus: Bonus, dungeon: Dungeon, group: StarterGroup):
        self.server = server
        self.bonus = bonus
        self.dungeon = dungeon
        self.group = group
        self.start_timestamp = pad_util.gh_to_timestamp_2(bonus.start_time_str, server)
        self.end_timestamp = pad_util.gh_to_timestamp_2(bonus.end_time_str, server)

        self.critical_failures = []

    def __str__(self):
        return 'MergedBonus({} {} - {} - {})'.format(
            self.server, self.group, self.dungeon, self.bonus)

    def open_duration(self):
        open_datetime_utc = datetime.fromtimestamp(self.start_timestamp, pytz.UTC)
        close_datetime_utc = datetime.fromtimestamp(self.end_timestamp, pytz.UTC)
        return close_datetime_utc - open_datetime_utc


class MergedEnemySkill(pad_util.Printable):
    def __init__(self, enemy_skill_ref: ESRef, enemy_skill: EnemySkill):
        self.enemy_skill_ref = enemy_skill_ref
        self.enemy_skill = enemy_skill


class MergedEnemy(pad_util.Printable):
    def __init__(self, enemy_id: int, enemy: Enemy, enemy_skills: List[MergedEnemySkill]):
        self.enemy_id = enemy_id
        self.enemy = enemy
        self.enemy_skills = enemy_skills


class MergedCard(pad_util.Printable):
    def __init__(self,
                 server: Server,
                 card: Card,
                 active_skill: ActiveSkill,
                 leader_skill: LeaderSkill,
                 enemy_skills: List[MergedEnemySkill]):
        self.server = server
        self.monster_no = card.monster_no
        self.monster_id = self.no_to_id(card.monster_no)
        self.card = card

        self.active_skill_id = active_skill.skill_id if active_skill else None
        self.active_skill = active_skill

        self.leader_skill_id = leader_skill.skill_id if leader_skill else None
        self.leader_skill = leader_skill

        self.enemy_skills = enemy_skills

        self.critical_failures = []

    def no_to_id(self, monster_no: MonsterNo) -> MonsterId:
        if self.server == Server.jp:
            return jp_no_to_monster_id(monster_no)
        else:
            return nakr_no_to_monster_id(monster_no)

    def __str__(self):
        return 'MergedCard({} - {} - {} [es:{}])'.format(
            repr(self.card), repr(self.active_skill), repr(self.leader_skill), len(self.enemy_skills))
