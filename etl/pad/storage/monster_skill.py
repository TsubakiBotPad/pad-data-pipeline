import os

from pad.common.utils import classproperty
from pad.db.db_util import DbWrapper
from pad.db.sql_item import ExistsStrategy, SimpleSqlItem
from pad.raw.skills import skill_text_typing
from pad.raw.skills.active_skill_info import ASCompound, ASEvolvingSkill, ASLoopingEvolvingSkill, ASMultiPartSkill, \
    ASRandomSkill, ActiveSkill as ASSkill
from pad.raw.skills.en.active_skill_text import EnASTextConverter
from pad.raw.skills.en.leader_skill_text import EnLSTextConverter
from pad.raw.skills.ja.active_skill_text import JaASTextConverter
from pad.raw.skills.ja.leader_skill_text import JaLSTextConverter
from pad.raw.skills.ko.active_skill_text import KoASTextConverter
from pad.raw_processor.crossed_data import CrossServerSkill


class ActiveSkill(SimpleSqlItem):
    """Monster active skill."""
    KEY_COL = 'active_skill_id'

    @classproperty
    def TABLE(cls):
        base_table_name = 'active_skills'

        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return base_table_name + '_na'
        # elif server.upper() == "JP":
        #    return base_table_name + '_jp'
        # elif server.upper() == "KR":
        #    return base_table_name + '_kr'
        else:
            return base_table_name

    @staticmethod
    def from_css(css: CrossServerSkill) -> 'ActiveSkill':
        jp_skill = css.jp_skill
        na_skill = css.na_skill
        kr_skill = css.kr_skill
        cur_skill = css.cur_skill

        desc_ja = cur_skill.full_text(JaASTextConverter())
        desc_ja_templated = cur_skill.templated_text(JaASTextConverter())
        desc_en = cur_skill.full_text(EnASTextConverter())
        desc_en_templated = cur_skill.templated_text(EnASTextConverter())
        desc_ko = cur_skill.full_text(KoASTextConverter())
        desc_ko_templated = cur_skill.templated_text(KoASTextConverter())

        skill_type_tags = skill_text_typing.parse_as_conditions(css)
        tags = skill_text_typing.format_conditions(skill_type_tags)

        return ActiveSkill(
            active_skill_id=jp_skill.skill_id,
            name_ja=jp_skill.name,
            name_en=na_skill.name,
            name_ko=kr_skill.name,
            desc_ja=desc_ja,
            desc_ja_templated=desc_ja_templated,
            desc_en=desc_en,
            desc_en_templated=desc_en_templated,
            desc_ko=desc_ko,
            desc_ko_templated=desc_ko_templated,
            turn_max=cur_skill.turn_max,
            turn_min=cur_skill.turn_min,
            tags=tags)

    @staticmethod
    def from_as(act: ASSkill) -> 'ActiveSkill':
        desc_ja = act.full_text(JaASTextConverter())
        desc_ja_templated = act.templated_text(JaASTextConverter())
        desc_en = act.full_text(EnASTextConverter())
        desc_en_templated = act.templated_text(EnASTextConverter())
        desc_ko = act.full_text(KoASTextConverter())
        desc_ko_templated = act.templated_text(KoASTextConverter())

        skill_type_tags = skill_text_typing.parse_as_conditions(act, True)
        tags = skill_text_typing.format_conditions(skill_type_tags)

        return ActiveSkill(
            active_skill_id=act.skill_id,
            name_ja="",
            name_en="",
            name_ko="",
            desc_ja=desc_ja,
            desc_ja_templated=desc_ja_templated,
            desc_en=desc_en,
            desc_en_templated=desc_en_templated,
            desc_ko=desc_ko,
            desc_ko_templated=desc_ko_templated,
            turn_max=act.turn_max or -1,
            turn_min=act.turn_min or -1,
            tags=tags)

    def __init__(self,
                 active_skill_id: int = None,
                 name_ja: str = None,
                 name_en: str = None,
                 name_ko: str = None,
                 desc_ja: str = None,
                 desc_ja_templated: str = None,
                 desc_en: str = None,
                 desc_en_templated: str = None,
                 desc_ko: str = None,
                 desc_ko_templated: str = None,
                 turn_max: int = None,
                 turn_min: int = None,
                 tags: str = None,
                 tstamp: int = None):
        self.active_skill_id = active_skill_id
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.desc_ja = desc_ja
        self.desc_ja_templated = desc_ja_templated
        self.desc_en = desc_en
        self.desc_en_templated = desc_en_templated
        self.desc_ko = desc_ko
        self.desc_ko_templated = desc_ko_templated
        self.turn_max = turn_max
        self.turn_min = turn_min
        self.tags = tags
        self.tstamp = tstamp

    def __str__(self):
        return 'Active({}): {} -> {}'.format(self.key_value(), self.name_en, self.desc_en)


