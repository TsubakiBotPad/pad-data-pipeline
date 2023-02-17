"""
Parses card data.
"""
import logging
from typing import List, Any, Optional

from pad.common import pad_util
from pad.common.shared_types import AttrId, MonsterNo, SkillId, TypeId, Curve

human_fix_logger = logging.getLogger('human_fix')

# The typical JSON file name for this data.
FILE_NAME = 'download_card_data.json'


class ESRef(pad_util.Printable):
    """Describes how this monster uses an enemy skill"""

    def __init__(self, enemy_skill_id: int, enemy_ai: int, enemy_rnd: int):
        self.enemy_skill_id = enemy_skill_id
        # This is an additive amount under a specific threshold?
        self.enemy_ai = enemy_ai
        # Seems like this is the base chance for an action
        self.enemy_rnd = enemy_rnd


class Enemy(pad_util.Printable):
    """Describes how this monster spawns as an enemy."""

    def __init__(self,
                 turns: int,
                 hp: Curve,
                 atk: Curve,
                 defense: Curve,
                 max_level: int,
                 coin: Curve,
                 xp: Curve,
                 enemy_skill_refs: List[ESRef]):
        self.turns = turns
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.max_level = max_level
        self.coin = coin
        self.xp = xp
        self.enemy_skill_refs = enemy_skill_refs


