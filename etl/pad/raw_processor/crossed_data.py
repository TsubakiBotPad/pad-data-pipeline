"""
Data from across multiple servers merged together.
"""
import logging
import os
from copy import copy
from typing import List, Optional, Union, TypeVar, Callable, Tuple

from pad.common import dungeon_types, pad_util
from pad.common.shared_types import MonsterId, DungeonId, Server
from pad.raw import Dungeon, EnemySkill
from pad.raw.dungeon import SubDungeon
from pad.raw.skills import skill_text_typing
from pad.raw.skills.active_skill_info import ActiveSkill
from pad.raw.skills.en.active_skill_text import EnASTextConverter
from pad.raw.skills.enemy_skill_info import ESInstance, ESUnknown, ESNone
from pad.raw.skills.leader_skill_info import LeaderSkill
from pad.raw_processor.jp_replacements import jp_en_replacements
from pad.raw_processor.merged_data import MergedCard
from pad.raw_processor.merged_database import Database

fail_logger = logging.getLogger('processor_failures')
human_fix_logger = logging.getLogger('human_fix')


class CrossServerCard(object):
    def __init__(self,
                 jp_card: MergedCard,
                 na_card: MergedCard,
                 kr_card: MergedCard,
                 server: Server):
        self.monster_id = jp_card.monster_id
        self.jp_card = jp_card
        self.na_card = na_card
        self.kr_card = kr_card

        self.cur_card = (jp_card, na_card, kr_card)[server.value]

        # These are optional loaded separately later
        self.has_hqimage = False
        self.has_animation = False

        # This is an initial pass; the more 'correct' versions override later
        self.leader_skill = make_cross_server_skill(jp_card.leader_skill,
                                                    na_card.leader_skill,
                                                    kr_card.leader_skill,
                                                    server)
        self.active_skill = make_cross_server_skill(jp_card.active_skill,
                                                    na_card.active_skill,
                                                    kr_card.active_skill,
                                                    server)

        self.enemy_behavior = make_cross_server_enemy_behavior(jp_card.enemy_skills,
                                                               na_card.enemy_skills,
                                                               kr_card.enemy_skills,
                                                               server)
        self.gem = None


def build_cross_server_cards(jp_database, na_database, kr_database, server) -> List[CrossServerCard]:
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

        csc, err_msg = make_cross_server_card(jp_card, na_card, kr_card, server)
        if csc:
            combined_cards.append(csc)
        elif err_msg:
            fail_logger.debug('Skipping card, %s', err_msg)

    # Post-Processing
    jp_gems = {}
    na_gems = {}
    for card in combined_cards[4468:]:
        if not card.cur_card.card.ownable:
            continue
        if card.jp_card.card.name.endswith('の希石') or \
                card.na_card.card.name.endswith("'s Gem"):
            jp_gems[card.jp_card.card.name[:-3]] = card
            na_gems[card.na_card.card.name[:-6]] = card

    for card in combined_cards:
        card.gem = jp_gems.get(card.jp_card.card.name) or \
                   na_gems.get(card.na_card.card.name)
        if card.gem:
            for jc in jp_gems:
                if jp_gems[jc] == card.gem:
                    jp_gems.pop(jc)
                    break
            for nc in na_gems:
                if na_gems[nc] == card.gem:
                    na_gems.pop(nc)
                    break

    jp_gems.update(na_gems)
    aggreg = jp_gems.keys()
    if aggreg:
        human_fix_logger.warning("Unassigned Gem(s): " + ', '.join(aggreg))

    return combined_cards


def is_bad_name(name):
    """Finds names that are currently placeholder data."""
    return any([x in name for x in ['***', '???']]) or any([x == name for x in ['None', '無し', '없음', 'なし']])


