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
    return str(round(float(x), 2)).rstrip('0').rstrip('.')


@public
def multi_getattr(o, *args):
    for a in args:
        v = getattr(o, a, None)
        if v is not None:
            return v
    raise Exception('Attributs not found:' + str(args))

@public 
def minmax(nmin, nmax, p = False, fmt = False):
    fmt = fmt_mult if fmt else (lambda x: x)
    if None in [nmin, nmax] or nmin == nmax:
        return str(fmt(nmin or nmax))+("%" if p else '')
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

    def attributes_to_str(self, attributes):
        return self.concat_list_and([self.ATTRIBUTES[x] for x in attributes])

    @property
    def TYPES(self) -> Dict[int, str]:
        raise I13NotImplemented()

    def typing_to_str(self, types):
        return self.concat_list_and([self.TYPES[x] for x in types])

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
    def concat_list_and(list_to_concat, conj):
        raise I13NotImplemented()

    @staticmethod
    def concat_list_semicolons(list_to_concat):
        raise I13NotImplemented()

    ATTRS_EXCEPT_BOMBS = list(range(9))
    ALL_ATTRS = list(range(10))

    #############################################################################
    # Everything below here are common helpers
    #############################################################################

    def attributes_format(self, attributes: List[int], sep: str = ', ') -> str:
        return sep.join([self.ATTRIBUTES[i] for i in attributes])

    def types_format(self, types: List[int]) -> str:
        return ', '.join([self.TYPES[i] for i in types])

    def fmt_stats_type_attr_bonus(self, ls,
                                  reduce_join_txt='; ',
                                  skip_attr_all=True,
                                  atk=None,
                                  rcv=None):
        types = getattr(ls, 'types', [])
        attributes = getattr(ls, 'attributes', [])
        hp_mult = getattr(ls, 'hp', 1)
        # TODO: maybe we can just move min_atk and min_rcv in here
        # TODO: had to add all these getattr because this is being used in the active
        #       skill parser as well, is this right?
        atk_mult = atk or getattr(ls, 'atk', 1)
        rcv_mult = rcv or getattr(ls, 'rcv', 1)
        damage_reduct = getattr(ls, 'shield', 0)
        reduct_att = getattr(ls, 'reduction_attributes', [])
        skill_text = ''

        multiplier_text = self.fmt_multiplier_text(hp_mult, atk_mult, rcv_mult)
        if multiplier_text:
            skill_text += multiplier_text

            for_skill_text = ''
            if types:
                for_skill_text += ' {} type'.format(self.types_format(types))

            is_attr_all = len(attributes) in [0, 5]
            should_skip_attr = is_attr_all and skip_attr_all

            if attributes and not should_skip_attr:
                if for_skill_text:
                    for_skill_text += ' and'
                color_text = 'all' if len(attributes) == 5 else self.attributes_format(attributes)
                for_skill_text += ' ' + color_text + ' Att.'

            if for_skill_text:
                skill_text += ' for' + for_skill_text

        reduct_text = self.fmt_reduct_text(damage_reduct, reduct_att)
        if reduct_text:
            if multiplier_text:
                skill_text += reduce_join_txt
            if not skill_text or ';' in reduce_join_txt:
                reduct_text = reduct_text.capitalize()
            skill_text += reduct_text

        return skill_text

    def fmt_multi_attr(self, attributes, conj='or'):
        prefix = ''
        if 1 <= len(attributes) <= 7:
            attr_list = [self.ATTRIBUTES[i] for i in attributes]
        elif 7 <= len(attributes) < 10:
            # TODO: this is kind of weird maybe needs fixing
            # All the attributes except the duplicate 'None' for fire, random, locked bomb, etc
            non_attrs = [x for x in self.ATTRIBUTES.keys() if x is not None and x >= 0]
            attrs = list(set(non_attrs) - set(attributes))
            att_sym_diff = sorted(attrs, key=lambda x: self.ATTRIBUTES[x])
            attr_list = [self.ATTRIBUTES[i] for i in att_sym_diff]
            prefix = 'non '
        else:
            return '' if conj == 'or' else ' all'

        return prefix + self.concat_list_and(attr_list, conj)

    def fmt_multiplier_text(self, hp_mult, atk_mult, rcv_mult):
        if hp_mult == atk_mult and atk_mult == rcv_mult:
            if hp_mult == 1:
                return None
            return self.all_stats(fmt_mult(hp_mult))

        mults = [(self.hp(), hp_mult), (self.atk(), atk_mult), (self.rcv(), rcv_mult)]
        mults = list(filter(lambda x: x[1] != 1, mults))
        mults.sort(key=lambda x: x[1], reverse=True)

        chunks = []
        x = 0
        while x < len(mults):
            can_check_double = x + 1 < len(mults)
            if can_check_double and mults[x][1] == mults[x + 1][1]:
                chunks.append(('{} & {}'.format(mults[x][0], mults[x + 1][0]), mults[x][1]))
                x += 2
            else:
                chunks.append((mults[x][0], mults[x][1]))
                x += 1

        output = ''
        for c in chunks:
            if len(output):
                output += ' and '
            output += '{}x {}'.format(fmt_mult(c[1]), c[0])

        return output

    def fmt_reduct_text(self, shield, reduct_att=None):
        if shield == 0:
            return None
        shield_text = fmt_mult(shield * 100)
        if reduct_att in [None, [], [0, 1, 2, 3, 4]]:
            return self.reduce_all_pct(shield_text)
        else:
            color_text = self.attributes_format(reduct_att)
            return self.reduce_attr_pct(color_text, shield_text)

    def attributes_to_str(self, attributes: List[int], concat=None) -> str:
        concatf = concat or self.concat_list_and
        if isinstance(concat, str):
            concatf = lambda x: self.concat_list_and(x, concat)
        return concatf([self.ATTRIBUTES[i] for i in attributes])

    def typing_to_str(self, types: List[int], concat=None) -> str:
        concatf = concat or self.concat_list_and
        if isinstance(concat, str):
            concatf = lambda x: self.concat_list_and(x, concat)
        return concatf([self.TYPES[i] for i in types])


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
