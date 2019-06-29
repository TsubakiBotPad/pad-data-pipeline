"""
Data from across multiple servers merged together.
"""
import json
import logging
from datetime import datetime
from typing import List, Any, Optional

import pytz

from pad.common.shared_types import MonsterId, MonsterNo
from pad.common import pad_util, monster_id_mapping, dungeon_types
from pad.raw import Bonus, Card, MonsterSkill, Dungeon, ESRef
from pad.raw.dungeon import SubDungeon
from pad.raw_processor.merged_data import MergedCard, MergedBonus, MergedEnemy
from pad.raw_processor.merged_database import Database

fail_logger = logging.getLogger('processor_failures')


class CrossServerCard(object):
    def __init__(self,
                 monster_id: MonsterId,
                 jp_card: MergedCard,
                 na_card: MergedCard,
                 kr_card: MergedCard):
        self.monster_id = monster_id
        self.jp_card = jp_card
        self.na_card = na_card
        self.kr_card = kr_card


def build_cross_server_cards(jp_database, na_database, kr_database) -> List[CrossServerCard]:
    all_monster_ids = set(jp_database.monster_id_to_card.keys())
    all_monster_ids.update(na_database.monster_id_to_card.keys())
    all_monster_ids.update(kr_database.monster_id_to_card.keys())
    all_monster_ids = list(sorted(all_monster_ids))

    # This is the list of cards we could potentially update
    combined_cards = []  # type: List[CrossServerCard]
    for monster_id in all_monster_ids:
        jp_card = jp_database.card_by_monster_id(monster_id)
        na_card = na_database.card_by_monster_id(monster_id)
        kr_card = kr_database.card_by_monster_id(monster_id)

        csc, err_msg = make_cross_server_card(jp_card, na_card, kr_card)
        if csc:
            combined_cards.append(csc)
        elif err_msg:
            fail_logger.debug('Skipping card, %s', err_msg)

    return combined_cards


def is_bad_name(name):
    """Finds names that are currently placeholder data."""
    return any(x in name for x in ['***', '???']) or name == '無し'


# Creates a CrossServerCard if appropriate.
# If the card cannot be created, provides an error message.
def make_cross_server_card(jp_card: MergedCard,
                           na_card: MergedCard,
                           kr_card: MergedCard) -> (CrossServerCard, str):
    if jp_card is None:
        # Basically only handles Voltron.
        jp_card = na_card

    if is_bad_name(jp_card.card.name):
        return None, 'Skipping debug card: {}'.format(repr(jp_card))

    if na_card is None or is_bad_name(na_card.card.name):
        # Card probably exists in JP but not in NA
        na_card = jp_card

    if kr_card is None or is_bad_name(kr_card.card.name):
        # Card probably exists in JP/NA but not in KR
        kr_card = na_card

    # Apparently some monsters can be ported to NA before their skills are
    def override_if_necessary(source_card: MergedCard, dest_card: MergedCard):
        if source_card.leader_skill and not dest_card.leader_skill:
            dest_card.leader_skill = source_card.leader_skill

        if source_card.active_skill and not dest_card.active_skill:
            dest_card.active_skill = source_card.active_skill

        if len(source_card.enemy_behavior) != len(dest_card.enemy_behavior):
            dest_card.enemy_behavior = source_card.enemy_behavior

        for idx in range(len(source_card.enemy_behavior)):
            if type(source_card.enemy_behavior[idx]) != type(dest_card.enemy_behavior[idx]):
                dest_card.enemy_behavior[idx] = source_card.enemy_behavior[idx]
            else:
                # Fill the source name in as a hack.
                # TODO: rename jp_name to alt_name or something
                dest_card.enemy_behavior[idx].jp_name = (source_card.enemy_behavior[idx].name or
                                                         dest_card.enemy_behavior[idx].name)

    # NA takes overrides from JP, and KR from NA
    override_if_necessary(jp_card, na_card)
    override_if_necessary(na_card, kr_card)

    return CrossServerCard(jp_card.monster_id, jp_card, na_card, kr_card), None


class CrossServerDungeon(object):
    def __init__(self, jp_dungeon: Dungeon, na_dungeon: Dungeon, kr_dungeon):
        self.dungeon_id = jp_dungeon.dungeon_id
        self.jp_dungeon = jp_dungeon
        self.na_dungeon = na_dungeon
        self.kr_dungeon = kr_dungeon

        self.sub_dungeons = make_cross_server_sub_dungeons(jp_dungeon, na_dungeon, kr_dungeon)


