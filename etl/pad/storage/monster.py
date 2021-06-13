import os
from datetime import date
from typing import List, Optional

from pad.common.shared_types import Server, MonsterId, MonsterNo
from pad.common.utils import format_int_list, classproperty
from pad.db import sql_item
from pad.db.sql_item import SimpleSqlItem, ExistsStrategy
from pad.raw.skills import skill_text_typing
from pad.raw.skills.en.active_skill_text import EnASTextConverter
from pad.raw.skills.en.leader_skill_text import EnLSTextConverter
from pad.raw.skills.jp.active_skill_text import JpASTextConverter
from pad.raw.skills.jp.leader_skill_text import JpLSTextConverter
from pad.raw_processor.crossed_data import CrossServerCard, CrossServerSkill
from pad.storage.series import Series


class Monster(SimpleSqlItem):
    """Monster data."""
    KEY_COL = 'monster_id'

    @classproperty
    def TABLE(cls):
        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return 'monsters_na'
        # elif server.upper() == "JP":
        #    return 'monsters_jp'
        # elif server.upper() == "KR":
        #     return 'monsters_kr'
        else:
            return 'monsters'

    @staticmethod
    def from_csm(o: CrossServerCard) -> 'Monster':
        jp_card = o.jp_card.card
        na_card = o.na_card.card
        kr_card = o.kr_card.card
        cur_card = o.cur_card.card

        max_level = cur_card.max_level
        if max_level == 1:
            exp = 0
        else:
            exp = round(cur_card.xp_curve().value_at(max_level))

        awakenings = format_int_list(cur_card.awakenings)
        super_awakenings = format_int_list(cur_card.super_awakenings)
        orb_skin_id = cur_card.orb_skin_id or None
        voice_id_jp = cur_card.voice_id or None if o.jp_card.server == Server.jp else None
        voice_id_na = cur_card.voice_id or None if o.na_card.server == Server.na else None
        linked_monster_id = o.cur_card.linked_monster_id or o.jp_card.linked_monster_id or o.na_card.linked_monster_id
        latent_slots = 8 if cur_card.latent_slot_unlock_flag else 6

        def none_or(value: int):
            return value if value > -1 else None

        on_jp = o.jp_card.server == Server.jp and jp_card.released_status
        on_na = o.na_card.server == Server.na and na_card.released_status
        on_kr = o.kr_card.server == Server.kr and kr_card.released_status

        diff_possible = on_jp and on_na

        def extract_skill_data(s):
            if s is None:
                return s
            return s.raw_data

        diff_stats = diff_possible and (jp_card.max_hp != na_card.max_hp or         # This whole block is only
                                        jp_card.max_atk != na_card.max_atk or       # applicable when dealing with
                                        jp_card.max_rcv != na_card.max_rcv or       # JP cards.  Ignore when building
                                        jp_card.max_level != na_card.max_level or   # a NA database.
                                        jp_card.limit_mult != na_card.limit_mult)
        diff_awakenings = diff_possible and (jp_card.awakenings != na_card.awakenings or
                                             jp_card.super_awakenings != na_card.super_awakenings)
        diff_leader_skill = diff_possible and (extract_skill_data(o.jp_card.leader_skill) !=
                                               extract_skill_data(o.na_card.leader_skill))
        diff_active_skill = diff_possible and (extract_skill_data(o.jp_card.active_skill) !=
                                               extract_skill_data(o.na_card.active_skill))

        return Monster(
            monster_id=o.monster_id,
            monster_no_jp=jp_card.monster_no,
            monster_no_na=na_card.monster_no,
            monster_no_kr=kr_card.monster_no,
            name_ja=jp_card.name,
            name_en=na_card.name,
            name_ko=kr_card.name,
            pronunciation_ja=jp_card.furigana,
            hp_min=cur_card.min_hp,
            hp_max=cur_card.max_hp,
            hp_scale=cur_card.hp_scale,
            atk_min=cur_card.min_atk,
            atk_max=cur_card.max_atk,
            atk_scale=cur_card.atk_scale,
            rcv_min=cur_card.min_rcv,
            rcv_max=cur_card.max_rcv,
            rcv_scale=cur_card.rcv_scale,
            cost=cur_card.cost,
            exp=exp,
            level=max_level,
            rarity=cur_card.rarity,
            limit_mult=cur_card.limit_mult,
            attribute_1_id=cur_card.attr_id,
            attribute_2_id=none_or(cur_card.sub_attr_id),
            leader_skill_id=jp_card.leader_skill_id,
            active_skill_id=jp_card.active_skill_id,
            type_1_id=cur_card.type_1_id,
            type_2_id=none_or(cur_card.type_2_id),
            type_3_id=none_or(cur_card.type_3_id),
            awakenings=awakenings,
            super_awakenings=super_awakenings,
            inheritable=cur_card.inheritable,
            stackable=cur_card.is_stackable,
            fodder_exp=int(cur_card.feed_xp_curve().value_at(max_level)),
            sell_gold=int(cur_card.sell_gold_curve().value_at(max_level)),
            sell_mp=cur_card.sell_mp,
            buy_mp=None,
            reg_date=date.today().isoformat(),
            on_jp=on_jp,
            on_na=on_na,
            on_kr=on_kr,
            diff_stats=diff_stats,
            diff_awakenings=diff_awakenings,
            diff_leader_skill=diff_leader_skill,
            diff_active_skill=diff_active_skill,
            base_id=o.cur_card.no_to_id(cur_card.base_id),
            has_animation=o.has_animation,
            has_hqimage=o.has_hqimage,
            orb_skin_id=orb_skin_id,
            voice_id_jp=voice_id_jp,
            voice_id_na=voice_id_na,
            linked_monster_id=linked_monster_id,
            latent_slots=latent_slots)

    def __init__(self,
                 monster_id: int = None,
                 monster_no_jp: int = None,
                 monster_no_na: int = None,
                 monster_no_kr: int = None,
                 name_ja: str = None,
                 name_en: str = None,
                 name_ko: str = None,
                 pronunciation_ja: str = None,
                 hp_min: int = None,
                 hp_max: int = None,
                 hp_scale: float = None,
                 atk_min: int = None,
                 atk_max: int = None,
                 atk_scale: float = None,
                 rcv_min: int = None,
                 rcv_max: int = None,
                 rcv_scale: float = None,
                 cost: int = None,
                 exp: int = None,
                 level: int = None,
                 rarity: int = None,
                 limit_mult: int = None,
                 attribute_1_id: int = None,
                 attribute_2_id: int = None,
                 leader_skill_id: int = None,
                 active_skill_id: int = None,
                 type_1_id: int = None,
                 type_2_id: int = None,
                 type_3_id: int = None,
                 awakenings: str = None,
                 super_awakenings: str = None,
                 inheritable: bool = None,
                 stackable: bool = None,
                 fodder_exp: int = None,
                 sell_gold: int = None,
                 sell_mp: int = None,
                 buy_mp: int = None,
                 reg_date: str = None,
                 on_jp: bool = None,
                 on_na: bool = None,
                 on_kr: bool = None,
                 diff_stats: bool = None,
                 diff_awakenings: bool = None,
                 diff_leader_skill: bool = None,
                 diff_active_skill: bool = None,
                 base_id: int = None,
                 has_animation: bool = None,
                 has_hqimage: bool = None,
                 orb_skin_id: int = None,
                 voice_id_jp: int = None,
                 voice_id_na: int = None,
                 linked_monster_id: int = None,
                 latent_slots: int = None,
                 tstamp: int = None):
        self.monster_id = monster_id
        self.monster_no_jp = monster_no_jp
        self.monster_no_na = monster_no_na
        self.monster_no_kr = monster_no_kr
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.pronunciation_ja = pronunciation_ja
        self.hp_min = hp_min
        self.hp_max = hp_max
        self.hp_scale = hp_scale
        self.atk_min = atk_min
        self.atk_max = atk_max
        self.atk_scale = atk_scale
        self.rcv_min = rcv_min
        self.rcv_max = rcv_max
        self.rcv_scale = rcv_scale
        self.cost = cost
        self.exp = exp
        self.level = level
        self.rarity = rarity
        self.limit_mult = limit_mult
        self.attribute_1_id = attribute_1_id
        self.attribute_2_id = attribute_2_id
        self.leader_skill_id = leader_skill_id
        self.active_skill_id = active_skill_id
        self.type_1_id = type_1_id
        self.type_2_id = type_2_id
        self.type_3_id = type_3_id
        self.awakenings = awakenings
        self.super_awakenings = super_awakenings
        self.inheritable = inheritable
        self.stackable = stackable
        self.fodder_exp = fodder_exp
        self.sell_gold = sell_gold
        self.sell_mp = sell_mp
        self.buy_mp = buy_mp
        self.reg_date = reg_date
        self.on_jp = on_jp
        self.on_na = on_na
        self.on_kr = on_kr
        self.diff_stats = diff_stats
        self.diff_awakenings = diff_awakenings
        self.diff_leader_skill = diff_leader_skill
        self.diff_active_skill = diff_active_skill
        self.base_id = base_id
        self.has_animation = has_animation
        self.has_hqimage = has_hqimage
        self.orb_skin_id = orb_skin_id
        self.voice_id_jp = voice_id_jp
        self.voice_id_na = voice_id_na
        self.linked_monster_id = linked_monster_id
        self.latent_slots = latent_slots
        self.tstamp = tstamp

    def _non_auto_update_cols(self):
        return [
            'buy_mp',
            'reg_date',
            'has_animation',
            'has_hqimage',
        ]

    def __str__(self):
        return 'Monster({}): {}'.format(self.key_value(), self.name_en)


