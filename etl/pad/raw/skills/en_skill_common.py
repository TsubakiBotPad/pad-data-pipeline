from typing import Dict

from pad.raw.skills.skill_common import BaseTextConverter


class EnBaseTextConverter(BaseTextConverter):
    """Contains code shared across AS and LS converters."""

    _ATTRIBUTES = {0: 'Fire',
                   1: 'Water',
                   2: 'Wood',
                   3: 'Light',
                   4: 'Dark',
                   5: 'Heal',
                   6: 'Jammer',
                   7: 'Poison',
                   8: 'Mortal Poison',
                   9: 'Bomb'}

    _TYPES = {0: 'Evo Material',
              1: 'Balanced',
              2: 'Physical',
              3: 'Healer',
              4: 'Dragon',
              5: 'God',
              6: 'Attacker',
              7: 'Devil',
              8: 'Machine',
              12: 'Awaken Material',
              14: 'Enhance Material',
              15: 'Redeemable Material'}

    # TODO: we have these in awoken_skill.json should load from there. maybe do the same for the others
    _AWAKENING_MAP = {
        0: '',  # No need.
        1: 'Enhanced HP',
        2: 'Enhanced Attack',
        3: 'Enhanced Heal',
        4: 'Reduce Fire Damage',
        5: 'Reduce Water Damage',
        6: 'Reduce Wood Damage',
        7: 'Reduce Light Damage',
        8: 'Reduce Dark Damage',
        9: 'Auto-Recover',
        10: 'Resistance-Bind',
        11: 'Resistance-Dark',
        12: 'Resistance-Jammers',
        13: 'Resistance-Poison',
        14: 'Enhanced Fire Orbs',
        15: 'Enhanced Water Orbs',
        16: 'Enhanced Wood Orbs',
        17: 'Enhanced Light Orbs',
        18: 'Enhanced Dark Orbs',
        19: 'Extend Time',
        20: 'Recover Bind',
        21: 'Skill Boost',
        22: 'Enhanced Fire Att.',
        23: 'Enhanced Water Att.',
        24: 'Enhanced Wood Att.',
        25: 'Enhanced Light Att.',
        26: 'Enhanced Dark Att.',
        27: 'Two-Pronged Attack',
        28: 'Resistance-Skill Bind',
        29: 'Enhanced Heal Orbs',
        30: 'Multi Boost',
        31: 'Dragon Killer',
        32: 'God Killer',
        33: 'Devil Killer',
        34: 'Machine Killer',
        35: 'Balanced Killer',
        36: 'Attacker Killer',
        37: 'Physical Killer',
        38: 'Healer Killer',
        39: 'Evolve Material Killer',
        40: 'Awaken Material Killer',
        41: 'Enhance Material Killer',
        42: 'Vendor Material Killer',
        43: 'Enhanced Combo',
        44: 'Guard Break',
        45: 'Additional Attack',
        46: 'Enhanced Team HP',
        47: 'Enhanced Team RCV',
        48: 'Damage Void Shield Penetration',
        49: 'Awoken Assist',
        50: 'Super Additional Attack',
        51: 'Skill Charge',
        52: 'Resistance-Bind＋',
        54: 'Resistance-Cloud',
        53: 'Extend Time＋',
        55: 'Resistance-Board Restrict',
        56: 'Skill Boost＋',
        57: 'Enhance when HP is above 80%',
        58: 'Enhance when HP is below 50%',
        59: 'L-Shape Damage Reduction',
        60: 'L-Shape Attack',
        61: 'Super Enhanced Combo',
        62: 'Combo Orb',
        63: 'Skill Voice',
        64: 'Dungeon Bonus',
        65: 'Reduced HP',
        66: 'Reduced Attack',
        67: 'Reduced RCV',
    }

    @property
    def ATTRIBUTES(self) -> Dict[int, str]:
        return self._ATTRIBUTES

    @property
    def TYPES(self) -> Dict[int, str]:
        return self._TYPES

    @property
    def AWAKENING_MAP(self) -> Dict[int, str]:
        return self._AWAKENING_MAP

    def all_stats(self, multiplier):
        return '{}x all stats'.format(multiplier)

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
    def concat_list(list_to_concat):
        return ', '.join(list_to_concat)

    @staticmethod
    def concat_list_and(list_to_concat):
        filtered_list = list(filter(None, list_to_concat))
        if len(filtered_list) == 1:
            return filtered_list[0][0].upper() + filtered_list[0][1:]
        if len(filtered_list) == 2:
            return ' and '.join(filtered_list)
        return ', '.join(filtered_list[:-1]) + ', and ' + filtered_list[-1]

    @staticmethod
    def concat_list_semicolons(list_to_concat):
        return '; '.join(list(filter(None, list_to_concat)))