class ActivePart(SimpleSqlItem):
    """Monster active skill part."""
    KEY_COL = 'active_part_id'

    @classproperty
    def TABLE(cls):
        base_table_name = 'active_parts'

        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return base_table_name + '_na'
        # elif server.upper() == "JP":
        #    return base_table_name + '_jp'
        # elif server.upper() == "KR":
        #    return base_table_name + '_kr'
        else:
            return base_table_name

    @staticmethod
    def from_css(act: ASSkill) -> 'ActivePart':
        desc_ja = act.full_text(JaASTextConverter())
        desc_ja_templated = act.templated_text(JaASTextConverter())
        desc_en = act.full_text(EnASTextConverter())
        desc_en_templated = act.templated_text(EnASTextConverter())
        desc_ko = act.full_text(KoASTextConverter())
        desc_ko_templated = act.templated_text(KoASTextConverter())

        skill_type_tags = skill_text_typing.parse_as_conditions(act, True)
        tags = skill_text_typing.format_conditions(skill_type_tags)

        return ActivePart(
            active_part_id=act.skill_id,
            active_skill_type_id=act.skill_type,
            desc_ja=desc_ja,
            desc_ja_templated=desc_ja_templated,
            desc_en=desc_en,
            desc_en_templated=desc_en_templated,
            desc_ko=desc_ko,
            desc_ko_templated=desc_ko_templated,
            tags=tags)

    def __init__(self,
                 active_part_id: int = None,
                 active_skill_type_id: int = None,
                 desc_ja: str = None,
                 desc_ja_templated: str = None,
                 desc_en: str = None,
                 desc_en_templated: str = None,
                 desc_ko: str = None,
                 desc_ko_templated: str = None,
                 tags: str = None,
                 tstamp: int = None):
        self.active_part_id = active_part_id
        self.active_skill_type_id = active_skill_type_id
        self.desc_ja_templated = desc_ja_templated
        self.desc_en = desc_en
        self.desc_en_templated = desc_en_templated
        self.desc_ko = desc_ko
        self.desc_ko_templated = desc_ko_templated
        self.tags = tags
        self.tstamp = tstamp

    def __str__(self):
        return 'ActivePart({}): {}'.format(self.key_value(), self.desc_en)


class ActiveSkillParts(SimpleSqlItem):
    """Active skills to their parts."""
    KEY_COL = 'active_skill_part_id'

    @classproperty
    def TABLE(cls):
        base_table_name = 'active_skill_parts'

        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return base_table_name + '_na'
        # elif server.upper() == "JP":
        #    return base_table_name + '_jp'
        # elif server.upper() == "KR":
        #    return base_table_name + '_kr'
        else:
            return base_table_name

    @staticmethod
    def from_css(skill: CrossServerSkill, part: ASSkill, order_idx: int = 0) \
            -> 'ActiveSkillParts':
        skill = skill.cur_skill

        return ActiveSkillParts(
            active_skill_part_id=None,  # Key that is looked up or inserted
            active_skill_id=skill.skill_id,
            active_part_id=part.skill_id,
            order_idx=order_idx)

    def __init__(self,
                 active_skill_part_id: int = None,
                 active_skill_id: int = None,
                 active_part_id: int = None,
                 order_idx: int = None,
                 tstamp: int = None):
        self.active_skill_part_id = active_skill_part_id
        self.active_skill_id = active_skill_id
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
        return ['active_skill_id', 'active_part_id', 'order_idx']

    def __str__(self):
        return 'ActiveSkillParts({}): {} -> {} (#{})'.format(self.key_value(), self.active_skill_id,
                                                             self.active_part_id, self.order_idx)