def _compare_named(override, dest):
    """Tries to determine if we should replace dest with override.

    First compares the null-ness of each, and then compares the quality of the 'name' property.
    """
    if override and not dest:
        return override
    if override \
            and dest and is_bad_name(pad_util.strip_colors(dest.name)) \
            and not is_bad_name(pad_util.strip_colors(override.name)):
        return override
    return dest


T = TypeVar("T")


def _coalesce_named(named1: T, named2: T, named3: T) -> Tuple[T, T, T]:
    named2 = _compare_named(_compare_named(named3, named1), named2)
    named1 = _compare_named(named2, named1)
    named3 = _compare_named(named1, named3)

    return named1, named2, named3


def _coalesce_by_server(jp: T, na: T, kr: T, server: Server,
                        coalescer: Callable[[T, T, T], Tuple[T, T, T]] = _coalesce_named) -> Tuple[T, T, T]:
    if server == Server.jp:
        jp, na, kr = coalescer(jp, na, kr)
    elif server == Server.na:
        na, jp, kr = coalescer(na, jp, kr)
    elif server == Server.kr:
        kr, jp, na = coalescer(kr, jp, na)
    return jp, na, kr


# Creates a CrossServerCard if appropriate.
# If the card cannot be created, provides an error message.
def make_cross_server_card(jp_card: MergedCard,
                           na_card: MergedCard,
                           kr_card: MergedCard,
                           server: Server) -> (CrossServerCard, str):
    def override_if_necessary(source_card: MergedCard, dest_card: MergedCard):
        """Return source_card if dest_card is invalid, otherwise return dest_card"""
        if dest_card is None:
            return source_card
        if source_card is None:
            return dest_card

        # Check if the card isn't available based on the name.
        new_data_card = _compare_named(source_card.card, dest_card.card)
        if new_data_card != dest_card.card:
            dest_card = copy(dest_card)
            dest_card.card = new_data_card
            # This is kind of gross and makes me think it might be wrong. We're checking the MergedCard.server
            # when creating the monster to determine where the data was sourced from, so we have to also
            # overwrite it here.
            dest_card.server = source_card.server

        # Apparently some monsters can be ported to servers before their skills are
        dest_card.leader_skill = _compare_named(source_card.leader_skill, dest_card.leader_skill)
        dest_card.active_skill = _compare_named(source_card.active_skill, dest_card.active_skill)

        return dest_card

    def override_in_order(card1: MergedCard, card2: MergedCard, card3: MergedCard):
        card2 = override_if_necessary(override_if_necessary(card3, card1), card2)
        card1 = override_if_necessary(card2, card1)
        card3 = override_if_necessary(card1, card3)
        return card1, card2, card3

    # Override priority: JP > NA, NA -> JP, NA -> KR.
    jp_card, na_card, kr_card = _coalesce_by_server(jp_card, na_card, kr_card, server, override_in_order)

    if is_bad_name(jp_card.card.name):
        # This is a debug monster, or not yet supported
        # TODO: Make sure this is safe for NA DB generation
        return None, 'Debug monster'

    return CrossServerCard(jp_card, na_card, kr_card, server), None


class CrossServerESInstance(object):
    """A per-monster skill info across servers.

    Not sure why we need both of these.
    """

    def __init__(self, jp_skill: ESInstance, na_skill: ESInstance, kr_skill: ESInstance, server: Server):
        self.enemy_skill_id = (jp_skill or na_skill or kr_skill).enemy_skill_id
        self.jp_skill = jp_skill
        self.na_skill = na_skill
        self.kr_skill = kr_skill
        self.cur_skill = (jp_skill, na_skill, kr_skill)[server.value]

    def unique_count(self):
        return len({map(id, [self.jp_skill, self.na_skill, self.kr_skill])})


