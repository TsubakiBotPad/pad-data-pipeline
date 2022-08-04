import json
from typing import List

from pad.db.db_util import DbWrapper
from pad.db.sql_item import ExistsStrategy
from pad.raw.skills import skill_text_typing
from pad.raw.skills.active_behaviors import behavior_to_json
from pad.raw.skills.active_skill_info import ActiveSkill as ASSkill
from pad.raw.skills.en.active_skill_text import EnASTextConverter
from pad.raw.skills.en.leader_skill_text import EnLSTextConverter
from pad.raw.skills.ja.active_skill_text import JaASTextConverter
from pad.raw.skills.ja.leader_skill_text import JaLSTextConverter
from pad.raw.skills.ko.active_skill_text import KoASTextConverter
from pad.raw_processor.crossed_data import CrossServerSkill
from pad.storage_processor.shared_storage import ServerDependentSqlItem


class ActiveSkill(ServerDependentSqlItem):
    """Monster active skill."""
    KEY_COL = 'active_skill_id'
    BASE_TABLE = 'active_skills'

    @staticmethod
    def from_css(css: CrossServerSkill) -> 'ActiveSkill':
        jp_skill = css.jp_skill
        na_skill = css.na_skill
        kr_skill = css.kr_skill
        cur_skill = css.cur_skill

        desc_ja = cur_skill.full_text(JaASTextConverter())
        desc_en = cur_skill.full_text(EnASTextConverter())
        desc_ko = cur_skill.full_text(KoASTextConverter())
        desc_templated_ja = cur_skill.templated_text(JaASTextConverter())
        desc_templated_en = cur_skill.templated_text(EnASTextConverter())
        desc_templated_ko = cur_skill.templated_text(KoASTextConverter())

        skill_type_tags = skill_text_typing.parse_as_conditions(css)
        tags = skill_text_typing.format_conditions(skill_type_tags)

        return ActiveSkill(
            active_skill_id=jp_skill.skill_id,
            compound_skill_type_id=cur_skill.compound_skill_type,
            name_ja=jp_skill.name,
            name_en=na_skill.name,
            name_ko=kr_skill.name,
            desc_ja=desc_ja,
            desc_en=desc_en,
            desc_ko=desc_ko,
            desc_templated_ja=desc_templated_ja,
            desc_templated_en=desc_templated_en,
            desc_templated_ko=desc_templated_ko,
            desc_official_ja=jp_skill.raw_description,
            desc_official_en=na_skill.raw_description,
            desc_official_ko=kr_skill.raw_description,
            cooldown_turns_max=cur_skill.cooldown_turns_max,
            cooldown_turns_min=cur_skill.cooldown_turns_min,
            tags=tags)

    def __init__(self,
                 active_skill_id: int = None,
                 compound_skill_type_id: int = None,
                 name_ja: str = None,
                 name_en: str = None,
                 name_ko: str = None,
                 desc_ja: str = None,
                 desc_en: str = None,
                 desc_ko: str = None,
                 desc_templated_ja: str = None,
                 desc_templated_en: str = None,
                 desc_templated_ko: str = None,
                 desc_official_ja: str = None,
                 desc_official_en: str = None,
                 desc_official_ko: str = None,
                 cooldown_turns_max: int = None,
                 cooldown_turns_min: int = None,
                 tags: str = None,
                 tstamp: int = None):
        self.active_skill_id = active_skill_id
        self.compound_skill_type_id = compound_skill_type_id
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.desc_ja = desc_ja
        self.desc_en = desc_en
        self.desc_ko = desc_ko
        self.desc_templated_ja = desc_templated_ja
        self.desc_templated_en = desc_templated_en
        self.desc_templated_ko = desc_templated_ko
        self.desc_official_ja = desc_official_ja
        self.desc_official_en = desc_official_en
        self.desc_official_ko = desc_official_ko
        self.cooldown_turns_max = cooldown_turns_max
        self.cooldown_turns_min = cooldown_turns_min
        # TODO: Delete these in one week
        self.turn_max = cooldown_turns_max
        self.turn_min = cooldown_turns_min
        self.tags = tags
        self.tstamp = tstamp

    def __str__(self):
        return 'ActiveSkill({}): {} -> {}'.format(self.key_value(), self.name_en, self.desc_en)


