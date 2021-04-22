"""
Parses limited time event data.

Data files can be different depending on the account; all 3 starters need to be parsed and then deduped against
each other to get the full list.
"""

import time
from typing import Dict, List, Optional, Union
from enum import Enum

from pad.common import pad_util
from pad.common.pad_util import ghmult_plain, ghchance_plain, Printable
from pad.common.shared_types import DungeonId, SubDungeonId, Server, StarterGroup

# The typical JSON file name for this data.
FILE_NAME = 'download_limited_bonus_data_{}.json'


class BonusType(Enum):
    unknown = 0
    exp_boost = 1
    coin_boost = 2
    drop_boost = 3
    stamina_reduction = 5
    dungeon = 6
    pem_event = 8
    rem_event = 9
    pem_cost = 10
    feed_xp_bonus_chance = 11
    plus_drop_rate_1 = 12
    unknown_13 = 13
    unknown_14 = 14
    send_egg_roll = 15
    plus_drop_rate_2 = 16
    feed_skillup_bonus_chance = 17
    tournament_active = 20
    tournament_closed = 21
    score_announcement = 22
    pad_metadata = 23
    gift_dungeon_with_reward = 24
    dungeon_special_event = 25
    multiplayer_announcement = 29
    multiplayer_dungeon_text = 31
    tournament_text = 32
    pad_metadata_2 = 33
    daily_dragons = 36
    monthly_quest_dungeon = 37
    exchange_text = 38
    dungeon_floor_text = 39
    unknown_40 = 40
    normal_announcement = 41
    technical_announcement = 42
    dungeon_web_info_link = 43
    stone_purchase_text = 44
    story_category_text = 47
    special_dungeon_info_link = 50
    dungeon_unavailable_popup = 52


class BonusTypeEntry(object):
    def __init__(self, bonus_type: BonusType, mod_fn=None):
        self.bonus_type = bonus_type
        self.mod_fn = mod_fn

    def __str__(self):
        return 'BonusType({}-{})'.format(self.bonus_type.value, self.bonus_type.name)


UNKNOWN_TYPE = BonusTypeEntry(BonusType.unknown)

ALL_TYPES = [
    # EXP multiplier.
    BonusTypeEntry(BonusType.exp_boost, ghmult_plain),
    # Coin multiplier.
    BonusTypeEntry(BonusType.coin_boost, ghmult_plain),
    # Drop rate increased.
    BonusTypeEntry(BonusType.drop_boost, ghmult_plain),
    # Stamina reduced.
    BonusTypeEntry(BonusType.stamina_reduction, ghmult_plain),
    # Special/co-op dungeon list.
    BonusTypeEntry(BonusType.dungeon),
    # PEM text.
    BonusTypeEntry(BonusType.pem_event),
    # REM text.
    BonusTypeEntry(BonusType.rem_event),
    # Current PEM pal point cost.
    BonusTypeEntry(BonusType.pem_cost, int),
    # Feed XP modifier.
    BonusTypeEntry(BonusType.feed_xp_bonus_chance, ghmult_plain),
    # Increased plus rate 1?
    BonusTypeEntry(BonusType.plus_drop_rate_1, ghchance_plain),
    # Unknown, no text, only value of 10K, multi-day event 
    BonusTypeEntry(BonusType.unknown_13),
    BonusTypeEntry(BonusType.unknown_14),
    # Send a Premium Egg Machine to a Friend and you will get one too!
    BonusTypeEntry(BonusType.send_egg_roll),
    # Increased plus rate 2?
    BonusTypeEntry(BonusType.plus_drop_rate_2, ghmult_plain),
    # Increased skillup chance
    BonusTypeEntry(BonusType.feed_skillup_bonus_chance, ghmult_plain),
    # ?
    BonusTypeEntry(BonusType.tournament_active),
    # "tourney is over, results pending"?
    BonusTypeEntry(BonusType.tournament_closed),
    # ?
    BonusTypeEntry(BonusType.score_announcement),
    # 'mr=10,mc=10,mt=180,frui=2,alrt=15,mrtr=15'
    BonusTypeEntry(BonusType.pad_metadata),
    # Gift dungeon with special text?
    # e.g. Mysterious Visitors dungeon with [+297] will be added to + Points message
    # Has a huge timestamp range, so reward probably
    BonusTypeEntry(BonusType.gift_dungeon_with_reward),
    # Seems to contain random text in the comment
    BonusTypeEntry(BonusType.dungeon_special_event),
    # Limited Time Dungeon arrives! (on multiplayer mode button)
    BonusTypeEntry(BonusType.multiplayer_announcement),
    # Multiplayer dungeon announcement?
    # TAMADRA Invades in Multiplayer Evo Rush!?
    BonusTypeEntry(BonusType.multiplayer_dungeon_text),
    # Tournament dungeon announcement?
    # Rank into the top 30% to get a Dragonbound, Rikuu
    BonusTypeEntry(BonusType.tournament_text),
    # '|22'
    BonusTypeEntry(BonusType.pad_metadata_2),
    # Daily XP dragon
    BonusTypeEntry(BonusType.daily_dragons),
    # ?
    BonusTypeEntry(BonusType.monthly_quest_dungeon),
    #  White Rose Wedding Dress Available!
    BonusTypeEntry(BonusType.exchange_text),
    # Reward: Jewel of Creation
    # Latent TAMADRA (Skill Delay Resist.) invades guaranteed!
    BonusTypeEntry(BonusType.dungeon_floor_text),
    # Some kind of flag, message is '|23'
    BonusTypeEntry(BonusType.unknown_40),
    # Text above the normal dungeon icon in the Dungeon menu
    BonusTypeEntry(BonusType.normal_announcement),
    # Text above the technical dungeon icon in the Dungeon menu
    BonusTypeEntry(BonusType.technical_announcement),
    # https://bit.ly/2zWWGPd - #Q#6th Year Anniversary Quest 1
    BonusTypeEntry(BonusType.dungeon_web_info_link),
    # !June Bride bundles available!
    BonusTypeEntry(BonusType.stone_purchase_text),
    # ソニア編登 - appears above the story dungeon card
    BonusTypeEntry(BonusType.story_category_text),
    # An infobox that links to a webpage appears at the top of the special dungeons
    BonusTypeEntry(BonusType.special_dungeon_info_link),
    # An infobox that links to a webpage appears at the top of the special dungeons
    BonusTypeEntry(BonusType.dungeon_unavailable_popup),
    # An popup that says a dungeon is currently unavailable.  Used when JP 8p was 
]

