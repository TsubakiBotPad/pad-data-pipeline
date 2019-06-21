import math
from enum import Enum
from typing import NewType, Dict, Any

# Raw data types
AttrId = NewType('AttrId', int)
CardId = NewType('CardId', int)
DungeonId = NewType('DungeonId', int)
DungeonFloorId = NewType('DungeonFloorId', int)
SkillId = NewType('SkillId', int)
TypeId = NewType('TypeId', int)

# DadGuide internal types
MonsterNo = NewType('MonsterNo', int)

# General purpose types
JsonType = Dict[str, Any]


class Printable(object):
    """Simple way to make an object printable."""

    def __repr__(self):
        return '%s(%s)'.format(self.__class__.__name__, self.__dict__)

    def __str__(self):
        return self.__repr__()


class Curve(Printable):
    """Describes how to scale according to level 1-10."""

    def __init__(self,
                 min_value: int,
                 max_value: int = None,
                 scale: float = 1.0,
                 max_level: int = 10):
        self.min_value = min_value
        self.max_value = max_value or min_value * max_level
        self.scale = scale
        self.max_level = max(max_level, 1)

    def value_at(self, level: int):
        f = 1 if self.max_level == 1 else ((level - 1) / (self.max_level - 1))
        return self.min_value + (self.max_value - self.min_value) * math.pow(f, self.scale)


def curve_value(min_val, max_val, scale, level, max_level):
    return Curve(min_val, max_val, scale).value_at(level, max_level)


class Server(Enum):
    JP = 'jp'
    NA = 'na'
    KR = 'kr'


class StarterGroup(Enum):
    RED = 'red'
    BLUE = 'blue'
    GREEN = 'green'