class ActiveSubskill(ServerDependentSqlItem):
    """Monster active subskill."""
    KEY_COL = 'active_subskill_id'
    BASE_TABLE = 'active_subskills'

    @staticmethod
    def from_as(act: ASSkill) -> 'ActiveSubskill':
        desc_ja = act.full_text(JaASTextConverter())
        desc_en = act.full_text(EnASTextConverter())
        desc_ko = act.full_text(KoASTextConverter())
        desc_templated_ja = act.templated_text(JaASTextConverter())
        desc_templated_en = act.templated_text(EnASTextConverter())
        desc_templated_ko = act.templated_text(KoASTextConverter())

        skill_type_tags = skill_text_typing.parse_as_conditions(act, True)
        tags = skill_text_typing.format_conditions(skill_type_tags)

        return ActiveSubskill(
            active_subskill_id=act.skill_id,
            behavior=behavior_to_json(act.behavior),
            # TODO: Figure out how to do names
            name_ja="",
            name_en="",
            name_ko="",
            desc_ja=desc_ja,
            desc_en=desc_en,
            desc_ko=desc_ko,
            desc_templated_ja=desc_templated_ja,
            desc_templated_en=desc_templated_en,
            desc_templated_ko=desc_templated_ko,
            board_65=act.board.to_6x5(),
            board_76=act.board.to_7x6(),
            cooldown=act.cooldown_turns_max or -1,
            tags=tags)

    def __init__(self,
                 active_subskill_id: int = None,
                 behavior: List[dict] = None,
                 name_ja: str = None,
                 name_en: str = None,
                 name_ko: str = None,
                 desc_ja: str = None,
                 desc_en: str = None,
                 desc_ko: str = None,
                 desc_templated_ja: str = None,
                 desc_templated_en: str = None,
                 desc_templated_ko: str = None,
                 board_65: str = None,
                 board_76: str = None,
                 cooldown: int = None,
                 tags: str = None,
                 tstamp: int = None):
        self.active_subskill_id = active_subskill_id
        self.behavior = json.dumps(behavior)
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.desc_ja = desc_ja
        self.desc_en = desc_en
        self.desc_ko = desc_ko
        self.desc_templated_ja = desc_templated_ja
        self.desc_templated_en = desc_templated_en
        self.desc_templated_ko = desc_templated_ko
        self.board_65 = board_65
        self.board_76 = board_76
        self.cooldown = cooldown
        self.tags = tags
        self.tstamp = tstamp

    def _json_cols(self):
        return ['behavior']

    def __str__(self):
        return 'ActiveSubskill({}): {}'.format(self.key_value(), self.desc_en)


class ActivePart(ServerDependentSqlItem):
    """Monster active subskill part."""
    KEY_COL = 'active_part_id'
    BASE_TABLE = 'active_parts'

    @staticmethod
    def from_as(act: ASSkill) -> 'ActivePart':
        desc_ja = act.full_text(JaASTextConverter())
        desc_en = act.full_text(EnASTextConverter())
        desc_ko = act.full_text(KoASTextConverter())
        desc_templated_ja = act.templated_text(JaASTextConverter())
        desc_templated_en = act.templated_text(EnASTextConverter())
        desc_templated_ko = act.templated_text(KoASTextConverter())

        skill_type_tags = skill_text_typing.parse_as_conditions(act, True)
        tags = skill_text_typing.format_conditions(skill_type_tags)

        return ActivePart(
            active_part_id=act.skill_id,
            behavior=behavior_to_json(act.behavior),
            active_skill_type_id=act.skill_type,
            raw_behavior=act.raw_data,
            desc_ja=desc_ja,
            desc_en=desc_en,
            desc_ko=desc_ko,
            desc_templated_ja=desc_templated_ja,
            desc_templated_en=desc_templated_en,
            desc_templated_ko=desc_templated_ko,
            tags=tags)

    def __init__(self,
                 active_part_id: int = None,
                 behavior: List[dict] = None,
                 active_skill_type_id: int = None,
                 raw_behavior: List[int] = None,
                 desc_ja: str = None,
                 desc_en: str = None,
                 desc_ko: str = None,
                 desc_templated_ja: str = None,
                 desc_templated_en: str = None,
                 desc_templated_ko: str = None,
                 tags: str = None,
                 tstamp: int = None):
        self.active_part_id = active_part_id
        self.behavior = json.dumps(behavior)
        self.active_skill_type_id = active_skill_type_id
        self.raw_behavior = json.dumps(raw_behavior)
        self.desc_ja = desc_ja
        self.desc_en = desc_en
        self.desc_ko = desc_ko
        self.desc_templated_ja = desc_templated_ja
        self.desc_templated_en = desc_templated_en
        self.desc_templated_ko = desc_templated_ko
        self.tags = tags
        self.tstamp = tstamp

    def _json_cols(self):
        return ['behavior', 'raw_behavior']

    def __str__(self):
        return 'ActivePart({}): {}'.format(self.key_value(), self.desc_en)


class ActiveSkillsSubskills(ServerDependentSqlItem):
    """Active skills to their subskills."""
    KEY_COL = 'active_skills_subskills_id'
    BASE_TABLE = 'active_skills_subskills'

    @staticmethod
    def from_css(skill: CrossServerSkill, subskill: ASSkill, order_idx: int = 0) \
            -> 'ActiveSkillsSubskills':
        return ActiveSkillsSubskills(
            active_skills_subskills_id=None,  # Key that is looked up or inserted
            active_skill_id=skill.cur_skill.skill_id,
            active_subskill_id=subskill.skill_id,
            order_idx=order_idx)

    def __init__(self,
                 active_skills_subskills_id: int = None,
                 active_skill_id: int = None,
                 active_subskill_id: int = None,
                 order_idx: int = None,
                 tstamp: int = None):
        self.active_skills_subskills_id = active_skills_subskills_id
        self.active_skill_id = active_skill_id
        self.active_subskill_id = active_subskill_id
        self.order_idx = order_idx
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]

    def _lookup_columns(self):
        return ['active_skill_id', 'active_subskill_id', 'order_idx']

    def __str__(self):
        return 'ActiveSkillsSubskills({}): {} -> {} (#{})'.format(self.key_value(), self.active_skill_id,
                                                                 self.active_subskill_id, self.order_idx)


