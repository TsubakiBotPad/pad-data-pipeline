import math
from enum import Enum
from typing import NewType, Dict, Any, List

# Raw data types
AttrId = NewType('AttrId', int)
MonsterNo = NewType('MonsterNo', int)
DungeonId = NewType('DungeonId', int)
SubDungeonId = NewType('SubDungeonId', int)
SkillId = NewType('SkillId', int)
TypeId = NewType('TypeId', int)

# DadGuide internal types
MonsterId = NewType('MonsterId', int)

# General purpose types
JsonType = Dict[str, Any]
ListJsonType = List[Dict[str, Any]]


class Printable(object):
    """Simple way to make an object printable."""

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, dump_helper(self))

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


class Server(Enum):
    jp = 0
    na = 1
    kr = 2


class StarterGroup(Enum):
    red = 'red'
    blue = 'blue'
    green = 'green'


class EvolutionType(Enum):
    evo = 1
    reversible = 2
    non_reversible = 3


def dump_helper(x):
    if callable(x):
        return 'fn_obj'
    elif isinstance(x, Enum):
        return str(x)
    elif hasattr(x, '__dict__'):
        return vars(x)
    else:
        return repr(x)
