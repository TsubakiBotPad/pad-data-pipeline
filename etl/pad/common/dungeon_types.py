from enum import Enum

class RawDungeonType(Enum):
    NORMAL = 1
    SPECIAL = 2
    TECHNICAL = 3
    GIFT = 4
    TOURNAMENT = 5
    SPECIAL_DESCENDED = 6
    MULTIPLAYER = 7

class RawRepeatDay(Enum):
    NONE = 0 # Doesn't repeat
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    WEEKEND = 8

