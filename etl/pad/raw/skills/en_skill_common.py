import json, os
from typing import Dict

from pad.raw.skills.skill_common import BaseTextConverter

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
AWOSKILLS = json.load(open(os.path.join(__location__, "../../storage_processor/awoken_skill.json")))


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

    _AWAKENING_MAP = {x['pad_awakening_id']: x['name_na'] for x in AWOSKILLS}
    _AWAKENING_MAP[0] = ''

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