class CrossServerSubDungeon(object):
    def __init__(self, jp_sub_dungeon: SubDungeon, na_sub_dungeon: SubDungeon, kr_sub_dungeon: SubDungeon):
        self.sub_dungeon_id = jp_sub_dungeon.sub_dungeon_id
        self.jp_sub_dungeon = jp_sub_dungeon
        self.na_sub_dungeon = na_sub_dungeon
        self.kr_sub_dungeon = kr_sub_dungeon


def build_cross_server_dungeons(jp_database: Database,
                                na_database: Database,
                                kr_database: Database) -> List[CrossServerDungeon]:
    dungeon_ids = set([dungeon.dungeon_id for dungeon in jp_database.dungeons])
    dungeon_ids.update([dungeon.dungeon_id for dungeon in na_database.dungeons])
    dungeon_ids = list(sorted(dungeon_ids))

    combined_dungeons = []  # type: List[CrossServerDungeon]
    for dungeon_id in dungeon_ids:
        jp_dungeon = jp_database.dungeon_by_id(dungeon_id)
        na_dungeon = na_database.dungeon_by_id(dungeon_id)
        kr_dungeon = kr_database.dungeon_by_id(dungeon_id)

        csc, err_msg = make_cross_server_dungeon(jp_dungeon, na_dungeon, kr_dungeon)
        if csc:
            combined_dungeons.append(csc)
        elif err_msg:
            fail_logger.debug('Skipping dungeon, %s', err_msg)

    return combined_dungeons


def make_cross_server_dungeon(jp_dungeon: Dungeon,
                              na_dungeon: Dungeon,
                              kr_dungeon: Dungeon) -> (CrossServerDungeon, str):
    jp_dungeon = jp_dungeon or na_dungeon
    na_dungeon = na_dungeon or jp_dungeon
    kr_dungeon = kr_dungeon or na_dungeon

    if is_bad_name(jp_dungeon.clean_name):
        return None, 'Skipping debug dungeon: {}'.format(repr(jp_dungeon))

    if is_bad_name(na_dungeon.clean_name):
        # dungeon probably exists in JP but not in NA
        na_dungeon = jp_dungeon

    if is_bad_name(kr_dungeon.clean_name):
        # dungeon probably exists in JP but not in KR
        kr_dungeon = na_dungeon

    if jp_dungeon.full_dungeon_type == dungeon_types.RawDungeonType.DEPRECATED:
        return None, 'Skipping deprecated dungeon'

    return CrossServerDungeon(jp_dungeon, na_dungeon, kr_dungeon), None


def make_cross_server_sub_dungeons(jp_dungeon: Dungeon,
                                   na_dungeon: Dungeon,
                                   kr_dungeon: Dungeon) -> List[CrossServerSubDungeon]:
    jp_sd_map = {sd.sub_dungeon_id: sd for sd in jp_dungeon.sub_dungeons}
    na_sd_map = {sd.sub_dungeon_id: sd for sd in na_dungeon.sub_dungeons}
    kr_sd_map = {sd.sub_dungeon_id: sd for sd in kr_dungeon.sub_dungeons}

    # Ensure we know every possible sub_dungeon across all servers
    sd_keys = set(jp_sd_map.keys())
    sd_keys.update(na_sd_map.keys())
    sd_keys.update(kr_sd_map.keys())

    # Convert to a sorted list of ids
    sd_keys = list(sorted(sd_keys))

    results = []
    for key in sd_keys:
        jp_sd = jp_sd_map.get(key)
        na_sd = na_sd_map.get(key)
        kr_sd = kr_sd_map.get(key)

        if jp_sd is None or is_bad_name(jp_sd.clean_name):
            jp_sd = na_sd
        if na_sd is None or is_bad_name(na_sd.clean_name):
            na_sd = jp_sd
        if kr_sd is None or is_bad_name(kr_sd.clean_name):
            kr_sd = na_sd

        results.append(CrossServerSubDungeon(jp_sd, na_sd, kr_sd))

    return results


class CrossServerSkill(object):
    def __init__(self, jp_skill: MonsterSkill, na_skill: MonsterSkill, kr_skill: MonsterSkill):
        self.skill_id = jp_skill.skill_id
        self.jp_skill = jp_skill
        self.na_skill = na_skill
        self.kr_skill = kr_skill


def build_cross_server_skills(jp_database: Database,
                              na_database: Database,
                              kr_database: Database) -> List[CrossServerSkill]:
    results = []  # type: List[CrossServerSkill]
    jp_ids = [skill.skill_id for skill in jp_database.skills]

    for skill_id in jp_ids:
        jp_skill = jp_database.skill_by_id(skill_id)
        na_skill = na_database.skill_by_id(skill_id)
        kr_skill = kr_database.skill_by_id(skill_id)

        combined_skill = make_cross_server_skill(jp_skill, na_skill, kr_skill)
        if combined_skill:
            results.append(combined_skill)

    return results