def make_cross_server_enemy_behavior(jp_skills: List[ESInstance],
                                     na_skills: List[ESInstance],
                                     kr_skills: List[ESInstance],
                                     server: Server) -> List[CrossServerESInstance]:
    """Creates enemy data by combining the JP/NA/KR enemy info."""
    jp_skills = list(jp_skills) or []
    na_skills = list(na_skills) or []
    kr_skills = list(kr_skills) or []

    def override_all_if_necessary(left, right):
        # Typically if a monster isn't in a server yet, the ES is empty or limited.
        if len(left) > len(right):
            return left

        # Occasionally the monster has the same ES count but some of them are ESNone.
        def count_useful_skills(ess: List[ESInstance]) -> int:
            return sum(map(lambda y: 0 if isinstance(y.behavior, ESNone) else 1, ess))

        return left if count_useful_skills(left) > count_useful_skills(right) else right

    def coalesce_all(skills1, skills2, skills3):
        skills2 = override_all_if_necessary(override_all_if_necessary(skills3, skills1), skills2)
        skills1 = override_all_if_necessary(skills2, skills1)
        skills3 = override_all_if_necessary(skills1, skills3)
        return skills1, skills2, skills3

    jp_skills, na_skills, kr_skills = _coalesce_by_server(jp_skills, na_skills, kr_skills, server, coalesce_all)

    def override_if_necessary(override_skills: List[ESInstance], dest_skills: List[ESInstance]):
        # Then check if we need to individually overwrite
        for idx in range(len(override_skills)):
            override_skill = override_skills[idx].behavior

            dest_skill = dest_skills[idx].behavior
            if override_skill is _compare_named(override_skill, dest_skill):
                dest_skills[idx] = override_skills[idx]

    def coalesce_any(skills1, skills2, skills3):  # Assuming JP, NA, KR
        skill_temp = skills1[:]  #
        override_if_necessary(skills3, skill_temp)  #
        override_if_necessary(skill_temp, skills2)  # (KR -> JP) -> NA
        override_if_necessary(skills2, skills1)  # NA -> JP
        override_if_necessary(skills1, skills3)  # JP -> KR

    # Override priority: JP > NA, NA -> JP
    if server == Server.jp:
        coalesce_any(jp_skills, na_skills, kr_skills)
    elif server == Server.na:
        coalesce_any(na_skills, jp_skills, kr_skills)
    elif server == Server.kr:
        coalesce_any(kr_skills, jp_skills, na_skills)

    return _combine_es(jp_skills, na_skills, kr_skills, server)


def _combine_es(jp_skills: List[ESInstance],
                na_skills: List[ESInstance],
                kr_skills: List[ESInstance],
                server: Server) -> List[CrossServerESInstance]:
    if not len(jp_skills) == len(na_skills) and len(na_skills) == len(kr_skills):
        raise ValueError('unexpected skill lengths')
    results = []

    cur_skills = (jp_skills, na_skills, kr_skills)[server.value]

    for idx, cur_skill in enumerate(cur_skills):
        if isinstance(cur_skill.behavior, ESUnknown):
            human_fix_logger.error('Detected an in-use unknown enemy skill: %d/%d: %s - %s',
                                   cur_skill.enemy_skill_id,
                                   cur_skill.behavior.type,
                                   cur_skill.behavior.name,
                                   cur_skill.behavior.params)
        results.append(CrossServerESInstance(jp_skills[idx], na_skills[idx], kr_skills[idx], server))
    return results


class CrossServerDungeon(object):
    def __init__(self, jp_dungeon: Dungeon, na_dungeon: Dungeon, kr_dungeon: Dungeon, server: Server):
        self.dungeon_id = jp_dungeon.dungeon_id
        self.jp_dungeon = jp_dungeon
        self.na_dungeon = na_dungeon
        self.kr_dungeon = kr_dungeon
        self.cur_dungeon = (jp_dungeon, na_dungeon, kr_dungeon)[server.value]

        # Replacements for JP dungeon attributes to English
        self.na_dungeon.clean_name = jp_en_replacements(self.na_dungeon.clean_name)

        self.sub_dungeons = make_cross_server_sub_dungeons(jp_dungeon, na_dungeon, kr_dungeon, server)

        # Replacements for JP subdungeon attributes to English
        for csd in self.sub_dungeons:
            csd.na_sub_dungeon.clean_name = jp_en_replacements(csd.na_sub_dungeon.clean_name)


