from enum import Enum, auto
from typing import Dict, List, TYPE_CHECKING, TypeVar

import jinja2

if TYPE_CHECKING:
    from pad.raw.skills.active_skill_info import ASTextConverter, ActiveSkill

T = TypeVar('T')


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


class BaseTextConverter:
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

    def process_raw(self, text: str) -> str:
        return jinja2.Template(text).render(
            awoskills={f"id{awid}": name for awid, name in self.AWAKENING_MAP.items()}
        )


# ENUMS
class TargetType(Enum):
    unset = auto()
    # Selective Subs
    random = auto()
    self_leader = auto()
    both_leader = auto()
    friend_leader = auto()
    subs = auto()
    other_subs = auto()
    attrs = auto()
    types = auto()
    card = auto()
    all = auto()

    # Specific Players/Enemies
    player = auto()
    enemy = auto()
    enemy_ally = auto()

    # Full Team Aspect
    awokens = auto()
    actives = auto()


class OrbShape(Enum):
    l_shape = auto()
    cross = auto()
    column = auto()
    row = auto()


class Status(Enum):
    movetime = auto()
    atk = auto()
    hp = auto()
    rcv = auto()


class Unit(Enum):
    unknown = auto()
    seconds = auto()
    percent = auto()
    none = auto()


class Absorb(Enum):
    unknown = auto()
    attr = auto()
    combo = auto()
    damage = auto()


class Source(Enum):
    all_sources = auto()
    attrs = auto()
    types = auto()


class Tag(Enum):
    NO_SKYFALL = auto()
    BOARD_7X6 = auto()
    DISABLE_POISON = auto()
    FIXED_TIME = auto()
    ERASE_P = auto()


def mult(x: int) -> float:
    return x / 100


def multi_floor(x: int) -> float:
    return mult(x) if x != 0 else 1.0


def atk_from_slice(x: List[int]) -> float:
    return mult(x[2]) if 1 in x[:2] else 1.0


def rcv_from_slice(x: List[int]) -> float:
    return mult(x[2]) if 2 in x[:2] else 1.0


def binary_con(x: int) -> List[int]:
    return [] if x == -1 else [i for i, v in enumerate(str(bin(x))[:1:-1]) if v == '1']


def list_binary_con(x: List[int]) -> List[int]:
    return [b for i in x for b in binary_con(i)]


def list_con_pos(x: List[int]) -> List[int]:
    return [i for i in x if i > 0]


def merge_defaults(data: List[T], defaults: List[T]) -> List[T]:
    return list(data) + defaults[len(data):]


class Board:
    DAWNGLARE_CONSTS = "RBGLDHJPMX X8765432Z"

    def __init__(self, data: List[List[int]] = None):
        self.data = data or [[-1 for _ in range(7)] for _ in range(6)]

    def __or__(self, other):
        if not isinstance(other, Board):
            raise TypeError(f"unsupported operand type(s) for |: 'Board' and '{other.__class__.__name__}'")
        return Board([[other.data[i][j] if other.data[i][j] != -1 else self.data[i][j]
                       for j in range(7)] for i in range(6)])

    def __and__(self, other):
        if not isinstance(other, Board):
            raise TypeError(f"unsupported operand type(s) for &: 'Board' and '{other.__class__.__name__}'")
        return Board([[self.data[i][j] if self.data[i][j] == other.data[i][j] else -1
                       for j in range(7)] for i in range(6)])

    def __bool__(self):
        return any(any(v != -1 for v in row) for row in self.data)

    def to_7x6(self):
        return "".join("".join(self.DAWNGLARE_CONSTS[v] for v in row) for row in self.data)

    def to_6x5(self):
        return "".join("".join(self.DAWNGLARE_CONSTS[v] for j, v in enumerate(row) if j != 3)
                       for i, row in enumerate(self.data) if i != 2)


class PartWithTextAndCount:
    def __init__(self, act: "ActiveSkill", text: str):
        self.act = act
        self.text = text
        self.repeat = 1

    def templated_text(self, converter: "ASTextConverter"):
        return self.text if self.repeat == 1 else converter.fmt_repeated(self.text, self.repeat)

    def full_text(self, converter: "ASTextConverter"):
        return converter.process_raw(self.templated_text(converter))
