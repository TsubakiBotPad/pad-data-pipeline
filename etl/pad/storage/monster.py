from datetime import date
from typing import List, Optional

from pad.common.shared_types import MonsterId, MonsterNo, Server
from pad.common.utils import format_int_list
from pad.db.sql_item import SimpleSqlItem
from pad.raw_processor.crossed_data import CrossServerCard
from pad.storage_processor.shared_storage import ServerDependentSqlItem


class Monster(ServerDependentSqlItem):
    """Monster data."""
    KEY_COL = 'monster_id'
    BASE_TABLE = 'monsters'

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
        voice_id_jp = cur_card.voice_id or None if o.jp_card.server == Server.jp else None
        voice_id_na = cur_card.voice_id or None if o.na_card.server == Server.na else None
        orb_skin_id = cur_card.orb_skin_id or None
        bgm_id = cur_card.bgm_set_id or None
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

        diff_stats = diff_possible and (jp_card.max_hp != na_card.max_hp or  # This whole block is only
                                        jp_card.max_atk != na_card.max_atk or  # applicable when dealing with
                                        jp_card.max_rcv != na_card.max_rcv or  # JP cards.  Ignore when building
                                        jp_card.max_level != na_card.max_level or  # a NA database.
                                        jp_card.limit_mult != na_card.limit_mult)
        diff_awakenings = diff_possible and (jp_card.awakenings != na_card.awakenings or
                                             jp_card.super_awakenings != na_card.super_awakenings)
        diff_leader_skill = diff_possible and (extract_skill_data(o.jp_card.leader_skill) !=
                                               extract_skill_data(o.na_card.leader_skill))
        diff_active_skill = diff_possible and (extract_skill_data(o.jp_card.active_skill) !=
                                               extract_skill_data(o.na_card.active_skill))

        return Monster(
            monster_id=o.monster_id,
            monster_no_jp=jp_card.monster_no if on_jp else None,
            monster_no_na=na_card.monster_no if on_na else None,
            monster_no_kr=kr_card.monster_no if on_kr else None,
            gungho_id_jp=jp_card.gungho_id if on_jp else None,
            gungho_id_na=na_card.gungho_id if on_na else None,
            gungho_id_kr=kr_card.gungho_id if on_kr else None,
            name_ja=jp_card.name,
            name_en=na_card.name,
            name_ko=kr_card.name,
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
            attribute_1_id=cur_card.attr1_id,
            attribute_2_id=none_or(cur_card.attr2_id),
            attribute_3_id=none_or(cur_card.attr3_id),
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
            group_id=cur_card.group_id,
            collab_id=cur_card.collab_id,
            has_animation=o.has_animation,
            has_hqimage=o.has_hqimage,
            voice_id_jp=voice_id_jp,
            voice_id_na=voice_id_na,
            orb_skin_id=orb_skin_id,
            bgm_id=bgm_id,
            latent_slots=latent_slots)

    def __init__(self,
                 monster_id: int = None,
                 monster_no_jp: int = None,
                 monster_no_na: int = None,
                 monster_no_kr: int = None,
                 gungho_id_jp: int = None,
                 gungho_id_na: int = None,
                 gungho_id_kr: int = None,
                 name_ja: str = None,
                 name_en: str = None,
                 name_ko: str = None,
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
                 attribute_3_id: int = None,
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
                 group_id: int = None,
                 collab_id: int = None,
                 has_animation: bool = None,
                 has_hqimage: bool = None,
                 voice_id_jp: int = None,
                 voice_id_na: int = None,
                 orb_skin_id: int = None,
                 bgm_id: int = None,
                 latent_slots: int = None,
                 tstamp: int = None):
        self.monster_id = monster_id
        self.monster_no_jp = monster_no_jp
        self.monster_no_na = monster_no_na
        self.monster_no_kr = monster_no_kr
        self.name_ja = name_ja
        self.name_en = name_en
        self.name_ko = name_ko
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
        self.attribute_3_id = attribute_3_id
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
        self.group_id = group_id
        self.collab_id = collab_id
        self.has_animation = has_animation
        self.has_hqimage = has_hqimage
        self.voice_id_jp = voice_id_jp
        self.voice_id_na = voice_id_na
        self.orb_skin_id = orb_skin_id
        self.bgm_id = bgm_id
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
        return 'Monster({}): {}'.format(self.key_str(), self.name_en)


class MonsterWithExtraImageInfo(ServerDependentSqlItem):
    """Monster helper for updating the image-related info."""
    KEY_COL = 'monster_id'
    BASE_TABLE = 'monsters'

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
        return 'MonsterImage({}): animated={} hq={}'.format(self.key_str(), self.has_animation, self.has_hqimage)


class MonsterWithMPValue(ServerDependentSqlItem):
    """Monster helper for inserting MP purchase."""
    KEY_COL = 'monster_id'
    BASE_TABLE = 'monsters'

    def __init__(self,
                 monster_id: int = None,
                 buy_mp: int = None,
                 tstamp: int = None):
        self.monster_id = monster_id
        self.buy_mp = buy_mp
        self.tstamp = tstamp

    def __str__(self):
        return 'MonsterMP({}): {}'.format(self.key_str(), self.buy_mp)


