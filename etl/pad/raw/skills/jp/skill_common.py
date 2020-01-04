import json, os
from typing import Dict

from pad.raw.skills.skill_common import BaseTextConverter
from pad.raw.skills.en.skill_common import EnBaseTextConverter as DefaultTextConverter

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
AWOSKILLS = json.load(open(os.path.join(__location__, "../../../storage_processor/awoken_skill.json")))
    
class JpBaseTextConverter(DefaultTextConverter):
    """Contains code shared across AS and LS converters."""

    _ATTRS = {0: '火',
              1: '水',
              2: '木',
              3: '光',
              4: '闇',
              5: '回復',
              6: 'お邪魔',
              7: '毒',
              8: '猛毒',
              9: '爆弾'}

    _TYPES = {0: '進化用',
              1: 'バランス',
              2: '体力',
              3: '回復',
              4: 'ドラゴン',
              5: '神',
              6: '攻撃',
              7: '悪魔',
              8: 'マシン',
              12: '覚醒用',
              14: '強化合成用',
              15: '売却用'}

    _AWAKENING_MAP = {x['pad_awakening_id']: x['name_jp'] for x in AWOSKILLS}
    #TODO: Make this unnecessary
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
        return '全パラメータが{}倍'.format(multiplier)

    def hp(self):
        return 'HP'

    def atk(self):
        return 'ATK'

    def rcv(self):
        return 'RCV'

    def reduce_all_pct(self, shield_text):
        return '受けるダメージを{}%減少'.format(shield_text)

    def reduce_attr_pct(self, attr_text, shield_text):
        return '{}属性の敵から受けるダメージを{}%減少'.format(attr_text, shield_text)

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
            return "と".join(l)
        return ", ".join(l)

    @staticmethod
    def concat_list_semicolons(list_to_concat):
        return '。'.join(filter(None, list_to_concat))
