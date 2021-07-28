from typing import Dict, List
from enum import Enum

__all__ = []


def public(x):
    global __all__
    __all__.append(x.__name__)
    return x


@public
class I13NotImplemented(NotImplementedError):
    pass


@public
def fmt_mult(x):
    return '{:,}'.format(round(float(x), 2)).rstrip('0').rstrip('.')


@public
def multi_getattr(o, *args):
    for a in args:
        v = getattr(o, a, None)
        if v is not None:
            return v
    raise Exception('Attributs not found:' + str(args))


@public
def minmax(nmin, nmax, p=False, fmt=False):
    fmt = fmt_mult if fmt else (lambda x: '{:,}'.format(x))
    if None in [nmin, nmax] or nmin == nmax:
        return "{}".format(fmt(nmin or nmax)) + ("%" if p else '')
    elif p:
        return "{}%~{}%".format(fmt(int(nmin)), fmt(int(nmax)))
    else:
        return "{}~{}".format(fmt(int(nmin)), fmt(int(nmax)))


@public
class BaseTextConverter(object):
    """Contains code shared across AS and LS converters."""

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
@public
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


@public
class OrbShape(Enum):
    l_shape = 0
    cross = 1
    column = 2
    row = 4


@public
class Status(Enum):
    movetime = 0
    atk = 1
    hp = 2
    rcv = 3


@public
class Unit(Enum):
    unknown = -1
    seconds = 0
    percent = 1
    none = 2


@public
class Absorb(Enum):
    unknown = -1
    attr = 0
    combo = 1
    damage = 2


@public
class Source(Enum):
    all_sources = 0
    attrs = 5
    types = 6


# LS FUNCTIONS
@public
class ThresholdType(Enum):
    BELOW = '<'
    ABOVE = '>'


@public
class Tag(Enum):
    NO_SKYFALL = 0
    BOARD_7X6 = 1
    DISABLE_POISON = 2
    FIXED_TIME = 3
    ERASE_P = 4


@public
def sort_tags(tags):
    return sorted(tags, key=lambda x: x.value)


@public
class AttributeDict(dict):
    def __getattr__(self, key):
        if key not in self:
            raise AttributeError()
        return self[key]

    __setattr__ = dict.__setitem__


@public
def mult(x):
    return x / 100


@public
def multi_floor(x):
    return x / 100 if x != 0 else 1.0


# TODO: clean all these things up
@public
def atk_from_slice(x):
    return x[2] / 100 if 1 in x[:2] else 1.0


@public
def rcv_from_slice(x):
    return x[2] / 100 if 2 in x[:2] else 1.0


@public
def binary_con(x):
    return [i for i, v in enumerate(str(bin(x))[:1:-1]) if v == '1']


@public
def list_binary_con(x):
    return [b for i in x for b in binary_con(i)]


@public
def list_con_pos(x):
    return [i for i in x if i > 0]


@public
def merge_defaults(input, defaults):
    return list(input) + defaults[len(input):]
