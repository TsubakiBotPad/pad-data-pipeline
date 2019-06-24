from datetime import date
from typing import List, Optional

from pad.common.shared_types import Server, MonsterId, MonsterNo
from pad.db.sql_item import SimpleSqlItem, ExistsStrategy
from pad.raw_processor.crossed_data import CrossServerSkill, CrossServerCard


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

        # TODO: fodder_exp and sell_gold

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
                 fodder_exp=0,
                 sell_gold=0,
                 sell_mp=jp_card.sell_mp,
                 buy_mp=None,
                 reg_date=date.today().isoformat(),
                 on_jp=o.jp_card.server == Server.JP and jp_card.released_status,
                 on_na=o.na_card.server == Server.NA and na_card.released_status,
                 on_kr=o.kr_card.server == Server.KR and kr_card.released_status,
                 pal_egg=False,
                 rem_egg=False,
                 series_id=None)

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
                 limit_mult: float = None,
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
        self.tstamp = tstamp

        def _non_auto_update_cols(self):
            return [
                'buy_mp',
                'reg_date',
                'series_id',
                'pal_egg',
                'rem_egg',
            ]


class ActiveSkill(SimpleSqlItem):
    """Monster active skill."""
    TABLE = 'active_skills'
    KEY_COL = 'active_skill_id'

    @staticmethod
    def from_css(o: CrossServerSkill) -> 'ActiveSkill':
        return ActiveSkill(
            active_skill_id=o.skill_id,
            name_jp=o.jp_skill.name,
            name_na=o.na_skill.name,
            name_kr=o.kr_skill.name,
            desc_jp=o.jp_skill.description,
            desc_na=o.na_skill.description,
            desc_kr=o.kr_skill.description,
            turn_max=o.jp_skill.turn_max,
            turn_min=o.jp_skill.turn_min)

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
        self.tstamp = tstamp


class LeaderSkill(SimpleSqlItem):
    """Monster leader skill."""
    TABLE = 'leader_skills'
    KEY_COL = 'leader_skill_id'

    @staticmethod
    def from_css(o: CrossServerSkill) -> 'LeaderSkill':
        return LeaderSkill(
            leader_skill_id=o.skill_id,
            name_jp=o.jp_skill.name,
            name_na=o.na_skill.name,
            name_kr=o.kr_skill.name,
            desc_jp=o.jp_skill.description,
            desc_na=o.na_skill.description,
            desc_kr=o.kr_skill.description,
            max_hp=1,
            max_atk=1,
            max_rcv=1,
            max_shield=0)

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
        self.tstamp = tstamp


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
                awakening_id=None, # Key that is looked up or inserted
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

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]

class Evolution(SimpleSqlItem):
    """Monster evolution entry."""
    TABLE = 'evolutions'
    KEY_COL = 'evolution_id'

    @staticmethod
    def from_csm(o: CrossServerCard) -> Optional['Evolution']:
        card = o.jp_card.card
        if not card.ancestor_id:
            return None

        def convert(x: MonsterNo) -> MonsterId:
            return o.jp_card.no_to_id(x)

        return Evolution(
            evolution_id=None, # Key that is looked up or inserted
            evolution_type=0, # Fix
            from_id=convert(card.ancestor_id),
            to_id=convert(card.monster_no),
            mat_1_id=convert(card.evo_mat_id_1) if card.evo_mat_id_1 else None,
            mat_2_id=convert(card.evo_mat_id_2) if card.evo_mat_id_2 else None,
            mat_3_id=convert(card.evo_mat_id_3) if card.evo_mat_id_3 else None,
            mat_4_id=convert(card.evo_mat_id_4) if card.evo_mat_id_4 else None,
            mat_5_id=convert(card.evo_mat_id_5) if card.evo_mat_id_5 else None)

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
