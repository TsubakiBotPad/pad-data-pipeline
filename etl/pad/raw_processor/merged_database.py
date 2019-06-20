import json
import logging
import os
from typing import List, Dict

from pad.common.monster_id_mapping import nakr_id_to_monster_no
from pad.common.shared_types import Server, StarterGroup, MonsterNo, CardId, DungeonId
from pad.raw import Bonus, Card, Dungeon, MonsterSkill, EnemySkill, Exchange, egg_machine
from pad.raw import bonus, card, dungeon, skill, exchange, enemy_skill
# from ..processor import enemy_skillset as ess
from .merged_data import MergedBonus, MergedCard, MergedEnemy

fail_logger = logging.getLogger('processor_failures')


def _clean_bonuses(server: Server, bonus_sets, dungeons) -> List[MergedBonus]:
    dungeons_by_id = {d.dungeon_id: d for d in dungeons}

    merged_bonuses = []
    for data_group, bonus_set in bonus_sets.items():
        for bonus in bonus_set:
            dungeon = None
            guerrilla_group = None
            critical_failures = []
            if bonus.dungeon_id:
                dungeon = dungeons_by_id.get(bonus.dungeon_id, None)
                if dungeon is None:
                    critical_failures.append('Dungeon lookup failed for bonus: %s'.format(repr(bonus)))
                else:
                    guerrilla_group = data_group if dungeon.dungeon_type == 'guerrilla' else None

            if guerrilla_group or data_group == StarterGroup.RED.name:
                result = MergedBonus(server, bonus, dungeon, guerrilla_group)
                result.critical_failures.extend(critical_failures)
                merged_bonuses.append(result)

    return merged_bonuses


def _clean_cards(cards: List[card.Card],
                 skills: List[skill.MonsterSkill],
                 enemy_skills: List[MergedEnemy]) -> List[MergedCard]:
    skills_by_id = {s.skill_id: s for s in skills}
    enemy_behavior_by_card_id = {int(s.enemy_id): s.behavior for s in enemy_skills}

    merged_cards = []
    for card in cards:
        active_skill = None
        leader_skill = None
        critical_failures = []

        if card.active_skill_id:
            active_skill = skills_by_id.get(card.active_skill_id, None)
            if active_skill is None:
                critical_failures.append('Active skill lookup failed: %s - %s'.format(
                                          repr(card), card.active_skill_id))

        if card.leader_skill_id:
            leader_skill = skills_by_id.get(card.leader_skill_id, None)
            if leader_skill is None:
                critical_failures.append('Leader skill lookup failed: %s - %s'.format(
                                         repr(card), card.leader_skill_id))

        enemy_behavior = enemy_behavior_by_card_id.get(card.card_id, [])

        result = MergedCard(card, active_skill, leader_skill, enemy_behavior)
        result.critical_failures.extend(critical_failures)
        merged_cards.append(result)

    return merged_cards


def _clean_enemy(cards, enemy_skills) -> List[MergedEnemy]:
    # TODO: enemy stuff
    # ess.enemy_skill_map = {s.enemy_skill_id: s for s in enemy_skills}
    merged_enemies = []
    # for card in cards:
    #     if len(card.enemy_skill_refs) == 0:
    #         continue
    #     enemy_skillset = [x for x in card.enemy_skill_refs]
    #     behavior = ess.extract_behavior(card, enemy_skillset)
    #     merged_enemies.append(MergedEnemy(card.card_id, behavior))
    return merged_enemies


class Database(object):
    def __init__(self, server: Server, raw_dir: str):
        self.server = server
        self.base_dir = os.path.join(raw_dir, server.value)

        # Loaded from disk
        self.raw_cards = []  # type: List[Card]
        self.dungeons = []  # type: List[Dungeon]
        self.bonus_sets = {} # type: Dict[str, List[Bonus]]
        self.skills = []  # type: List[MonsterSkill]
        self.enemy_skills = []  # type: List[EnemySkill]
        self.exchange = []  # type: List[Exchange]
        self.egg_machines = []

        # Computed from other entries
        self.bonuses = []  # type: List[MergedBonus]
        self.cards = []  # type: List[MergedCard]
        self.enemies = []  # type: List[MergedEnemy]

        # Faster lookups
        self.dungeon_id_to_dungeon = {} # type: Dict[DungeonId, Dungeon]
        self.card_id_to_card = {} # type: Dict[CardId, MergedCard]
        self.monster_no_to_card = {} # type: Dict[MonsterNo, MergedCard]
        self.enemy_id_to_enemy = {}

    def load_database(self, skip_skills=False, skip_bonus=False, skip_extra=False):
        base_dir = self.base_dir
        raw_cards = card.load_card_data(data_dir=base_dir)
        self.dungeons = dungeon.load_dungeon_data(data_dir=base_dir)

        if not skip_bonus:
            self.bonus_sets = {
                g.value: bonus.load_bonus_data(data_dir=base_dir, server=self.server, data_group=g.value) for g in StarterGroup
            }

        if not skip_skills:
            self.skills = skill.load_skill_data(data_dir=base_dir)
            # TODO: need to compute skill data here

        self.enemy_skills = enemy_skill.load_enemy_skill_data(data_dir=base_dir)

        if not skip_extra:
            self.exchange = exchange.load_data(data_dir=base_dir)
            self.egg_machines = egg_machine.load_data(data_dir=base_dir)

        self.bonuses = _clean_bonuses(self.server, self.bonus_sets, self.dungeons)
        self.enemies = _clean_enemy(raw_cards, self.enemy_skills)
        self.cards = _clean_cards(raw_cards, self.skills, self.enemies)

        self.dungeon_id_to_dungeon = {d.dungeon_id: d for d in self.dungeons}
        self.card_id_to_card = {c.card_id: c for c in self.cards}
        if self.server == Server.JP:
            self.monster_no_to_card = self.card_id_to_card
        else:
            self.monster_no_to_card = {nakr_id_to_monster_no(c.card_id): c for c in self.cards}

        self.enemy_id_to_enemy = {e.enemy_id: e for e in self.enemies}

    def save(self, output_dir: str, file_name: str, obj: object, pretty: bool):
        output_file = os.path.join(output_dir, '{}_{}.json'.format(self.server.name, file_name))
        with open(output_file, 'w') as f:
            indent = 4 if pretty else None
            json.dump(obj, f, indent=indent, sort_keys=True, default=lambda x: x.__dict__)

    def save_all(self, output_dir: str, pretty: bool):
        self.save(output_dir, 'dungeons', self.dungeons, pretty)
        self.save(output_dir, 'skills', self.skills, pretty)
        self.save(output_dir, 'enemy_skills', self.enemy_skills, pretty)
        self.save(output_dir, 'bonuses', self.bonuses, pretty)
        self.save(output_dir, 'cards', self.cards, pretty)
        self.save(output_dir, 'exchange', self.exchange, pretty)
        self.save(output_dir, 'enemies', self.enemies, pretty)

    def dungeon_by_id(self, dungeon_id: DungeonId):
        return self.dungeon_id_to_dungeon.get(dungeon_id, None)

    def card_by_id(self, card_id: CardId):
        return self.card_id_to_card.get(card_id, None)

    def card_by_monster_no(self, monster_no: MonsterNo):
        return self.monster_no_to_card.get(monster_no, None)

    def enemy_by_id(self, enemy_id):
        return self.enemy_id_to_enemy.get(enemy_id, None)
