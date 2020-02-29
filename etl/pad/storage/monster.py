from datetime import date
from typing import List, Optional

from pad.common.shared_types import Server, MonsterId, MonsterNo, EvolutionType
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
    TABLE = 'monsters'
    KEY_COL = 'monster_id'

    @staticmethod
    def from_csm(o: CrossServerCard) -> 'Monster':
        jp_card = o.jp_card.card
        na_card = o.na_card.card
        kr_card = o.kr_card.card

        max_level = jp_card.max_level
        if max_level == 1:
            exp = 0
        else:
            exp = round(jp_card.xp_curve().value_at(max_level))

        orb_skin_id = jp_card.orb_skin_id or None
        voice_id_jp = jp_card.voice_id or None if o.jp_card.server == Server.jp else None
        voice_id_na = na_card.voice_id or None if o.na_card.server == Server.na else None
        linked_monster_id = o.jp_card.linked_monster_id or o.na_card.linked_monster_id

        def none_or(value: int):
            return value if value > -1 else None

        return Monster(
            monster_id=o.monster_id,
            monster_no_jp=jp_card.monster_no,
            monster_no_na=na_card.monster_no,
            monster_no_kr=kr_card.monster_no,
            name_jp=jp_card.name,
            name_na=na_card.name,
            name_kr=kr_card.name,
            pronunciation_jp=jp_card.furigana,
            hp_min=jp_card.min_hp,
            hp_max=jp_card.max_hp,
            hp_scale=jp_card.hp_scale,
            atk_min=jp_card.min_atk,
            atk_max=jp_card.max_atk,
            atk_scale=jp_card.atk_scale,
            rcv_min=jp_card.min_rcv,
            rcv_max=jp_card.max_rcv,
            rcv_scale=jp_card.rcv_scale,
            cost=jp_card.cost,
            exp=exp,
            level=max_level,
            rarity=jp_card.rarity,
            limit_mult=jp_card.limit_mult,
            attribute_1_id=jp_card.attr_id,
            attribute_2_id=none_or(jp_card.sub_attr_id),
            leader_skill_id=jp_card.leader_skill_id,
            active_skill_id=jp_card.active_skill_id,
            type_1_id=jp_card.type_1_id,
            type_2_id=none_or(jp_card.type_2_id),
            type_3_id=none_or(jp_card.type_3_id),
            inheritable=jp_card.inheritable,
            fodder_exp=int(jp_card.feed_xp_curve().value_at(max_level)),
            sell_gold=int(jp_card.sell_gold_curve().value_at(max_level)),
            sell_mp=jp_card.sell_mp,
            buy_mp=None,
            reg_date=date.today().isoformat(),
            on_jp=o.jp_card.server == Server.jp and jp_card.released_status,
            on_na=o.na_card.server == Server.na and na_card.released_status,
            on_kr=o.kr_card.server == Server.kr and kr_card.released_status,
            pal_egg=False,
            rem_egg=False,
            series_id=Series.UNSORTED_SERIES_ID,
            orb_skin_id=orb_skin_id,
            voice_id_jp=voice_id_jp,
            voice_id_na=voice_id_na,
            linked_monster_id=linked_monster_id)

    def __init__(self,
                 monster_id: int = None,
                 monster_no_jp: int = None,
                 monster_no_na: int = None,
                 monster_no_kr: int = None,
                 name_jp: str = None,
                 name_na: str = None,
                 name_kr: str = None,
                 pronunciation_jp: str = None,
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
                 inheritable: bool = None,
                 fodder_exp: int = None,
                 sell_gold: int = None,
                 sell_mp: int = None,
                 buy_mp: int = None,
                 reg_date: str = None,
                 on_jp: bool = None,
                 on_na: bool = None,
                 on_kr: bool = None,
                 pal_egg: bool = None,
                 rem_egg: bool = None,
                 series_id: int = None,
                 orb_skin_id: int = None,
                 voice_id_jp: int = None,
                 voice_id_na: int = None,
                 linked_monster_id: int = None,
                 tstamp: int = None):
        self.monster_id = monster_id
        self.monster_no_jp = monster_no_jp
        self.monster_no_na = monster_no_na
        self.monster_no_kr = monster_no_kr
        self.name_jp = name_jp
        self.name_na = name_na
        self.name_kr = name_kr
        self.pronunciation_jp = pronunciation_jp
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
        self.inheritable = inheritable
        self.fodder_exp = fodder_exp
        self.sell_gold = sell_gold
        self.sell_mp = sell_mp
        self.buy_mp = buy_mp
        self.reg_date = reg_date
        self.on_jp = on_jp
        self.on_na = on_na
        self.on_kr = on_kr
        self.pal_egg = pal_egg
        self.rem_egg = rem_egg
        self.series_id = series_id
        self.has_animation = False
        self.has_hqimage = False
        self.orb_skin_id = orb_skin_id
        self.voice_id_jp = voice_id_jp
        self.voice_id_na = voice_id_na
        self.linked_monster_id = linked_monster_id
        self.tstamp = tstamp

    def _non_auto_update_cols(self):
        return [
            'buy_mp',
            'reg_date',
            'series_id',
            'pal_egg',
            'rem_egg',
            'has_animation',
            'has_hqimage',
        ]

    def __str__(self):
        return 'Monster({}): {}'.format(self.key_value(), self.name_na)