TYPES_MAP = {bte.bonus_type.value: bte for bte in ALL_TYPES}


class Bonus(Printable):
    """Basically any type of modifier text shown in a menu."""

    keys = 'sebiadmf'

    def __init__(self, raw: Dict[str, str], server: Server):
        if not set(raw) <= set(Bonus.keys):
            raise ValueError('Unexpected keys: ' + str(set(raw) - set(Bonus.keys)))

        # Start time as gungho time string
        self.start_time_str = str(raw['s'])
        self.start_timestamp = pad_util.gh_to_timestamp_2(self.start_time_str, server)

        # End time as gungho time string
        self.end_time_str = str(raw['e'])
        self.end_timestamp = pad_util.gh_to_timestamp_2(self.end_time_str, server)

        # Optional DungeonId
        self.dungeon_id = None  # type: Optional[DungeonId]
        if 'd' in raw:
            self.dungeon_id = DungeonId(int(raw['d']))

        # Optional DungeonFloorId
        # Stuff like rewards text in monthly quests
        self.sub_dungeon_id = None  # type: Optional[SubDungeonId]
        if 'f' in raw:
            self.sub_dungeon_id = SubDungeonId(int(raw['f']))

        # If REM/PEM, the ID of the machine
        self.egg_machine_id = None  # type: Optional[int]
        if 'i' in raw:
            self.egg_machine_id = int(raw['i'])

        # Optional human-readable message (with formatting)
        self.message = None  # type: Optional[str]
        # Optional human-readable message (no formatting)
        self.clean_message = None  # type: Optional[str]
        if 'm' in raw:
            self.message = str(raw['m'])
            self.clean_message = pad_util.strip_colors(self.message)

        bonus_id = int(raw['b'])
        self.bonus_info = TYPES_MAP.get(bonus_id, UNKNOWN_TYPE)

        # Bonus value, if provided, optionally processed
        self.bonus_value = None  # type: Optional[Union[float, int]]
        if 'a' in raw:
            self.bonus_value = raw['a']
            if self.bonus_info.mod_fn:
                self.bonus_value = self.bonus_info.mod_fn(self.bonus_value)

        # Human readable name for the bonus
        self.bonus_name = self.bonus_info.bonus_type.name
        if self.bonus_info.bonus_type == BonusType.unknown:
            self.bonus_name += '({})'.format(bonus_id)
        self.bonus_id = bonus_id

        self.raw = raw

    def is_open(self):
        current_time = int(time.time())
        return self.start_timestamp < current_time < self.end_timestamp

    def __str__(self):
        return 'Bonus({} - {} - {}/{})'.format(self.bonus_name,
                                               self.clean_message,
                                               self.dungeon_id,
                                               self.sub_dungeon_id)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def load_bonus_data(data_dir: str = None,
                    data_group: StarterGroup = None,
                    server: Server = None,
                    json_file: str = None) -> List[Bonus]:
    """Load Bonus objects from the PAD json file."""
    group_file_name = FILE_NAME.format(data_group)
    data_json = pad_util.load_raw_json(data_dir, json_file, group_file_name)
    return [Bonus(item, server) for item in data_json['bonuses']]