def make_cross_server_skill(jp_skill: MonsterSkill,
                            na_skill: MonsterSkill,
                            kr_skill: MonsterSkill) -> Optional[CrossServerSkill]:
    jp_skill = jp_skill
    na_skill = na_skill or jp_skill
    kr_skill = kr_skill or na_skill

    if is_bad_name(jp_skill.name) and is_bad_name(na_skill.name):
        # Probably a debug skill
        return None

    if is_bad_name(jp_skill.name):
        jp_skill = na_skill

    if is_bad_name(na_skill.name):
        # skill probably exists in JP but not in NA
        na_skill = jp_skill

    if is_bad_name(kr_skill.name):
        # skill probably exists in JP but not in KR
        kr_skill = na_skill

    return CrossServerSkill(jp_skill, na_skill, kr_skill)


class CrossServerDatabase(object):
    def __init__(self, jp_database: Database, na_database: Database, kr_database: Database):
        self.all_cards = build_cross_server_cards(jp_database,
                                                  na_database,
                                                  kr_database)  # type: List[CrossServerCard]
        self.ownable_cards = list(
            filter(lambda c: 0 < c.monster_id < 19999, self.all_cards))  # type: List[CrossServerCard]

        self.dungeons = build_cross_server_dungeons(jp_database,
                                                    na_database,
                                                    kr_database)  # type: List[CrossServerDungeon]
        self.skills = build_cross_server_skills(jp_database,
                                                na_database,
                                                kr_database)  # type: List[CrossServerSkill]

        # Hack to inject calculated skills from old padguide system
        self.calculated_skills = {}

        self.jp_bonuses = jp_database.bonuses
        self.na_bonuses = na_database.bonuses
        # self.kr_bonuses = kr_database.bonuses

    def load_skill_text(self, skills_file_path: str):
        # This is a hack until we have skill parsing working properly.
        with open(skills_file_path) as f:
            skills_json = json.load(f)
        self.calculated_skills = {int(k): v for k, v in skills_json.items()}

    def card_diagnostics(self):
        print('checking', len(self.all_cards), 'cards')
        for c in self.all_cards:
            jpc = c.jp_card
            nac = c.na_card

            if jpc.card.type_1_id != nac.card.type_1_id:
                print('type1 failure: {} - {} {}'.format(nac.card.name, jpc.card.type_1_id, nac.card.type_1_id))

            if jpc.card.type_2_id != nac.card.type_2_id:
                print('type2 failure: {} - {} {}'.format(nac.card.name, jpc.card.type_2_id, nac.card.type_2_id))

            if jpc.card.type_3_id != nac.card.type_3_id:
                print('type3 failure: {} - {} {}'.format(nac.card.name, jpc.card.type_3_id, nac.card.type_3_id))

            jpcas = jpc.active_skill
            nacas = nac.active_skill
            if jpcas and nacas and jpcas.skill_id != nacas.skill_id:
                print('active skill failure: {} - {} / {}'.format(nac.card.name, jpcas.skill_id, nacas.skill_id))

            jpcls = jpc.leader_skill
            nacls = nac.leader_skill
            if jpcls and nacls and jpcls.skill_id != nacls.skill_id:
                print('leader skill failure: {} - {} / {}'.format(nac.card.name, jpcls.skill_id, nacls.skill_id))

            if len(jpc.card.awakenings) != len(nac.card.awakenings):
                print('awakening : {} - {} / {}'.format(nac.card.name,
                                                        len(jpc.card.awakenings),
                                                        len(nac.card.awakenings)))

            if len(jpc.card.super_awakenings) != len(nac.card.super_awakenings):
                print('super awakening : {} - {} / {}'.format(nac.card.name,
                                                              len(jpc.card.super_awakenings),
                                                              len(nac.card.super_awakenings)))

    def dungeon_diagnostics(self):
        print('checking', len(self.dungeons), 'dungeons')
        for d in self.dungeons:
            jpd = d.jp_dungeon
            nad = d.na_dungeon

            if len(jpd.sub_dungeons) != len(nad.sub_dungeons):
                print('Floor count failure: {} / {} - {} / {}'.format(jpd.clean_name, nad.clean_name,
                                                                      len(jpd.sub_dungeons),
                                                                      len(nad.sub_dungeons)))

            if jpd.full_dungeon_type != nad.full_dungeon_type:
                print('Dungeon type failure: {} / {} - {} / {}'.format(jpd.clean_name, nad.clean_name,
                                                                       jpd.full_dungeon_type, nad.full_dungeon_type))