class MonsterWithSeries(SimpleSqlItem):
    """Monster helper for inserting series."""
    TABLE = 'monsters'
    KEY_COL = 'monster_id'

    def __init__(self,
                 monster_id: int = None,
                 series_id: int = None,
                 tstamp: int = None):
        self.monster_id = monster_id
        self.series_id = series_id
        self.tstamp = tstamp

    def __str__(self):
        return 'Monster({}): {}'.format(self.key_value(), self.series_id)


class MonsterWithExtraImageInfo(SimpleSqlItem):
    """Monster helper for updating the image-related info."""
    TABLE = 'monsters'
    KEY_COL = 'monster_id'

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
    TABLE = 'monsters'
    KEY_COL = 'monster_id'

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
    TABLE = 'active_skills'
    KEY_COL = 'active_skill_id'

    @staticmethod
    def from_css(css: CrossServerSkill) -> 'ActiveSkill':
        jp_skill = css.jp_skill
        na_skill = css.na_skill
        kr_skill = css.kr_skill

        jp_as_converter = JpASTextConverter()
        jp_description = jp_skill.full_text(jp_as_converter)

        en_as_converter = EnASTextConverter()
        na_description = jp_skill.full_text(en_as_converter)

        skill_type_tags = skill_text_typing.parse_as_conditions(css)
        tags = skill_text_typing.format_conditions(skill_type_tags)

        # In the event that we don't have KR data, use the NA name and calculated description.
        kr_name = kr_skill.name if jp_skill != kr_skill else na_skill.name
        kr_desc = kr_skill.raw_description if jp_skill != kr_skill else na_description

        return ActiveSkill(
            active_skill_id=jp_skill.skill_id,
            name_jp=jp_skill.name,
            name_na=na_skill.name,
            name_kr=kr_name,
            desc_jp=jp_description,
            desc_na=na_description,
            desc_kr=kr_desc,
            turn_max=jp_skill.turn_max,
            turn_min=jp_skill.turn_min,
            tags=tags)

    def __init__(self,
                 active_skill_id: int = None,
                 name_jp: str = None,
                 name_na: str = None,
                 name_kr: str = None,
                 desc_jp: str = None,
                 desc_na: str = None,
                 desc_kr: str = None,
                 turn_max: int = None,
                 turn_min: int = None,
                 tags: str = None,
                 tstamp: int = None):
        self.active_skill_id = active_skill_id
        self.name_jp = name_jp
        self.name_na = name_na
        self.name_kr = name_kr
        self.desc_jp = desc_jp
        self.desc_na = desc_na
        self.desc_kr = desc_kr
        self.turn_max = turn_max
        self.turn_min = turn_min
        self.tags = tags
        self.tstamp = tstamp

    def __str__(self):
        return 'Active({}): {} -> {}'.format(self.key_value(), self.name_na, self.desc_na)