class MonsterWithExtraImageInfo(SimpleSqlItem):
    """Monster helper for updating the image-related info."""
    KEY_COL = 'monster_id'

    @classproperty
    def TABLE(cls):
        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return 'monsters_na'
        # elif server.upper() == "JP":
        #    return 'monsters_jp'
        # elif server.upper() == "KR":
        #     return 'monsters_kr'
        else:
            return 'monsters'

    def __init__(self,
                 monster_id: int = None,
                 has_animation: bool = None,
                 has_hqimage: bool = None,
                 tstamp: int = None):
        self.monster_id = monster_id
        self.has_animation = has_animation
        self.has_hqimage = has_hqimage
        self.tstamp = tstamp

    def __str__(self):
        return 'MonsterImage({}): animated={} hq={}'.format(self.key_value(), self.has_animation, self.has_hqimage)


class MonsterWithMPValue(SimpleSqlItem):
    """Monster helper for inserting MP purchase."""
    KEY_COL = 'monster_id'

    @classproperty
    def TABLE(cls):
        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return 'monsters_na'
        # elif server.upper() == "JP":
        #    return 'monsters_jp'
        # elif server.upper() == "KR":
        #     return 'monsters_kr'
        else:
            return 'monsters'

    def __init__(self,
                 monster_id: int = None,
                 buy_mp: int = None,
                 tstamp: int = None):
        self.monster_id = monster_id
        self.buy_mp = buy_mp
        self.tstamp = tstamp

    def __str__(self):
        return 'MonsterMP({}): {}'.format(self.key_value(), self.buy_mp)


