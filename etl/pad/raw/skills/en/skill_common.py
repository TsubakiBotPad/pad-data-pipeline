import json, os
from typing import Dict, List
from enum import Enum

from pad.raw.skills.skill_common import *
import pad.raw.skills.skill_common as base_skill_common

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
AWOSKILLS = json.load(open(os.path.join(__location__, "../../../storage_processor/awoken_skill.json")))

__all__ = list(filter(lambda x: not x.startswith('__'), dir(base_skill_common)))

def public(x):
    global __all__
    __all__.append(x.__name__)
    return x

@public    
def capitalize_first(x: str):
    if not x:
        return x
    elif len(x) == 1:
        return x.upper()
    else:
        return x[0].upper() + x[1:]

article_irregulars = {
    'L shape':'an L shape',
}

@public 
def indef_article(noun):
    return article_irregulars.get(noun, 'a{} {}'.format('n' if noun[0] in 'aeiou' else '', noun))

irregulars = {
    'status': 'statuses',
    'both leaders': 'both leaders',
    'active skills': 'active skills',
    'awoken skills': 'awoken skills',
}

@public 
def pluralize(noun, number):
    irregular_plural = irregulars.get(noun)
    if number not in (1, '1'):
        noun = irregular_plural or noun + 's'
    return noun

@public 
def pluralize2(noun, number, max_number = None):
    if max_number is not None:
        number = minmax(number, max_number)
    if number is None:
        return noun
    irregular_plural = irregulars.get(noun)
    if number not in (1, '1'):
        noun = irregular_plural or noun + 's'
    return "{} {}".format(number, noun)

@public 
class EnBaseTextConverter(BaseTextConverter):
    """Contains code shared across AS and LS converters."""

    _ATTRS = {0: 'Fire',
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
        return self._ATTRS

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
        return ', '.join(map(str,list_to_concat))

    @staticmethod
    def concat_list_and(l):
        l = [str(i) for i in l if i]
        if len(l) == 0:
            return ""
        elif len(l) == 1:
            return l[0]
        elif len(l) == 2:
            return " and ".join(l)
        l[-1] = "and " + l[-1]
        return ", ".join(l)

    @staticmethod
    def concat_list_semicolons(list_to_concat):
        return '; '.join(filter(None, list_to_concat))
