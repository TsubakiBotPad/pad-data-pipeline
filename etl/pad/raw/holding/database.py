import json
import logging
import os
from typing import List

from pad.raw import Card, Dungeon, MonsterSkill, EnemySkill, Exchange
from pad.raw import bonus, card, dungeon, skill, exchange, enemy_skill
from ..processor import enemy_skillset as ess
from ..processor.merged_data import MergedBonus, MergedCard, MergedEnemy

fail_logger = logging.getLogger('processor_failures')


def _clean_bonuses(pg_server, bonus_sets, dungeons) -> List[MergedBonus]:
    dungeons_by_id = {d.dungeon_id: d for d in dungeons}

    merged_bonuses = []
    for data_group, bonus_set in bonus_sets.items():
        for bonus in bonus_set:
            dungeon = None
            guerrilla_group = None
            if bonus.dungeon_id:
                dungeon = dungeons_by_id.get(bonus.dungeon_id, None)
                if dungeon is None:
                    fail_logger.critical('Dungeon lookup failed for bonus: %s', repr(bonus))
                else:
                    guerrilla_group = data_group if dungeon.dungeon_type == 'guerrilla' else None

            if guerrilla_group or data_group == 'red':
                merged_bonuses.append(MergedBonus(pg_server, bonus, dungeon, guerrilla_group))

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

        if card.active_skill_id:
            active_skill = skills_by_id.get(card.active_skill_id, None)
            if active_skill is None:
                fail_logger.critical('Active skill lookup failed: %s - %s',
                                     repr(card), card.active_skill_id)

        if card.leader_skill_id:
            leader_skill = skills_by_id.get(card.leader_skill_id, None)
            if leader_skill is None:
                fail_logger.critical('Leader skill lookup failed: %s - %s',
                                     repr(card), card.leader_skill_id)

        enemy_behavior = enemy_behavior_by_card_id.get(int(card.card_id), [])

        merged_cards.append(MergedCard(card, active_skill, leader_skill, enemy_behavior))
    return merged_cards


def _clean_enemy(cards, enemy_skills) -> List[MergedEnemy]:
    ess.enemy_skill_map = {s.enemy_skill_id: s for s in enemy_skills}
    merged_enemies = []
    for card in cards:
        if len(card.enemy_skill_refs) == 0:
            continue
        enemy_skillset = [x for x in card.enemy_skill_refs]
        behavior = ess.extract_behavior(card, enemy_skillset)
        merged_enemies.append(MergedEnemy(card.card_id, behavior))
    return merged_enemies


class Database(object):
    def __init__(self, pg_server, raw_dir):
        self.pg_server = pg_server
        self.base_dir = os.path.join(raw_dir, pg_server)

        # Loaded from disk
        self.raw_cards = []  # type: List[Card]
        self.dungeons = []  # type: List[Dungeon]
        self.bonus_sets = {}
        self.skills = []  # type: List[MonsterSkill]
        self.enemy_skills = []  # type: List[EnemySkill]
        self.exchange = []  # type: List[Exchange]
        self.egg_machines = []

        # This is temporary for the integration of calculated skills
        self.raw_skills = []

        # Computed from other entries
        self.bonuses = []  # type: List[MergedBonus]
        self.cards = []  # type: List[MergedCard]
        self.enemies = []  # type: List[MergedEnemy]

        # Faster lookups
        self.dungeon_id_to_dungeon = {}
        self.card_id_to_raw_card = {}
        self.enemy_id_to_enemy = {}

    def load_database(self, skip_skills=False, skip_bonus=False, skip_extra=False):
        base_dir = self.base_dir
        self.raw_cards = card.load_card_data(data_dir=base_dir)
        self.dungeons = dungeon.load_dungeon_data(data_dir=base_dir)

        if not skip_bonus:
            self.bonus_sets = {
                'red': bonus.load_bonus_data(data_dir=base_dir, data_group='red'),
                'blue': bonus.load_bonus_data(data_dir=base_dir, data_group='blue'),
                'green': bonus.load_bonus_data(data_dir=base_dir, data_group='green'),
            }

        if not skip_skills:
            self.skills = skill.load_skill_data(data_dir=base_dir)
            self.raw_skills = skill.load_raw_skill_data(data_dir=base_dir)
        self.enemy_skills = enemy_skill.load_enemy_skill_data(data_dir=base_dir)

        if not skip_extra:
            self.exchange = exchange.load_data(data_dir=base_dir)
            # TODO move this to egg machines parser same as others
            with open(os.path.join(base_dir, 'egg_machines.json')) as f:
                self.egg_machines = json.load(f)

        self.bonuses = _clean_bonuses(self.pg_server, self.bonus_sets, self.dungeons)
        self.enemies = _clean_enemy(self.raw_cards, self.enemy_skills)
        self.cards = _clean_cards(self.raw_cards, self.skills, self.enemies)

        self.dungeon_id_to_dungeon = {d.dungeon_id: d for d in self.dungeons}
        self.card_id_to_raw_card = {c.card_id: c for c in self.raw_cards}
        self.enemy_id_to_enemy = {e.enemy_id: e for e in self.enemies}

    def save(self, output_dir: str, file_name: str, obj: object, pretty: bool):
        output_file = os.path.join(output_dir, '{}_{}.json'.format(self.pg_server, file_name))
        with open(output_file, 'w') as f:
            if pretty:
                json.dump(obj, f, indent=4, sort_keys=True, default=lambda x: x.__dict__)
            else:
                json.dump(obj, f, sort_keys=True, default=lambda x: x.__dict__)

    def save_all(self, output_dir: str, pretty: bool):
        self.save(output_dir, 'raw_cards', self.raw_cards, pretty)
        self.save(output_dir, 'dungeons', self.dungeons, pretty)
        self.save(output_dir, 'skills', self.skills, pretty)
        self.save(output_dir, 'enemy_skills', self.enemy_skills, pretty)
        self.save(output_dir, 'bonuses', self.bonuses, pretty)
        self.save(output_dir, 'cards', self.cards, pretty)
        self.save(output_dir, 'exchange', self.exchange, pretty)
        self.save(output_dir, 'enemies', self.enemies, pretty)

    def dungeon_by_id(self, dungeon_id):
        return self.dungeon_id_to_dungeon.get(dungeon_id, None)

    def raw_card_by_id(self, card_id):
        return self.card_id_to_raw_card.get(card_id, None)

    def enemy_by_id(self, enemy_id):
        return self.enemy_id_to_enemy.get(enemy_id, None)