class ActiveSkill(SimpleSqlItem):
    """Monster active skill."""
    KEY_COL = 'active_skill_id'

    @classproperty
    def TABLE(cls):
        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return 'active_skills_na'
        # elif server.upper() == "JP":
        #    return 'active_skills_jp'
        # elif server.upper() == "KR":
        #     return 'active_skills_kr'
        else:
            return 'active_skills'

    @staticmethod
    def from_css(css: CrossServerSkill) -> 'ActiveSkill':
        jp_skill = css.jp_skill
        na_skill = css.na_skill
        kr_skill = css.kr_skill
        cur_skill = css.cur_skill

        jp_as_converter = JpASTextConverter()
        ja_description = cur_skill.full_text(jp_as_converter)

        en_as_converter = EnASTextConverter()
        en_description = cur_skill.full_text(en_as_converter)

        skill_type_tags = skill_text_typing.parse_as_conditions(css)
        tags = skill_text_typing.format_conditions(skill_type_tags)

        # In the event that we don't have KR data, use the NA name and calculated description.
        kr_name = kr_skill.name if cur_skill != kr_skill else na_skill.name
        ko_desc = kr_skill.raw_description if cur_skill != kr_skill else en_description

        return ActiveSkill(
            active_skill_id=jp_skill.skill_id,
            name_ja=cur_skill.name,
            name_en=na_skill.name,
            name_ko=kr_name,
            desc_ja=ja_description,
            desc_en=en_description,
            desc_ko=ko_desc,
            turn_max=cur_skill.turn_max,
            turn_min=cur_skill.turn_min,
            tags=tags)

    def __init__(self,
                 active_skill_id: int = None,
                 name_ja: str = None,
                 name_en: str = None,
                 name_ko: str = None,
                 desc_ja: str = None,
                 desc_en: str = None,
                 desc_ko: str = None,
                 turn_max: int = None,
                 turn_min: int = None,
                 tags: str = None,
                 tstamp: int = None):
        self.active_skill_id = active_skill_id
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
        self.desc_ja = desc_ja
        self.desc_en = desc_en
        self.desc_ko = desc_ko
        self.turn_max = turn_max
        self.turn_min = turn_min
        self.tags = tags
        self.tstamp = tstamp

    def __str__(self):
        return 'Active({}): {} -> {}'.format(self.key_value(), self.name_en, self.desc_en)


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

        en_ls_converter = EnLSTextConverter()
        jp_ls_converter = JpLSTextConverter()
        en_description = cur_skill.full_text(en_ls_converter) or na_skill.raw_description
        ja_description = cur_skill.full_text(jp_ls_converter) or jp_skill.raw_description
        skill_type_tags = skill_text_typing.parse_ls_conditions(css)
        tags = skill_text_typing.format_conditions(skill_type_tags)

        # In the event that we don't have KR data, use the NA name and calculated description.
        kr_name = kr_skill.name if cur_skill != kr_skill else na_skill.name
        ko_desc = kr_skill.raw_description if cur_skill != kr_skill else en_description

        return LeaderSkill(
            leader_skill_id=jp_skill.skill_id,
            name_ja=jp_skill.name,
            name_en=na_skill.name,
            name_ko=kr_name,
            desc_ja=ja_description,
            desc_en=en_description,
            desc_ko=ko_desc,
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


class Awakening(SimpleSqlItem):
    """Monster awakening entry."""
    KEY_COL = 'awakening_id'

    @classproperty
    def TABLE(cls):
        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return 'awakenings_na'
        # elif server.upper() == "JP":
        #    return 'awakenings_jp'
        # elif server.upper() == "KR":
        #     return 'awakenings_kr'
        else:
            return 'awakenings'

    @staticmethod
    def from_csm(o: CrossServerCard) -> List['Awakening']:
        awakenings = [(a_id, False) for a_id in o.cur_card.card.awakenings]
        awakenings.extend([(sa_id, True) for sa_id in o.cur_card.card.super_awakenings])
        results = []
        for i, v in enumerate(awakenings):
            results.append(Awakening(
                awakening_id=None,  # Key that is looked up or inserted
                monster_id=o.monster_id,
                awoken_skill_id=v[0],
                is_super=v[1],
                order_idx=i))
        return results

    def __init__(self,
                 awakening_id: int = None,
                 monster_id: int = None,
                 awoken_skill_id: int = None,
                 is_super: bool = None,
                 order_idx: int = None,
                 tstamp: int = None):
        self.awakening_id = awakening_id
        self.monster_id = monster_id
        self.awoken_skill_id = awoken_skill_id
        self.is_super = is_super
        self.order_idx = order_idx
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def value_exists_sql(self):
        sql = """
        SELECT awakening_id FROM {table}
        WHERE monster_id = {monster_id} and order_idx = {order_idx}
        """.format(table=self._table(), **sql_item.object_to_sql_params(self))
        return sql

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]

    def __str__(self):
        return 'Awakening ({}): {} -> {}, super={}'.format(
            self.key_value(), self.monster_id, self.awoken_skill_id, self.is_super)