class CrossServerSubDungeon(object):
    def __init__(self,
                 jp_sub_dungeon: SubDungeon,
                 na_sub_dungeon: SubDungeon,
                 kr_sub_dungeon: SubDungeon,
                 server: Server):
        self.sub_dungeon_id = jp_sub_dungeon.sub_dungeon_id
        self.jp_sub_dungeon = jp_sub_dungeon
        self.na_sub_dungeon = na_sub_dungeon
        self.kr_sub_dungeon = kr_sub_dungeon
        self.cur_sub_dungeon = (jp_sub_dungeon, na_sub_dungeon, kr_sub_dungeon)[server.value]


def build_cross_server_dungeons(jp_database: Database,
                                na_database: Database,
                                kr_database: Database,
                                server: Server) -> List[CrossServerDungeon]:
    dungeon_ids = set([dungeon.dungeon_id for dungeon in jp_database.dungeons])
    dungeon_ids.update([dungeon.dungeon_id for dungeon in na_database.dungeons])
    dungeon_ids.update([dungeon.dungeon_id for dungeon in kr_database.dungeons])
    dungeon_ids = list(sorted(dungeon_ids))

    combined_dungeons = []  # type: List[CrossServerDungeon]
    for dungeon_id in dungeon_ids:
        jp_dungeon = jp_database.dungeon_by_id(dungeon_id)
        na_dungeon = na_database.dungeon_by_id(dungeon_id)
        kr_dungeon = kr_database.dungeon_by_id(dungeon_id)

        csc, err_msg = make_cross_server_dungeon(jp_dungeon, na_dungeon, kr_dungeon, server)
        if csc:
            combined_dungeons.append(csc)
        elif err_msg:
            fail_logger.debug('Skipping dungeon, %s', err_msg)

    return combined_dungeons


def make_cross_server_dungeon(jp_dungeon: Dungeon,
                              na_dungeon: Dungeon,
                              kr_dungeon: Dungeon,
                              server: Server) -> (CrossServerDungeon, str):
    jp_dungeon, na_dungeon, kr_dungeon = _coalesce_by_server(jp_dungeon, na_dungeon, kr_dungeon, server)

    if is_bad_name(jp_dungeon.clean_name):
        return None, 'Skipping debug dungeon: {}'.format(repr(jp_dungeon))

    if jp_dungeon.full_dungeon_type == dungeon_types.RawDungeonType.DEPRECATED:
        return None, 'Skipping deprecated dungeon'

    return CrossServerDungeon(jp_dungeon, na_dungeon, kr_dungeon, server), None


def make_cross_server_sub_dungeons(jp_dungeon: Dungeon,
                                   na_dungeon: Dungeon,
                                   kr_dungeon: Dungeon,
                                   server: Server) -> List[CrossServerSubDungeon]:
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

        jp_sd, na_sd, kr_sd = _coalesce_by_server(jp_sd, na_sd, kr_sd, server)

        results.append(CrossServerSubDungeon(jp_sd, na_sd, kr_sd, server))

    return results


EitherSkillType = Union[ActiveSkill, LeaderSkill]


class CrossServerSkill(object):
    def __init__(self, jp_skill: EitherSkillType, na_skill: EitherSkillType, kr_skill: EitherSkillType, server: Server):
        self.skill_id = (jp_skill or na_skill or kr_skill).skill_id
        self.jp_skill = jp_skill
        self.na_skill = na_skill
        self.kr_skill = kr_skill
        self.cur_skill = (jp_skill, na_skill, kr_skill)[server.value]


