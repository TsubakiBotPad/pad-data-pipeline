import json
import os
from typing import Dict

from pad.raw.skills.en.skill_common import capitalize_first
from pad.raw.skills.skill_common import BaseTextConverter, fmt_mult

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

AWOSKILLS = json.load(open(os.path.join(__location__, "../../../storage_processor/awoken_skill.json")))


class EmojiBaseTextConverter(BaseTextConverter):
    """Contains code shared across AS and LS converters."""

    # This is the 3rd dictionary
    _ATTRS = {
        -9: '{locked_bomb_orb}',
        -1: '{random_attribute}',
        None: '{fire_orb}',
        0: '{fire_orb}',
        1: '{water_orb}',
        2: '{wood_orb}',
        3: '{light_orb}',
        4: '{dark_orb}',
        5: '{healer_orb}',
        6: '{jammer_orb}',
        7: '{poison_orb}',
        8: '{mortal_poison_orb}',
        9: '{bomb_orb}',
    }
    # This is the 4th
    _TYPES = {
        0: '{evo_material_type}',
        1: '{balanced_type}',
        2: '{physical_type}',
        3: '{healer_type}',
        4: '{dragon_type}',
        5: '{god_type}',
        6: '{attacker_type}',
        7: '{devil_type}',
        8: '{machine_type}',
        12: '{awakening_material_type}',
        14: '{enhance_material_type}',
        15: '{redeemable_material_type}',
    }

    _AWAKENING_MAP = {x['pad_awakening_id']: x['name_en'] for x in AWOSKILLS}
    _AWAKENING_MAP[0] = ''

    @property
    def ATTRIBUTES(self) -> Dict[int, str]:
        return self._ATTRS

    @property
    def TYPES(self) -> Dict[int, str]:
        return self._TYPES

    @property
    def AWAKENING_MAP(self) -> Dict[int, str]:
        return self._AWAKENING_MAP

    def all_stats(self, multiplier):
        return '{}x all stats'.format(multiplier)

    @classmethod
    def attributes_to_emoji(cls, atts, emoji_map=None):
        if emoji_map is None:
            emoji_map = cls._ATTRS
        if not isinstance(atts, list):
            atts = [atts]
        emoji = ''
        if len(atts) >= 6:
            return 'All'
        for a in atts:
            emoji += emoji_map[a]
        return emoji

    def hp(self):
        return 'HP'

    def atk(self):
        return 'ATK'

    def rcv(self):
        return 'RCV'

    def reduce_all_pct(self, shield_text):
        return 'reduce damage taken by {}%'.format(shield_text)

    def reduce_attr_pct(self, attr_text, shield_text):
        return 'reduce damage taken from {} Att. by {}%'.format(attr_text, shield_text)

    @staticmethod
    def concat_list(iterable):
        return ', '.join([str(i) for i in iterable if i])

    @staticmethod
    def concat_list_and(iterable, conj='and'):
        array = [str(i) for i in iterable if i]
        if len(array) == 0:
            return ""
        elif len(array) == 1:
            return array[0]
        elif len(array) == 2:
            return " {} ".format(conj).join(array)
        array[-1] = conj + " " + array[-1]
        return ", ".join(array)

    @staticmethod
    def concat_list_semicolons(iterable):
        return '; '.join([str(i) for i in iterable if i])

    ################################################
    #               Format Functions               #
    ################################################

    def fmt_stats_type_attr_bonus(self, ls,
                                  reduce_join_txt='; ',
                                  skip_attr_all=True,
                                  atk=None,
                                  rcv=None,
                                  types=None,
                                  attributes=None,
                                  hp=None,
                                  shield=None,
                                  reduction_attributes=None):
        types = types or getattr(ls, 'types', [])
        attributes = attributes or getattr(ls, 'attributes', [])
        hp_mult = hp or getattr(ls, 'hp', 1)
        # TODO: maybe we can just move min_atk and min_rcv in here
        # TODO: had to add all these getattr because this is being used in the active
        #       skill parser as well, is this right?
        atk_mult = atk or getattr(ls, 'atk', 1)
        rcv_mult = rcv or getattr(ls, 'rcv', 1)
        damage_reduct = shield or getattr(ls, 'shield', 0)
        reduct_att = reduction_attributes or getattr(ls, 'reduction_attributes', [])

        skill_text = self.fmt_multiplier_text(hp_mult, atk_mult, rcv_mult)
        if skill_text:

            for_skill_text = ''
            if types:
                for_skill_text += ' {} type'.format(self.typing_to_str(types))

            is_attr_all = len(attributes) in [0, 5]
            should_skip_attr = is_attr_all and skip_attr_all

            if attributes and not should_skip_attr:
                if for_skill_text:
                    for_skill_text += ' and'
                color_text = 'all' if len(attributes) == 5 else self.attributes_to_str(attributes)
                for_skill_text += ' ' + color_text + ' Att.'

            if for_skill_text:
                skill_text += ' for' + for_skill_text

        reduct_text = self.fmt_reduct_text(damage_reduct, reduct_att)
        if reduct_text:
            if skill_text:
                skill_text += reduce_join_txt
            if not skill_text or ';' in reduce_join_txt:
                reduct_text = capitalize_first(reduct_text)
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
                return ''
            return self.all_stats(fmt_mult(hp_mult))

        mults = [('HP', hp_mult), ('ATK', atk_mult), ('RCV', rcv_mult)]
        mults = list(filter(lambda ml: ml[1] != 1, mults))
        mults.sort(key=lambda ml: ml[1], reverse=True)

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
            return ''
        shield_text = fmt_mult(shield * 100)
        if reduct_att in [None, [], [0, 1, 2, 3, 4]]:
            return self.reduce_all_pct(shield_text)
        else:
            attr_text = self.attributes_to_str(reduct_att)
            return self.reduce_attr_pct(attr_text, shield_text)