class ActiveSubskillsParts(ServerDependentSqlItem):
    """Active subskills to their parts."""
    KEY_COL = 'active_subskills_parts_id'
    BASE_TABLE = 'active_subskills_parts'

    @staticmethod
    def from_css(skill: ASSkill, part: ASSkill, order_idx: int = 0) \
            -> 'ActiveSubskillsParts':
        return ActiveSubskillsParts(
            active_subskills_parts_id=None,  # Key that is looked up or inserted
            active_subskill_id=skill.skill_id,
            active_part_id=part.skill_id,
            order_idx=order_idx)

    def __init__(self,
                 active_subskills_parts_id: int = None,
                 active_subskill_id: int = None,
                 active_part_id: int = None,
                 order_idx: int = None,
                 tstamp: int = None):
        self.active_subskills_parts_id = active_subskills_parts_id
        self.active_subskill_id = active_subskill_id
        self.active_part_id = active_part_id
        self.order_idx = order_idx
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]

    def _lookup_columns(self):
        return ['active_subskill_id', 'active_part_id', 'order_idx']

    def __str__(self):
        return 'ActiveSubskillsParts({}): {} -> {} (#{})'.format(self.key_value(), self.active_subskill_id,
                                                                 self.active_part_id, self.order_idx)


def upsert_active_skill_data(db: DbWrapper, skill: CrossServerSkill):
    db.insert_or_update(ActiveSkill.from_css(skill))
    for c, subskill in enumerate(skill.cur_skill.subskills):
        db.insert_or_update(ActiveSubskill.from_as(subskill))
        for c2, part in enumerate(subskill.parts):
            db.insert_or_update(ActivePart.from_as(part))
            db.insert_or_update(ActiveSubskillsParts.from_css(subskill, part, c2))
        db.insert_or_update(ActiveSkillsSubskills.from_css(skill, subskill, c))


class LeaderSkill(ServerDependentSqlItem):
    """Monster leader skill."""
    KEY_COL = 'leader_skill_id'
    BASE_TABLE = 'leader_skills'

    @staticmethod
    def from_css(css: CrossServerSkill) -> 'LeaderSkill':
        jp_skill = css.jp_skill
        na_skill = css.na_skill
        kr_skill = css.kr_skill
        cur_skill = css.cur_skill

        jp_ls_converter = JaLSTextConverter()
        en_ls_converter = EnLSTextConverter()
        desc_ja = cur_skill.full_text(jp_ls_converter) or jp_skill.raw_description
        desc_en = cur_skill.full_text(en_ls_converter) or na_skill.raw_description
        skill_type_tags = skill_text_typing.parse_ls_conditions(css)
        tags = skill_text_typing.format_conditions(skill_type_tags)

        # In the event that we don't have KR data, use the NA name and calculated description.
        name_ko = kr_skill.name if cur_skill != kr_skill else na_skill.name
        desc_ko = kr_skill.raw_description if cur_skill != kr_skill else desc_en

        return LeaderSkill(
            leader_skill_id=jp_skill.skill_id,
            name_ja=jp_skill.name,
            name_en=na_skill.name,
            name_ko=name_ko,
            desc_ja=desc_ja,
            desc_en=desc_en,
            desc_ko=desc_ko,
            max_hp=cur_skill.hp,
            max_atk=cur_skill.atk,
            max_rcv=cur_skill.rcv,
            max_shield=cur_skill.shield,
            max_combos=cur_skill.extra_combos,
            mult_bonus_damage=cur_skill.mult_bonus_damage,
            bonus_damage=cur_skill.bonus_damage,
            extra_time=cur_skill.extra_time,
            tags=tags)

    def __init__(self,
                 leader_skill_id: int = None,
                 name_ja: str = None,
                 name_en: str = None,
                 name_ko: str = None,
                 desc_ja: str = None,
                 desc_en: str = None,
                 desc_ko: str = None,
                 max_hp: float = None,
                 max_atk: float = None,
                 max_rcv: float = None,
                 max_shield: float = None,
                 max_combos: int = None,
                 bonus_damage: int = None,
                 mult_bonus_damage: int = None,
                 extra_time: float = None,
                 tags: str = None,
                 tstamp: int = None):
        self.leader_skill_id = leader_skill_id
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.desc_ja = desc_ja
        self.desc_en = desc_en
        self.desc_ko = desc_ko
        self.max_hp = max_hp
        self.max_atk = max_atk
        self.max_rcv = max_rcv
        self.max_shield = max_shield
        self.max_combos = max_combos
        self.bonus_damage = bonus_damage
        self.mult_bonus_damage = mult_bonus_damage
        self.extra_time = extra_time
        self.tags = tags
        self.tstamp = tstamp

    def __str__(self):
        return 'LeaderSkill({}): {} -> {}'.format(self.key_value(), self.name_en, self.desc_en)
