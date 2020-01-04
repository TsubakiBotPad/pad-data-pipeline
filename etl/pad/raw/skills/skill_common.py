from operator import itemgetter
from typing import Dict, List


class I13NotImplemented(Exception):
    pass


def fmt_mult(x):
    return str(round(float(x), 2)).rstrip('0').rstrip('.')


def multi_getattr(o, *args):
    for a in args:
        v = getattr(o, a, None)
        if v is not None:
            return v
    raise Exception('Attributs not found:' + str(args))


class BaseTextConverter(object):
    """Contains code shared across AS and LS converters."""

    #############################################################################
    # Items here must be implemented by language-specific subclasses
    #############################################################################

    @property
    def ATTRIBUTES(self) -> Dict[int, str]:
        raise I13NotImplemented()

    @property
    def TYPES(self) -> Dict[int, str]:
        raise I13NotImplemented()

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
    def concat_list_and(list_to_concat):
        raise I13NotImplemented()

    @staticmethod
    def concat_list_semicolons(list_to_concat):
        raise I13NotImplemented()

    #############################################################################
    # Everything below here are common helpers
    #############################################################################

    def attributes_format(self, attributes: List[int], sep: str=', ') -> str:
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

    def fmt_multi_attr(self, attributes, conjunction='or'):
        # TODO: Returned value shouldn't start with a space
        prefix = ' '
        if 1 <= len(attributes) <= 7:
            attr_list = [self.ATTRIBUTES[i] for i in attributes]
        elif 7 <= len(attributes) < 10:
            att_sym_diff = sorted(list(set(self.ATTRIBUTES) - set(attributes)), key=lambda x: self.ATTRIBUTES[x])
            attr_list = [self.ATTRIBUTES[i] for i in att_sym_diff]
            prefix = ' non '
        else:
            return '' if conjunction == 'or' else ' all'

        if len(attr_list) == 1:
            return prefix + attr_list[0]
        elif len(attributes) == 2:
            return prefix + ' '.join([attr_list[0], conjunction, attr_list[1]])
        else:
            return prefix + ', '.join(attr for attr in attr_list[:-1]) + ', {} {}'.format(conjunction, attr_list[-1])

    def fmt_multiplier_text(self, hp_mult, atk_mult, rcv_mult):
        if hp_mult == atk_mult and atk_mult == rcv_mult:
            if hp_mult == 1:
                return None
            return self.all_stats(fmt_mult(hp_mult))

        mults = [(self.hp(), hp_mult), (self.atk(), atk_mult), (self.rcv(), rcv_mult)]
        mults = list(filter(lambda x: x[1] != 1, mults))
        mults.sort(key=itemgetter(1), reverse=True)

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