class ActiveSkillsCompound(SimpleSqlItem):
    """Active skills to their subskills."""
    KEY_COL = 'active_skills_compound_id'

    @classproperty
    def TABLE(cls):
        base_table_name = 'active_skills_compound'

        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return base_table_name + '_na'
        # elif server.upper() == "JP":
        #    return base_table_name + '_jp'
        # elif server.upper() == "KR":
        #    return base_table_name + '_kr'
        else:
            return base_table_name

    @staticmethod
    def from_css(skill: CrossServerSkill, subskill: ASSkill, order_idx: int = 0) \
            -> 'ActiveSkillsCompound':
        skill = skill.cur_skill

        compound_skill_type_id = 0
        if isinstance(skill, ASRandomSkill):
            compound_skill_type_id = 1
        elif isinstance(skill, ASEvolvingSkill):
            compound_skill_type_id = 2
        elif isinstance(skill, ASLoopingEvolvingSkill):
            compound_skill_type_id = 3

        return ActiveSkillsCompound(
            active_skills_compound_id=None,  # Key that is looked up or inserted
            compound_skill_type_id=compound_skill_type_id,
            active_skill_id=skill.skill_id,
            child_active_skill_id=subskill.skill_id,
            order_idx=order_idx)

    def __init__(self,
                 active_skills_compound_id: int = None,
                 compound_skill_type_id: int = None,
                 active_skill_id: int = None,
                 child_active_skill_id: int = None,
                 order_idx: int = None,
                 tstamp: int = None):
        self.active_skills_compound_id = active_skills_compound_id
        self.compound_skill_type_id = compound_skill_type_id
        self.active_skill_id = active_skill_id
        self.child_active_skill_id = child_active_skill_id
        self.order_idx = order_idx
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]

    def _lookup_columns(self):
        return ['active_skill_id', 'child_active_skill_id', 'order_idx']

    def __str__(self):
        return 'ActiveSkillsCompound({}): {} -> {} (#{})'.format(self.key_value(), self.active_skill_id,
                                                                self.child_active_skill_id, self.order_idx)


def upsert_active_skill_data(db: DbWrapper, skill: CrossServerSkill):
    db.insert_or_update(ActivePart.from_css(skill.cur_skill))
    for part in skill.cur_skill.parts:
        db.insert_or_update(ActivePart.from_css(part))

    if isinstance(skill.cur_skill, ASMultiPartSkill):
        for c, part in enumerate(skill.cur_skill.parts):
            db.insert_or_update(ActiveSkillParts.from_css(skill, part, c))
    else:
        db.insert_or_update(ActiveSkillParts.from_css(skill, skill.cur_skill, 0))

    if isinstance(skill.cur_skill, ASCompound):
        for c, subskill in enumerate(skill.cur_skill.child_skills):
            db.insert_or_update(ActiveSkill.from_as(subskill))
            db.insert_or_update(ActiveSkillsCompound.from_css(skill, subskill, c))
    else:
        db.insert_or_update(ActiveSkillsCompound.from_css(skill, skill.cur_skill, 0))


class LeaderSkill(SimpleSqlItem):
    """Monster leader skill."""
    KEY_COL = 'leader_skill_id'

    @classproperty
    def TABLE(cls):
        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return 'leader_skills_na'
        # elif server.upper() == "JP":
        #    return 'leader_skills_jp'
        # elif server.upper() == "KR":
        #     return 'leader_skills_kr'
        else:
            return 'leader_skills'

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
        return 'Leader ({}): {} -> {}'.format(self.key_value(), self.name_en, self.desc_en)