class Evolution(SimpleSqlItem):
    """Monster evolution entry."""
    KEY_COL = 'evolution_id'

    @classproperty
    def TABLE(cls):
        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return 'evolutions_na'
        # elif server.upper() == "JP":
        #    return 'evolutions_jp'
        # elif server.upper() == "KR":
        #     return 'evolutions_kr'
        else:
            return 'evolutions'

    @staticmethod
    def from_csm(o: CrossServerCard) -> Optional['Evolution']:
        card = o.cur_card.card

        def convert(x: MonsterNo) -> MonsterId:
            return o.cur_card.no_to_id(x)

        def safe_convert(x: MonsterNo) -> MonsterId:
            return convert(x) if x else None

        reversible = False
        if card.is_ult and card.un_evo_mat_1 > 0:
            reversible = True
        elif 49 in card.awakenings:
            reversible = True

        return Evolution(
            evolution_id=None,  # Key that is looked up or inserted
            evolution_type=0,  # Eventually remove this.  evolution_type is deprecated and barely works as is
            reversible=reversible,
            from_id=convert(card.ancestor_id),
            to_id=convert(card.monster_no),
            mat_1_id=safe_convert(card.evo_mat_id_1),
            mat_2_id=safe_convert(card.evo_mat_id_2),
            mat_3_id=safe_convert(card.evo_mat_id_3),
            mat_4_id=safe_convert(card.evo_mat_id_4),
            mat_5_id=safe_convert(card.evo_mat_id_5))

    def __init__(self,
                 evolution_id: int = None,
                 evolution_type: int = None,
                 reversible: bool = None,
                 from_id: MonsterId = None,
                 to_id: MonsterId = None,
                 mat_1_id: MonsterId = None,
                 mat_2_id: MonsterId = None,
                 mat_3_id: MonsterId = None,
                 mat_4_id: MonsterId = None,
                 mat_5_id: MonsterId = None,
                 tstamp: int = None):
        self.evolution_id = evolution_id
        self.evolution_type = evolution_type
        self.reversible = reversible
        self.from_id = from_id
        self.to_id = to_id
        self.mat_1_id = mat_1_id
        self.mat_2_id = mat_2_id
        self.mat_3_id = mat_3_id
        self.mat_4_id = mat_4_id
        self.mat_5_id = mat_5_id
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]

    def _lookup_columns(self):
        return ['from_id', 'to_id']

    def __str__(self):
        return 'Evo ({}): {} -> {}, type={}'.format(self.key_value(), self.from_id, self.to_id, self.evolution_type)