def build_cross_server_skills(jp_skills: List[EitherSkillType],
                              na_skills: List[EitherSkillType],
                              kr_skills: List[EitherSkillType],
                              server: Server) -> List[CrossServerSkill]:
    jp_map = {skill.skill_id: skill for skill in jp_skills}
    na_map = {skill.skill_id: skill for skill in na_skills}
    kr_map = {skill.skill_id: skill for skill in kr_skills}

    all_ids = set()
    all_ids.update(jp_map.keys())
    all_ids.update(na_map.keys())
    all_ids.update(kr_map.keys())

    results = []  # type: List[CrossServerSkill]
    for skill_id in all_ids:
        jp_skill = jp_map.get(skill_id, None)
        na_skill = na_map.get(skill_id, None)
        kr_skill = kr_map.get(skill_id, None)

        combined_skill = make_cross_server_skill(jp_skill, na_skill, kr_skill, server)
        if combined_skill:
            results.append(combined_skill)

    return results


def make_cross_server_skill(jp_skill: EitherSkillType,
                            na_skill: EitherSkillType,
                            kr_skill: EitherSkillType,
                            server: Server) -> Optional[CrossServerSkill]:
    # Override priority: JP > NA, NA -> JP, NA -> KR.
    jp_skill, na_skill, kr_skill = _coalesce_by_server(jp_skill, na_skill, kr_skill, server)

    if jp_skill:
        return CrossServerSkill(jp_skill, na_skill, kr_skill, server)
    else:
        return None


class CrossServerEnemySkill(object):
    def __init__(self, jp_skill: EnemySkill, na_skill: EnemySkill, kr_skill: EnemySkill, server: Server):
        self.enemy_skill_id = (jp_skill or na_skill or kr_skill).enemy_skill_id
        self.jp_skill = jp_skill
        self.na_skill = na_skill
        self.kr_skill = kr_skill
        self.cur_skill = (jp_skill, na_skill, kr_skill)[server.value]


def build_cross_server_enemy_skills(jp_skills: List[EnemySkill],
                                    na_skills: List[EnemySkill],
                                    kr_skills: List[EnemySkill],
                                    server: Server) -> List[CrossServerEnemySkill]:
    jp_map = {skill.enemy_skill_id: skill for skill in jp_skills}
    na_map = {skill.enemy_skill_id: skill for skill in na_skills}
    kr_map = {skill.enemy_skill_id: skill for skill in kr_skills}

    all_ids = set()
    all_ids.update(jp_map.keys())
    all_ids.update(na_map.keys())
    all_ids.update(kr_map.keys())

    results = []  # type: List[CrossServerEnemySkill]
    for skill_id in all_ids:
        jp_skill = jp_map.get(skill_id, None)
        na_skill = na_map.get(skill_id, None)
        kr_skill = kr_map.get(skill_id, None)

        jp_skill, na_skill, kr_skill = _coalesce_by_server(jp_skill, na_skill, kr_skill, server)

        if na_skill or jp_skill or kr_skill:
            results.append(CrossServerEnemySkill(jp_skill, na_skill, kr_skill, server))

    return results