class LeaderSkill(SimpleSqlItem):
    """Monster leader skill."""
    TABLE = 'leader_skills'
    KEY_COL = 'leader_skill_id'

    @staticmethod
    def from_css(css: CrossServerSkill) -> 'LeaderSkill':
        jp_skill = css.jp_skill
        na_skill = css.na_skill
        kr_skill = css.kr_skill

        en_ls_converter = EnLSTextConverter()
        jp_ls_converter = JpLSTextConverter()
        na_description = jp_skill.full_text(en_ls_converter) or na_skill.raw_description
        jp_description = jp_skill.full_text(jp_ls_converter) or jp_skill.raw_description
        skill_type_tags = skill_text_typing.parse_ls_conditions(css)
        tags = skill_text_typing.format_conditions(skill_type_tags)

        # In the event that we don't have KR data, use the NA name and calculated description.
        kr_name = kr_skill.name if jp_skill != kr_skill else na_skill.name
        kr_desc = kr_skill.raw_description if jp_skill != kr_skill else na_description

        return LeaderSkill(
            leader_skill_id=jp_skill.skill_id,
            name_jp=jp_skill.name,
            name_na=na_skill.name,
            name_kr=kr_name,
            desc_jp=jp_description,
            desc_na=na_description,
            desc_kr=kr_desc,
            max_hp=jp_skill.hp,
            max_atk=jp_skill.atk,
            max_rcv=jp_skill.rcv,
            max_shield=jp_skill.shield,
            tags=tags)

    def __init__(self,
                 leader_skill_id: int = None,
                 name_jp: str = None,
                 name_na: str = None,
                 name_kr: str = None,
                 desc_jp: str = None,
                 desc_na: str = None,
                 desc_kr: str = None,
                 max_hp: float = None,
                 max_atk: float = None,
                 max_rcv: float = None,
                 max_shield: float = None,
                 tags: str = None,
                 tstamp: int = None):
        self.leader_skill_id = leader_skill_id
        self.name_jp = name_jp
        self.name_na = name_na
        self.name_kr = name_kr
        self.desc_jp = desc_jp
        self.desc_na = desc_na
        self.desc_kr = desc_kr
        self.max_hp = max_hp
        self.max_atk = max_atk
        self.max_rcv = max_rcv
        self.max_shield = max_shield
        self.tags = tags
        self.tstamp = tstamp

    def __str__(self):
        return 'Leader ({}): {} -> {}'.format(self.key_value(), self.name_na, self.desc_na)


class Awakening(SimpleSqlItem):
    """Monster awakening entry."""
    TABLE = 'awakenings'
    KEY_COL = 'awakening_id'

    @staticmethod
    def from_csm(o: CrossServerCard) -> List['Awakening']:
        awakenings = [(a_id, False) for a_id in o.jp_card.card.awakenings]
        awakenings.extend([(sa_id, True) for sa_id in o.jp_card.card.super_awakenings])
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
        SELECT awakening_id FROM awakenings
        WHERE monster_id = {monster_id} and order_idx = {order_idx}
        """.format(**sql_item._object_to_sql_params(self))
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
    TABLE = 'evolutions'
    KEY_COL = 'evolution_id'

    @staticmethod
    def from_csm(o: CrossServerCard, ancestor: CrossServerCard) -> Optional['Evolution']:
        card = o.jp_card.card

        def convert(x: MonsterNo) -> MonsterId:
            return o.jp_card.no_to_id(x)

        def safe_convert(x: MonsterNo) -> MonsterId:
            return convert(x) if x else None

        reversible = False
        if card.is_ult and card.un_evo_mat_1 > 0:
            reversible = True
        elif 49 in card.awakenings:
            reversible = True

        if not ancestor.jp_card.card.ancestor_id:
            evolution_type = EvolutionType.evo.value  # Evo
        elif reversible:
            evolution_type = EvolutionType.reversible.value  # Ult/Awoken/Assist
        else:
            evolution_type = EvolutionType.non_reversible.value  # Reincarn/SuperReincarn

        return Evolution(
            evolution_id=None,  # Key that is looked up or inserted
            evolution_type=evolution_type,
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