class Card(pad_util.Printable):
    """Data about a player-ownable monster."""

    def __init__(self, raw: List):
        _unflatten(raw, 57, 3)
        _unflatten(raw, 58, 1)

        self.monster_no = MonsterNo(raw[0])
        self.name: str = raw[1]
        self.attr_id = AttrId(raw[2])
        self.sub_attr_id = AttrId(raw[3])
        self.is_ult: bool = bool(raw[4])  # True if ultimate, False if normal evo
        self.type_1_id = TypeId(raw[5])
        self.type_2_id = TypeId(raw[6])
        self.rarity: int = raw[7]
        self.cost: int = raw[8]

        # Appears to be related to the size of the monster.
        # If 5, the monster always spawns alone. Needs more research.
        self.unknown_009: int = raw[9]

        self.max_level: int = raw[10]
        self.feed_xp_per_level = raw[11] / 4
        self.released_status = raw[12] == 100
        self.sell_gold_per_level = raw[13] / 10

        self.min_hp: int = raw[14]
        self.max_hp: int = raw[15]
        self.hp_scale = float(raw[16])

        self.min_atk: int = raw[17]
        self.max_atk: int = raw[18]
        self.atk_scale = float(raw[19])

        self.min_rcv: int = raw[20]
        self.max_rcv: int = raw[21]
        self.rcv_scale = float(raw[22])

        self.xp_max: int = raw[23]
        self.xp_scale = float(raw[24])

        self.active_skill_id = SkillId(raw[25])
        self.leader_skill_id = SkillId(raw[26])

        # Enemy turn timer for normal dungeons, and techs where enemy_turns_alt is not populated.
        self.enemy_turns: int = raw[27]

        # Min = lvl 1 and Max = lvl 10
        self.enemy_hp_min: int = raw[28]
        self.enemy_hp_max: int = raw[29]
        self.enemy_hp_scale = float(raw[30])

        self.enemy_atk_min: int = raw[31]
        self.enemy_atk_max: int = raw[32]
        self.enemy_atk_scale = float(raw[33])

        self.enemy_def_min: int = raw[34]
        self.enemy_def_max: int = raw[35]
        self.enemy_def_scale = float(raw[36])

        self.enemy_max_level: int = raw[37]
        self.enemy_coins_per_level = raw[38] / 2
        self.enemy_xp_per_level = raw[39] / 2

        self.ancestor_id = MonsterNo(raw[40])

        self.evo_mat_id_1 = MonsterNo(raw[41])
        self.evo_mat_id_2 = MonsterNo(raw[42])
        self.evo_mat_id_3 = MonsterNo(raw[43])
        self.evo_mat_id_4 = MonsterNo(raw[44])
        self.evo_mat_id_5 = MonsterNo(raw[45])

        self.un_evo_mat_1 = MonsterNo(raw[46])
        self.un_evo_mat_2 = MonsterNo(raw[47])
        self.un_evo_mat_3 = MonsterNo(raw[48])
        self.un_evo_mat_4 = MonsterNo(raw[49])
        self.un_evo_mat_5 = MonsterNo(raw[50])

        # When >0, the enemy turn timer for technical dungeons.
        self.enemy_turns_alt: int = raw[51]

        # Controls whether the monster uses the 'new' AI or the 'old' AI.
        # Monsters using the old  AI only have support up to some limit of ES values.
        # One main difference between is behavior during preempts; old-AI monsters will
        # attack if they cannot execute a preempt, new-AI monsters will skip to the next.
        # (needs verification).
        self.use_new_ai = bool(raw[52])

        # Each monster has an internal counter which starts at raw[53] and is decremented
        # each time a skill activates. If the counter is less than the action cost, it cannot
        # execute.
        #
        # Turn flow follows this order:
        # 1: pick action (possibly checking counter value)
        # 2: increment the counter up, capped at the max value
        # 3: decrement the counter based on the selected action value
        #
        # The starting and maximum value for the enemy skill action counter.
        self.enemy_skill_max_counter: int = raw[53]

        # The amount to increment the counter each turn.
        #
        # The vast majority of these are 0/1.
        # Deus Ex Machina has 2, Kanna has 7.
        self.enemy_skill_counter_increment: int = raw[54]

        # Boolean, unlikely to be anything useful, only populated for 495 (1) and 111 (1000).
        self.unknown_055: int = raw[55]

        # Unused
        self.unknown_056: Any = raw[56]

        self.enemy_skill_refs: List[ESRef] = []
        es_data: List[int] = raw[57]
        for i in range(0, len(es_data) - 2, 3):
            self.enemy_skill_refs.append(ESRef(es_data[i], es_data[i + 1], es_data[i + 2]))

        self.awakenings: List[int] = raw[58]
        self.super_awakenings: List[int] = list(map(int, filter(str.strip, raw[59].split(','))))

        self.base_id = MonsterNo(int(raw[60]))
        self.group_id: int = raw[61]
        self.type_3_id = TypeId(int(raw[62]))

        self.sell_mp: int = raw[63]
        self.latent_on_feed: int = raw[64]
        self.collab_id: int = raw[65]

        # Bitmap with some non-random flag values
        self.flags: int = raw[66]
        self.inheritable_flag = bool(self.flags & 1)
        self.take_assists_flag = bool(self.flags & 2)
        self.is_collab_flag = bool(self.flags & 4)
        self.unstackable_flag = bool(self.flags & 8)
        self.assist_only_flag = bool(self.flags & 16)
        self.latent_slot_unlock_flag = bool(self.flags & 32)

        # Composed with flags and other monster attributes
        self.inheritable = bool(self.inheritable_flag and self.active_skill_id)
        self.take_assists = bool(self.take_assists_flag and self.active_skill_id)
        self.is_stackable = bool(not self.unstackable_flag and self.type_1_id in [0, 12, 14])
        self.ownable = self.monster_no < 100000
        self.usable = bool(not self.assist_only_flag and self.ownable)

        self.search_strings: List[str] = raw[67].split('|')
        self.limit_mult: int = raw[68]

        # 1-indexed media ids
        self.voice_id: int = raw[69]
        self.orb_skin_id: int = raw[70] if raw[70] < 10_000 else 0
        self.bgm_id: int = raw[70] - 10_000 if 10_000 <= raw[70] else 0

        # This is currently unused by GH except for old monster transform values
        self.tags: str = raw[71]

        self.ls_bitflag: int = raw[72] + (raw[73] << 32)

        # This is 0 for all cards except NY cards
        self.unknown_74: int = raw[74]

        # This is 0 for all cards
        self.unknown_75: int = raw[75]

        # Use this for server mismatch
        if len(raw) == 74:
            raw += [0] * 2

        self.other_fields: List = raw[76:]

        if self.other_fields:
            human_fix_logger.error('Unused monster values found.')

    def enemy(self) -> Enemy:
        return Enemy(self.enemy_turns,
                     Curve(self.enemy_hp_min,
                           self.enemy_hp_max,
                           self.enemy_hp_scale,
                           self.enemy_max_level),
                     Curve(self.enemy_atk_min,
                           self.enemy_atk_max,
                           self.enemy_atk_scale,
                           self.enemy_max_level),
                     Curve(self.enemy_def_min,
                           self.enemy_def_max,
                           self.enemy_def_scale,
                           self.enemy_max_level),
                     self.enemy_max_level,
                     Curve(self.enemy_coins_per_level,
                           max_level=self.enemy_max_level),
                     Curve(self.enemy_xp_per_level,
                           max_level=self.enemy_max_level),
                     self.enemy_skill_refs)

    def hp_curve(self) -> Curve:
        return Curve(self.min_hp, self.max_hp, self.hp_scale, max_level=99)

    def atk_curve(self) -> Curve:
        return Curve(self.min_atk, self.max_atk, self.atk_scale, max_level=99)

    def rcv_curve(self) -> Curve:
        return Curve(self.min_rcv, self.max_rcv, self.rcv_scale, max_level=99)

    def xp_curve(self) -> Curve:
        return Curve(0, self.xp_max, self.xp_scale, max_level=99)

    def feed_xp_curve(self) -> Curve:
        return Curve(self.feed_xp_per_level, max_level=99)

    def sell_gold_curve(self) -> Curve:
        return Curve(self.sell_gold_per_level, max_level=99)

    def __str__(self):
        return 'Card({} - {})'.format(self.monster_no, self.name)


def _unflatten(raw: List[Any], idx: int, width: int):
    """Unflatten a card array.

    Index is the slot containing the item count.
    Width is the number of slots per item.
    If replace is true, values are moved into an array at idx.
    If replace is false, values are deleted.
    """
    item_count = raw[idx]
    if item_count == 0:
        raw[idx] = list()
        return

    data_start = idx + 1
    flattened_item_count = width * item_count
    flattened_data_slice = slice(data_start, data_start + flattened_item_count)

    data = list(raw[flattened_data_slice])
    del raw[flattened_data_slice]
    raw[idx] = data


def load_card_data(data_dir: str = None, json_file: str = None) -> List[Card]:
    """Load Card objects from PAD JSON file."""
    data_json = pad_util.load_raw_json(data_dir, json_file, FILE_NAME)
    return [Card(r) for r in data_json['card']]
