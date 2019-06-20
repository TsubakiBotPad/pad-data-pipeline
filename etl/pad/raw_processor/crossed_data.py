"""
Data from across multiple servers merged together.
"""

import logging
from datetime import datetime
from typing import List, Any

import pytz

from pad.common.shared_types import MonsterNo, CardId
from pad.common import pad_util, monster_id_mapping
from pad.raw import Bonus, Card, MonsterSkill, Dungeon, ESRef
from pad.raw_processor.merged_data import MergedCard, MergedBonus, MergedEnemy
from pad.raw_processor.merged_database import Database

fail_logger = logging.getLogger('processor_failures')


class CrossServerCard(object):
    def __init__(self,
                 monster_no: MonsterNo,
                 jp_card: MergedCard,
                 na_card: MergedCard,
                 kr_card: MergedCard):
        self.monster_no = monster_no
        self.jp_card = jp_card
        self.na_card = na_card
        self.kr_card = kr_card


def nakr_id_to_jp_id(monster_id: CardId) -> CardId:
    # The monster_no is equivalent to the JP id
    return CardId(monster_id_mapping.nakr_id_to_monster_no(monster_id))


def build_ownable_cross_server_cards(jp_database, na_database) -> List[CrossServerCard]:
    all_cards = build_cross_server_cards(jp_database, na_database)
    # 10K-20K could contain NA-only monsters (Voltron).
    return list(filter(lambda c: 0 < c.monster_no < 19_999, all_cards))


def build_cross_server_cards(jp_database, na_database, kr_database) -> List[CrossServerCard]:
    all_monster_nos = set(jp_database.monster_no_to_card.keys())
    all_monster_nos.update(na_database.monster_no_to_card.keys())
    all_monster_nos.update(kr_database.monster_no_to_card.keys())
    all_monster_nos = list(sorted(all_monster_nos))

    # This is the list of cards we could potentially update
    combined_cards = []  # type: List[CrossServerCard]
    for monster_no in all_monster_nos:
        jp_card = jp_database.card_by_monster_no(monster_no)
        na_card = na_database.card_by_monster_no(monster_no)
        kr_card = kr_database.card_by_monster_no(monster_no)

        csc, err_msg = make_cross_server_card(jp_card, na_card, kr_card)
        if csc:
            combined_cards.append(csc)
        elif err_msg:
            fail_logger.debug('Skipping card, %s', err_msg)

    return combined_cards


def is_bad_name(name):
    """Finds names that are currently placeholder data."""
    return any(x in name for x in ['***', '???'])


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

    return CrossServerCard(MonsterNo(jp_card.card.card_id), jp_card, na_card, kr_card), None


class CrossServerDungeon(object):
    def __init__(self, jp_dungeon: Dungeon, na_dungeon: Dungeon, kr_dungeon):
        self.dungeon_id = jp_dungeon.dungeon_id
        self.jp_dungeon = jp_dungeon
        self.na_dungeon = na_dungeon
        self.kr_dungeon = kr_dungeon


def build_cross_server_dungeons(jp_database: Database,
                                na_database: Database,
                                kr_database: Database) -> List[CrossServerDungeon]:
    jp_dungeon_ids = [dungeon.dungeon_id for dungeon in jp_database.dungeons]

    # This is the list of dungeons we could potentially update
    combined_dungeons = []  # type: List[CrossServerDungeon]
    for dungeon_id in jp_dungeon_ids:
        jp_dungeon = jp_database.dungeon_by_id(dungeon_id)

        # Might need a mapping like cards
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

    return CrossServerDungeon(jp_dungeon, na_dungeon, kr_dungeon), None


class CrossServerDatabase(object):
    def __init__(self, jp_database: Database, na_database: Database, kr_database: Database):
        self.all_cards = build_cross_server_cards(jp_database, na_database, kr_database)
        self.ownable_cards = list(filter(lambda c: 0 < c.monster_no < 19_999, self.all_cards))
        self.dungeons = build_cross_server_dungeons(jp_database, na_database, kr_database)

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
                print('awakening : {} - {} / {}'.format(nac.card.name, len(jpc.card.awakenings), len(nac.card.awakenings)))

            if len(jpc.card.super_awakenings) != len(nac.card.super_awakenings):
                print('super awakening : {} - {} / {}'.format(nac.card.name, len(jpc.card.super_awakenings), len(nac.card.super_awakenings)))


    def dungeon_diagnostics(self):
        print('checking', len(self.dungeons), 'dungeons')
        for d in self.dungeons:
            jpd = d.jp_dungeon
            nad = d.na_dungeon

            if len(jpd.floors) != len(nad.floors):
                print('Floor count failure: {} / {} - {} / {}'.format(jpd.clean_name, nad.clean_name, len(jpd.floors),
                                                                      len(nad.floors)))

            if jpd.full_dungeon_type != nad.full_dungeon_type:
                print('Dungeon type failure: {} / {} - {} / {}'.format(jpd.clean_name, nad.clean_name,
                                                                       jpd.full_dungeon_type, nad.full_dungeon_type))