class AltMonster(SimpleSqlItem):
    """Alt. monster data."""
    KEY_COL = 'alt_monster_id'

    @classproperty
    def TABLE(cls):
        server = os.environ.get("CURRENT_PIPELINE_SERVER") or ""
        if server.upper() == "NA":
            return 'alt_monsters_na'
        # elif server.upper() == "JP":
        #    return 'alt_monsters_jp'
        # elif server.upper() == "KR":
        #     return 'alt_monsters_kr'
        else:
            return 'alt_monsters'

    @staticmethod
    def from_csm(o: CrossServerCard) -> 'AltMonster':
        return AltMonster(
            alt_monster_id=o.monster_id,
            canonical_id=o.monster_id % 1000000,
            active_skill_id=o.cur_card.card.active_skill_id,
            reg_date=date.today().isoformat(),
            is_alt=20000 <= o.monster_id)

    def __init__(self,
                 alt_monster_id: int = None,
                 canonical_id: int = None,
                 active_skill_id: int = None,
                 reg_date: str = None,
                 is_alt: bool = None,
                 tstamp: int = None):
        self.alt_monster_id = alt_monster_id
        self.canonical_id = canonical_id
        self.active_skill_id = active_skill_id
        self.reg_date = reg_date
        self.is_alt = is_alt
        self.tstamp = tstamp

    def _non_auto_update_cols(self):
        return ['reg_date']

    def __str__(self):
        return 'AltMonster({})'.format(self.key_value())
