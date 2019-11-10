"""
Data from across multiple servers merged together.
"""
import logging
import os
from typing import List, Optional, Union

from pad.common import dungeon_types, pad_util
from pad.common.shared_types import MonsterId, DungeonId
from pad.raw import Dungeon, EnemySkill, ESRef
from pad.raw.dungeon import SubDungeon
from pad.raw.skills import skill_text_typing
from pad.raw.skills.active_skill_info import ActiveSkill
from pad.raw.skills.en_active_skill_text import EnAsTextConverter
from pad.raw.skills.en_leader_skill_text import EnLsTextConverter
from pad.raw.skills.leader_skill_info import LeaderSkill
from pad.raw.skills.skill_text_typing import AsCondition, LsCondition
from pad.raw_processor.merged_data import MergedCard, MergedEnemySkill
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

        # These are optional loaded separately later
        self.has_hqimage = False
        self.has_animation = False

        # This is an initial pass; the more 'correct' versions override later
        self.leader_skill = make_cross_server_skill(jp_card.leader_skill, na_card.leader_skill, kr_card.leader_skill)
        self.active_skill = make_cross_server_skill(jp_card.active_skill, na_card.active_skill, kr_card.active_skill)

        self.enemy_behavior = make_cross_server_enemy_behavior(jp_card.enemy_skills, na_card.enemy_skills)

        # This is mostly just for integration test purposes. Should really be fixed a different way.
        self.en_ls_text = None
        self.en_as_text = None

    def load_text(self):
        self.en_ls_text = self.leader_skill.jp_skill.full_text(EnLsTextConverter()) if self.leader_skill else None
        self.en_as_text = self.active_skill.jp_skill.full_text(EnAsTextConverter()) if self.active_skill else None


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
    return any([x in name for x in ['***', '???']]) or any([x == name for x in ['None', '無し', '없음', 'なし']])


def _compare_named(override, dest):
    """Tries to determine if we should replace dest with override.

    First compares the null-ness of each, and then compares the quality of the 'name' property.
    """
    if override and not dest:
        return override
    if override and dest and is_bad_name(dest.name) and not is_bad_name(override.name):
        return override
    return dest


# Creates a CrossServerCard if appropriate.
# If the card cannot be created, provides an error message.
def make_cross_server_card(jp_card: MergedCard,
                           na_card: MergedCard,
                           kr_card: MergedCard) -> (CrossServerCard, str):
    def override_if_necessary(source_card: MergedCard, dest_card: MergedCard):
        if dest_card is None:
            return source_card
        if source_card is None:
            return dest_card

        # Check if the card isn't available based on the name.
        new_data_card = _compare_named(source_card.card, dest_card.card)
        if new_data_card != dest_card.card:
            dest_card.card = new_data_card
            # This is kind of gross and makes me think it might be wrong. We're checking the MergedCard.server
            # when creating the monster to determine where the data was sourced from, so we have to also
            # overwrite it here.
            dest_card.server = source_card.server

        # Apparently some monsters can be ported to servers before their skills are
        dest_card.leader_skill = _compare_named(source_card.leader_skill, dest_card.leader_skill)
        dest_card.active_skill = _compare_named(source_card.active_skill, dest_card.active_skill)

        return dest_card

    # Override priority: JP > NA, NA -> JP, NA -> KR.
    na_card = override_if_necessary(jp_card, na_card)
    jp_card = override_if_necessary(na_card, jp_card)
    kr_card = override_if_necessary(na_card, kr_card)

    if is_bad_name(jp_card.card.name):
        # This is a debug monster, or not yet supported
        return None, 'Debug monster'

    return CrossServerCard(jp_card.monster_id, jp_card, na_card, kr_card), None


def make_cross_server_enemy_behavior(jp_skills: List[MergedEnemySkill],
                                     na_skills: List[MergedEnemySkill]) -> List[ESRef]:
    """Creates enemy data by combining the JP enemy info with the NA enemy info."""
    jp_skills = list(jp_skills) or []
    na_skills = list(na_skills) or []

    if len(jp_skills) > len(na_skills):
        return jp_skills
    elif len(na_skills) > len(jp_skills):
        return na_skills
    elif not na_skills and not jp_skills:
        return []

    def override_if_necessary(override_skills: List[MergedEnemySkill], dest_skills: List[MergedEnemySkill]):
        # Then check if we need to individually overwrite
        for idx in range(len(override_skills)):
            override_skill = override_skills[idx].enemy_skill
            dest_skill = dest_skills[idx].enemy_skill
            if override_skill == _compare_named(override_skill, dest_skill):
                dest_skills[idx] = override_skills[idx]

    # Override priority: JP > NA, NA -> JP
    override_if_necessary(jp_skills, na_skills)
    override_if_necessary(na_skills, jp_skills)

    return list(map(lambda s: s.enemy_skill_ref, jp_skills))


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