class CrossServerDatabase(object):
    def __init__(self, jp_database: Database, na_database: Database, kr_database: Database, server=Server.jp):
        self.all_cards = build_cross_server_cards(jp_database,
                                                  na_database,
                                                  kr_database,
                                                  server)  # type: List[CrossServerCard]
        self.ownable_cards = [c for c in self.all_cards if 0 < c.monster_id < 19999]  # type: List[CrossServerCard]

        self.leader_skills = build_cross_server_skills(jp_database.leader_skills,
                                                       na_database.leader_skills,
                                                       kr_database.leader_skills,
                                                       server)

        self.active_skills = build_cross_server_skills(jp_database.active_skills,
                                                       na_database.active_skills,
                                                       kr_database.active_skills,
                                                       server)

        en_as_converter = EnASTextConverter()
        for ask in self.active_skills:
            ask.skill_type_tags = list(skill_text_typing.parse_as_conditions(ask))
            ask.skill_type_tags.sort(key=lambda x: x.value)

        self.dungeons = build_cross_server_dungeons(jp_database,
                                                    na_database,
                                                    kr_database,
                                                    server)  # type: List[CrossServerDungeon]

        self.enemy_skills = build_cross_server_enemy_skills(jp_database.raw_enemy_skills,
                                                            na_database.raw_enemy_skills,
                                                            kr_database.raw_enemy_skills,
                                                            server)

        self.jp_bonuses = jp_database.bonuses
        self.na_bonuses = na_database.bonuses
        self.kr_bonuses = kr_database.bonuses

        self.jp_exchange = jp_database.exchange
        self.na_exchange = na_database.exchange
        self.kr_exchange = kr_database.exchange

        self.jp_egg_machines = jp_database.egg_machines
        self.na_egg_machines = na_database.egg_machines
        self.kr_egg_machines = kr_database.egg_machines

        self.jp_purchase = jp_database.purchase
        self.na_purchase = na_database.purchase
        self.kr_purchase = kr_database.purchase

        self.monster_id_to_card = {c.monster_id: c for c in self.all_cards}
        self.leader_id_to_leader = {s.skill_id: s for s in self.leader_skills}
        self.active_id_to_active = {s.skill_id: s for s in self.active_skills}
        self.dungeon_id_to_dungeon = {d.dungeon_id: d for d in self.dungeons}

        self.hq_image_monster_ids = []  # type: List[MonsterId]
        self.animated_monster_ids = []  # type: List[MonsterId]

        for csc in self.ownable_cards:
            if csc.leader_skill:
                csc.leader_skill = self.leader_id_to_leader[csc.leader_skill.skill_id]
            if csc.active_skill:
                csc.active_skill = self.active_id_to_active[csc.active_skill.skill_id]

        self.server = server

    def card_by_monster_id(self, monster_id: MonsterId) -> CrossServerCard:
        return self.monster_id_to_card.get(monster_id, None)

    def dungeon_by_id(self, dungeon_id: DungeonId) -> CrossServerDungeon:
        return self.dungeon_id_to_dungeon.get(dungeon_id, None)

    def load_extra_image_info(self, media_dir: str):
        for f in os.listdir(os.path.join(media_dir, 'hq_portraits')):
            if len(f) == 9 and f[-4:].lower() == '.png':
                self.hq_image_monster_ids.append(MonsterId(int(f[0:5])))

        for f in os.listdir(os.path.join(media_dir, 'animated_portraits')):
            if len(f) == 9 and f[-4:].lower() == '.mp4':
                self.animated_monster_ids.append(MonsterId(int(f[0:5])))

        for csc in self.ownable_cards:
            if csc.monster_id in self.hq_image_monster_ids:
                csc.has_hqimage = True
            if csc.monster_id in self.animated_monster_ids:
                csc.has_animation = True

    def save(self, output_dir: str, file_name: str, obj: object, pretty: bool):
        output_file = os.path.join(output_dir, '{}.json'.format(file_name))
        with open(output_file, 'w', encoding='utf-8') as f:
            pad_util.json_file_dump(obj, f, pretty)

    def save_all(self, output_dir: str, pretty: bool):
        self.save(output_dir, 'all_cards', self.all_cards, pretty)
        self.save(output_dir, 'dungeons', self.dungeons, pretty)
        self.save(output_dir, 'active_skills', self.active_skills, pretty)
        self.save(output_dir, 'leader_skills', self.leader_skills, pretty)
        self.save(output_dir, 'enemy_skills', self.enemy_skills, pretty)
        self.save(output_dir, 'jp_bonuses', self.jp_bonuses, pretty)
        self.save(output_dir, 'na_bonuses', self.na_bonuses, pretty)
        self.save(output_dir, 'kr_bonuses', self.kr_bonuses, pretty)
