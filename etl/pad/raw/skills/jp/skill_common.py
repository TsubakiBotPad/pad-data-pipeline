import json
import os
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
class JpBaseTextConverter(BaseTextConverter):
    """Contains code shared across AS and LS converters."""

    _ATTRS = {
        -9: 'ロックされた爆弾',
        -1: 'ランダム属性の',
        None: '火',
        0: '火',
        1: '水',
        2: '木',
        3: '光',
        4: '闇',
        5: '回復',
        6: 'お邪魔',
        7: '毒',
        8: '猛毒',
        9: '爆弾',
    }

    _TYPES = {
        0: '進化用',
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
        15: '売却用',
    }

    _AWAKENING_MAP = {x['pad_awakening_id']: x['name_jp'] for x in AWOSKILLS}
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
        return '、'.join(map(str, list_to_concat))

    @staticmethod
    def concat_list_and(iterable, conj='と'):
        arr = [str(i) for i in iterable if i]
        if len(arr) == 0:
            return ""
        elif len(arr) == 1:
            return arr[0]
        elif len(arr) == 2:
            return conj.join(arr)
        return "、".join(arr)

    @staticmethod
    def concat_list_semicolons(list_to_concat):
        return '。'.join(filter(None, list_to_concat))

    @staticmethod
    def big_number(n):
        if n == 0:
            return str(int(n // 1e0)) + ''
        elif n % 1e8 == 0:
            return str(int(n // 1e8)) + '億'
        elif n % 1e7 == 0:
            return str(int(n // 1e7)) + '千万'
        elif n % 1e4 == 0:
            return str(int(n // 1e4)) + '万'
        elif n % 1e3 == 0:
            return str(int(n // 1e3)) + '千'

        elif n < 1e4:
            return str(n)
        elif n < 1e8:
            return str(n)[:-4] + '万' + str(n)[-4:]
        else:
            return str(n)[:-8] + '億' + str(n)[-8:-4] + '万' + str(n)[-4:]