EitherSkillType = Union[ActiveSkill, LeaderSkill]


class CrossServerSkill(object):
    def __init__(self, jp_skill: EitherSkillType, na_skill: EitherSkillType, kr_skill: EitherSkillType):
        self.skill_id = (jp_skill or na_skill or kr_skill).skill_id
        self.jp_skill = jp_skill
        self.na_skill = na_skill
        self.kr_skill = kr_skill

        self.en_text = None
        self.skill_type_tags = []  # type: List[Union[LsCondition, AsCondition]]


def build_cross_server_skills(jp_skills: List[EitherSkillType],
                              na_skills: List[EitherSkillType],
                              kr_skills: List[EitherSkillType]) -> List[CrossServerSkill]:
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

        combined_skill = make_cross_server_skill(jp_skill, na_skill, kr_skill)
        if combined_skill:
            results.append(combined_skill)

    return results


def make_cross_server_skill(jp_skill: EitherSkillType,
                            na_skill: EitherSkillType,
                            kr_skill: EitherSkillType) -> Optional[CrossServerSkill]:
    # Override priority: JP > NA, NA -> JP, NA -> KR.
    na_skill = _compare_named(jp_skill, na_skill)
    jp_skill = _compare_named(na_skill, jp_skill)
    kr_skill = _compare_named(na_skill, kr_skill)

    if na_skill or jp_skill or kr_skill:
        return CrossServerSkill(jp_skill, na_skill, kr_skill)
    else:
        return None


class CrossServerEnemySkill(object):
    def __init__(self, jp_skill: EnemySkill, na_skill: EnemySkill, kr_skill: EnemySkill):
        self.enemy_skill_id = (jp_skill or na_skill or kr_skill).enemy_skill_id
        self.jp_skill = jp_skill
        self.na_skill = na_skill
        self.kr_skill = kr_skill


def build_cross_server_enemy_skills(jp_skills: List[EnemySkill],
                                    na_skills: List[EnemySkill],
                                    kr_skills: List[EnemySkill]) -> List[CrossServerEnemySkill]:
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

        # Override priority: JP > NA, NA -> JP, NA -> KR.
        na_skill = _compare_named(jp_skill, na_skill)
        jp_skill = _compare_named(na_skill, jp_skill)
        kr_skill = _compare_named(na_skill, kr_skill)

        if na_skill or jp_skill or kr_skill:
            results.append(CrossServerEnemySkill(jp_skill, na_skill, kr_skill))

    return results


