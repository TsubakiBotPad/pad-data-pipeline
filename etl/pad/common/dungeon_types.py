from enum import Enum

class RawDungeonType(Enum):
    NORMAL = 0
    SPECIAL = 1
    TECHNICAL = 2
    GIFT = 3
    RANKING = 4
    DEPRECATED = 5 # Not entirely sure of this one but seems like a safe bet
    SPECIAL_DESCENDED = 6
    MULTIPLAYER_2 = 7

class RawRepeatDay(Enum):
    NONE = 0 # Doesn't repeat
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    WEEKEND = 8

