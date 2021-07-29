from typing import Dict
from enum import Enum


class I13NotImplemented(NotImplementedError):
    pass


def fmt_mult(x):
    return '{:,}'.format(round(float(x), 2)).rstrip('0').rstrip('.')


def multi_getattr(o, *args):
    for a in args:
        v = getattr(o, a, None)
        if v is not None:
            return v
    raise Exception('Attributes not found:' + str(args))


class BaseTextConverter(object):
    """Contains code shared across AS and LS converters."""
    _ATTRS = _TYPES = {}

    #############################################################################
    # Items here must be implemented by language-specific subclasses
    #############################################################################

    @property
    def ATTRIBUTES(self) -> Dict[int, str]:
        raise I13NotImplemented()

    @classmethod
    def attributes_to_str(cls, attributes, concat=None, cf=None):
        if cf is None:
            cf = cls.concat_list_and
        if concat is not None:
            return cf([cls._ATTRS[x] for x in attributes], concat)
        else:
            return cf([cls._ATTRS[x] for x in attributes])

    @property
    def TYPES(self) -> Dict[int, str]:
        raise I13NotImplemented()

    @classmethod
    def typing_to_str(cls, types, conj=None):
        if conj is not None:
            return cls.concat_list_and([cls._TYPES[x] for x in types], conj)
        else:
            return cls.concat_list_and([cls._TYPES[x] for x in types])

    @property
    def AWAKENING_MAP(self) -> Dict[int, str]:
        raise I13NotImplemented()

    def all_stats(self, multiplier):
        raise I13NotImplemented()

    def hp(self):
        raise I13NotImplemented()

    def atk(self):
        raise I13NotImplemented()

    def rcv(self):
        raise I13NotImplemented()

    def reduce_all_pct(self, shield_text):
        raise I13NotImplemented()

    def reduce_attr_pct(self, attr_text, shield_text):
        raise I13NotImplemented()

    @staticmethod
    def concat_list(list_to_concat):
        raise I13NotImplemented()

    @staticmethod
    def concat_list_and(list_to_concat, conj=None):
        raise I13NotImplemented()

    @staticmethod
    def concat_list_semicolons(list_to_concat):
        raise I13NotImplemented()

    ATTRS_EXCEPT_BOMBS = list(range(9))
    ALL_ATTRS = list(range(10))


# ENUMS
class TargetType(Enum):
    unset = -1
    # Selective Subs
    random = 0
    self_leader = 1
    both_leader = 2
    friend_leader = 3
    subs = 4
    attrs = 5
    types = 6
    card = 6.5

    # Specific Players/Enemies
    player = 7
    enemy = 8
    enemy_ally = 9

    # Full Team Aspect
    awokens = 10
    actives = 11


class OrbShape(Enum):
    l_shape = 0
    cross = 1
    column = 2
    row = 4


class Status(Enum):
    movetime = 0
    atk = 1
    hp = 2
    rcv = 3


class Unit(Enum):
    unknown = -1
    seconds = 0
    percent = 1
    none = 2


class Absorb(Enum):
    unknown = -1
    attr = 0
    combo = 1
    damage = 2


class Source(Enum):
    all_sources = 0
    attrs = 5
    types = 6


# LS FUNCTIONS
class ThresholdType(Enum):
    BELOW = '<'
    ABOVE = '>'


class Tag(Enum):
    NO_SKYFALL = 0
    BOARD_7X6 = 1
    DISABLE_POISON = 2
    FIXED_TIME = 3
    ERASE_P = 4


def sort_tags(tags):
    return sorted(tags, key=lambda x: x.value)


class AttributeDict(dict):
    def __getattr__(self, key):
        if key not in self:
            raise AttributeError()
        return self[key]

    __setattr__ = dict.__setitem__


def mult(x):
    return x / 100


def multi_floor(x):
    return mult(x) if x != 0 else 1.0


def atk_from_slice(x):
    return mult(x[2]) if 1 in x[:2] else 1.0


def rcv_from_slice(x):
    return mult(x[2]) if 2 in x[:2] else 1.0


def binary_con(x):
    return [] if x == -1 else [i for i, v in enumerate(str(bin(x))[:1:-1]) if v == '1']


def list_binary_con(x):
    return [b for i in x for b in binary_con(i)]


def list_con_pos(x):
    return [i for i in x if i > 0]


def merge_defaults(data, defaults):
    return list(data) + defaults[len(data):]