class CrossServerDatabase(object):
    def __init__(self, jp_database: Database, na_database: Database, kr_database: Database):
        self.all_cards = build_cross_server_cards(jp_database,
                                                  na_database,
                                                  kr_database)  # type: List[CrossServerCard]
        self.ownable_cards = list(
            filter(lambda c: 0 < c.monster_id < 19999, self.all_cards))  # type: List[CrossServerCard]

        self.leader_skills = build_cross_server_skills(jp_database.leader_skills,
                                                       na_database.leader_skills,
                                                       kr_database.leader_skills)

        ls_converter = EnLsTextConverter()
        for ls in self.leader_skills:
            ls.en_text = ls.jp_skill.full_text(ls_converter)
            ls.skill_type_tags = list(skill_text_typing.parse_ls_conditions(ls.en_text))
            ls.skill_type_tags.sort(key=lambda x: x.value)

        self.active_skills = build_cross_server_skills(jp_database.active_skills,
                                                       na_database.active_skills,
                                                       kr_database.active_skills)

        as_converter = EnAsTextConverter()
        for ask in self.active_skills:
            ask.en_text = ask.jp_skill.full_text(as_converter)
            ask.skill_type_tags = list(skill_text_typing.parse_as_conditions(ask.en_text))
            ask.skill_type_tags.sort(key=lambda x: x.value)

        self.dungeons = build_cross_server_dungeons(jp_database,
                                                    na_database,
                                                    kr_database)  # type: List[CrossServerDungeon]

        self.enemy_skills = build_cross_server_enemy_skills(jp_database.enemy_skills,
                                                            na_database.enemy_skills,
                                                            kr_database.enemy_skills)

        self.jp_bonuses = jp_database.bonuses
        self.na_bonuses = na_database.bonuses
        self.kr_bonuses = kr_database.bonuses

        self.jp_exchange = jp_database.exchange
        self.na_exchange = na_database.exchange
        self.kr_exchange = kr_database.exchange

        self.jp_egg_machines = jp_database.egg_machines
        self.na_egg_machines = na_database.egg_machines
        self.kr_egg_machines = kr_database.egg_machines
        
        self.jp_exchange = jp_database.exchange
        self.na_exchange = na_database.exchange
        self.kr_exchange = kr_database.exchange

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
            csc.load_text()

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

    # TODO: move this to another file
    # TODO: check with KR data
    def card_diagnostics(self):
        print('checking', len(self.all_cards), 'cards')
        for c in self.all_cards:
            jpc = c.jp_card
            nac = c.na_card
            krc = c.kr_card

            if jpc.card.type_1_id != nac.card.type_1_id:
                print('type1 failure: {} - {} {}'.format(nac.card.name, jpc.card.type_1_id, nac.card.type_1_id))

            if jpc.card.type_2_id != nac.card.type_2_id:
                print('type2 failure: {} - {} {}'.format(nac.card.name, jpc.card.type_2_id, nac.card.type_2_id))

            if jpc.card.type_3_id != nac.card.type_3_id:
                print('type3 failure: {} - {} {}'.format(nac.card.name, jpc.card.type_3_id, nac.card.type_3_id))

            if krc.card.type_1_id != nac.card.type_1_id:
                print('kr type1 failure: {} - {} {}'.format(nac.card.name, krc.card.type_1_id, nac.card.type_1_id))

            if krc.card.type_2_id != nac.card.type_2_id:
                print('kr type2 failure: {} - {} {}'.format(nac.card.name, krc.card.type_2_id, nac.card.type_2_id))

            if krc.card.type_3_id != nac.card.type_3_id:
                print('kr type3 failure: {} - {} {}'.format(nac.card.name, krc.card.type_3_id, nac.card.type_3_id))

            jpcas = jpc.active_skill
            nacas = nac.active_skill
            krcas = krc.active_skill
            if jpcas and nacas and jpcas.skill_id != nacas.skill_id:
                print('active skill failure: {} - {} / {}'.format(nac.card.name, jpcas.skill_id, nacas.skill_id))
            if krcas and nacas and krcas.skill_id != nacas.skill_id:
                print('active skill failure: {} - {} / {}'.format(nac.card.name, krcas.skill_id, nacas.skill_id))

            jpcls = jpc.leader_skill
            nacls = nac.leader_skill
            krcls = krc.leader_skill
            if jpcls and nacls and jpcls.skill_id != nacls.skill_id:
                print('leader skill failure: {} - {} / {}'.format(nac.card.name, jpcls.skill_id, nacls.skill_id))
            if krcls and nacls and krcls.skill_id != nacls.skill_id:
                print('leader skill failure: {} - {} / {}'.format(nac.card.name, krcls.skill_id, nacls.skill_id))

            if len(jpc.card.awakenings) != len(nac.card.awakenings):
                print('awakening : {} - {} / {}'.format(nac.card.name,
                                                        len(jpc.card.awakenings),
                                                        len(nac.card.awakenings)))

            if len(krc.card.awakenings) != len(nac.card.awakenings):
                print('awakening : {} - {} / {}'.format(nac.card.name,
                                                        len(krc.card.awakenings),
                                                        len(nac.card.awakenings)))

            if len(jpc.card.super_awakenings) != len(nac.card.super_awakenings):
                print('super awakening : {} - {} / {}'.format(nac.card.name,
                                                              len(jpc.card.super_awakenings),
                                                              len(nac.card.super_awakenings)))

            if len(krc.card.super_awakenings) != len(nac.card.super_awakenings):
                print('super awakening : {} - {} / {}'.format(nac.card.name,
                                                              len(krc.card.super_awakenings),
                                                              len(nac.card.super_awakenings)))

    def dungeon_diagnostics(self):
        print('checking', len(self.dungeons), 'dungeons')
        for d in self.dungeons:
            jpd = d.jp_dungeon
            nad = d.na_dungeon
            krd = d.kr_dungeon

            if len(jpd.sub_dungeons) != len(nad.sub_dungeons):
                print('Floor count failure: {} / {} - {} / {}'.format(jpd.clean_name, nad.clean_name,
                                                                      len(jpd.sub_dungeons),
                                                                      len(nad.sub_dungeons)))

            if len(krd.sub_dungeons) != len(nad.sub_dungeons):
                print('Floor count failure: {} / {} - {} / {}'.format(krd.clean_name, nad.clean_name,
                                                                      len(krd.sub_dungeons),
                                                                      len(nad.sub_dungeons)))

            if jpd.full_dungeon_type != nad.full_dungeon_type:
                print('Dungeon type failure: {} / {} - {} / {}'.format(jpd.clean_name, nad.clean_name,
                                                                       jpd.full_dungeon_type, nad.full_dungeon_type))

            if krd.full_dungeon_type != nad.full_dungeon_type:
                print('Dungeon type failure: {} / {} - {} / {}'.format(krd.clean_name, nad.clean_name,
                                                                       krd.full_dungeon_type, nad.full_dungeon_type))