class LatentTamadra(SimpleSqlItem):
    """Latent tamadra to add monster_id to latent_skills."""
    TABLE = 'latent_skills'
    KEY_COL = 'latent_skill_id'

    @staticmethod
    def from_csm(o: CrossServerCard):
        return LatentTamadra(latent_skill_id=o.cur_card.card.latent_on_feed,
                             monster_id=o.monster_id)

    def __init__(self,
                 latent_skill_id: int = None,
                 monster_id: int = None,
                 tstamp: int = None):
        self.latent_skill_id = latent_skill_id
        self.monster_id = monster_id
        self.tstamp = tstamp

    def __str__(self):
        return 'LatentTamadra({}): {}'.format(self.key_str(), self.monster_id)


class Awakening(ServerDependentSqlItem):
    """Monster awakening entry."""
    KEY_COL = {'monster_id', 'order_idx'}
    BASE_TABLE = 'awakenings'

    @staticmethod
    def from_csm(o: CrossServerCard) -> List['Awakening']:
        awakenings = [(a_id, False) for a_id in o.cur_card.card.awakenings]
        awakenings.extend([(sa_id, True) for sa_id in o.cur_card.card.super_awakenings])
        results = []
        for i, v in enumerate(awakenings):
            results.append(Awakening(
                monster_id=o.monster_id,
                awoken_skill_id=v[0],
                is_super=v[1],
                order_idx=i))
        return results

    def __init__(self,
                 monster_id: int = None,
                 awoken_skill_id: int = None,
                 is_super: bool = None,
                 order_idx: int = None,
                 tstamp: int = None):
        self.monster_id = monster_id
        self.awoken_skill_id = awoken_skill_id
        self.is_super = is_super
        self.order_idx = order_idx
        self.tstamp = tstamp

    def __str__(self):
        return 'Awakening ({}): {}, super={}'.format(
            self.key_str(), self.awoken_skill_id, self.is_super)


class Evolution(ServerDependentSqlItem):
    """Monster evolution entry."""
    KEY_COL = 'to_id'
    BASE_TABLE = 'evolutions'

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
            evolution_type=0,  # TODO: Eventually remove this.  evolution_type is deprecated and barely works as is
            reversible=reversible,
            from_id=convert(card.ancestor_id),
            to_id=convert(card.gungho_id),
            mat_1_id=safe_convert(card.evo_mat_id_1),
            mat_2_id=safe_convert(card.evo_mat_id_2),
            mat_3_id=safe_convert(card.evo_mat_id_3),
            mat_4_id=safe_convert(card.evo_mat_id_4),
            mat_5_id=safe_convert(card.evo_mat_id_5))

    def __init__(self,
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

    def __str__(self):
        return 'Evo ({}): from={} type={}'.format(self.key_str(), self.from_id, self.evolution_type)


class Transformation(ServerDependentSqlItem):
    """Monster evolution entry."""
    KEY_COL = {'from_monster_id', 'to_monster_id'}
    BASE_TABLE = 'transformations'

    @staticmethod
    def from_csm(o: CrossServerCard, tfid: MonsterNo, numerator: float, denominator: float) \
            -> Optional['Transformation']:
        card = o.cur_card.card

        def convert(x: MonsterNo) -> MonsterId:
            return o.cur_card.no_to_id(x)

        # Do something with the chance
        return Transformation(
            from_monster_id=convert(card.gungho_id),
            to_monster_id=convert(tfid))

    def __init__(self,
                 from_monster_id: MonsterId = None,
                 to_monster_id: MonsterId = None,
                 tstamp: int = None):
        self.from_monster_id = from_monster_id
        self.to_monster_id = to_monster_id
        self.tstamp = tstamp

    def __str__(self):
        return 'Transform ({})'.format(self.key_str())


class AltMonster(ServerDependentSqlItem):
    """Alt. monster data."""
    KEY_COL = 'alt_monster_id'
    BASE_TABLE = 'alt_monsters'

    @staticmethod
    def from_csm(o: CrossServerCard, mid: Optional[int]) -> 'AltMonster':
        return AltMonster(
            alt_monster_id=o.monster_id,
            monster_id=mid,
            active_skill_id=o.cur_card.card.active_skill_id,
            reg_date=date.today().isoformat(),
            is_alt=o.monster_id >= 100_000)

    def __init__(self,
                 alt_monster_id: int = None,
                 monster_id: Optional[int] = None,
                 active_skill_id: int = None,
                 reg_date: str = None,
                 is_alt: bool = None,
                 tstamp: int = None):
        self.alt_monster_id = alt_monster_id
        self.monster_id = monster_id
        self.active_skill_id = active_skill_id
        self.reg_date = reg_date
        self.is_alt = is_alt
        self.tstamp = tstamp

    def _non_auto_update_cols(self):
        return ['reg_date']

    def __str__(self):
        return 'AltMonster({}) - {}'.format(self.key_str(), self.monster_id)
