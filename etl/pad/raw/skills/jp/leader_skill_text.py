import logging
import json
import os

from pad.raw.skills.skill_common import *
from pad.raw.skills.jp.skill_common import *

human_fix_logger = logging.getLogger('human_fix')

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
SERIES = json.load(open(os.path.join(__location__, "../../../storage_processor/series.json")))


class JpLSTextConverter(JpBaseTextConverter):
    _COLLAB_MAP = {x['collab_id']: x['name_ja'] for x in SERIES if 'collab_id' in x}
    _GROUP_MAP = {
        0: 'ドット進化',
        1: '超転生進化のみ',
        2: '転生と超転生進化のみ',
    }

    TAGS = {
        Tag.NO_SKYFALL: '【落ちコンなし】',
        Tag.DISABLE_POISON: '【毒ダメージを無効化】',
        Tag.BOARD_7X6: '【7×6マス】',
        Tag.FIXED_TIME: '【操作時間{:d}秒固定】',
        Tag.ERASE_P: '【ドロップを{:d}個以下で消せない】',
    }

    def threshold_hp(self, thresh, above):
        thresh = int(thresh * 100)
        if thresh == 100:
            return 'HPが{}'.format('満タン時' if above else '99%以下')
        elif thresh == 1:
            return ''
        else:
            return 'HPが{}%以{}で'.format(thresh, '上' if above else '下')

    def matching_n_or_more_attr(self, attr, n_attr, is_range=False):
        skill_text = ''
        if attr == [0, 1, 2, 3, 4]:
            skill_text += '{}色以上同時攻撃'.format(n_attr)
        elif attr == [0, 1, 2, 3, 4, 5]:
            skill_text += '{}色({}色+回復)以上同時攻撃'.format(n_attr, n_attr - 1)
        elif len(attr) > n_attr and is_range:
            skill_text += '{}を{}個つなげて'.format(self.attributes_to_str(attr), n_attr)
        elif len(attr) > n_attr:
            skill_text += '{}から{}色以上同時攻撃'.format(self.attributes_to_str(attr), n_attr)
        else:
            skill_text += '{}同時攻撃'.format(self.attributes_to_str(attr, concat='、'))
        return skill_text

    def passive_stats_text(self, ls, **kwargs):
        o = self.fmt_stats_type_attr_bonus(ls, **kwargs)
        return o + '。' if o else ''

    def hp_reduction_optional_atk(self, hp: float, attributes: List[int], atk: float):
        text = self.fmt_multiplier_text(hp, 1, 1)
        if atk != 1:
            text += '、' + self.fmt_stats_type_attr_bonus(None, attributes=attributes, atk=atk)
        text += '。'
        return text

    def after_attack_text(self, ls):
        return 'ドロップ消した時、攻撃力ｘ{}倍の追い打ち。'.format(fmt_mult(ls.multiplier))

    def heal_on_text(self, ls):
        return 'ドロップ消した時、回復力ｘ{}倍のHPを回復。'.format(fmt_mult(ls.multiplier))

    def resolve_text(self, ls):
        return 'HPが0になる攻撃を受けてもふんばることがある(HPが{}%以上)。'.format(fmt_mult(ls.threshold * 100))

    def bonus_time_text(self, ls):
        skill_text = []
        skill_text.append(self.fmt_stats_type_attr_bonus(ls))
        if ls.time:
            skill_text.append('ドロップ操作時間を{}秒延長'.format(fmt_mult(ls.time)))
        return self.concat_list_semicolons(skill_text) + '。'

    def taiko_text(self, ls):
        return 'ドロップ操作時に太鼓の音がなる。'

    def threshold_stats_text(self, ls):
        return self.threshold_hp(ls.threshold, ls.above) + self.fmt_stats_type_attr_bonus(ls, reduce_join_txt='、') + '。'

    def counter_attack_text(self, ls):
        attribute = self.ATTRIBUTES[ls.attributes[0]]
        mult = fmt_mult(ls.multiplier)
        if ls.chance == 1:
            return '攻撃力ｘ{}倍の{}属性で反撃。'.format(mult, attribute)
        return '{}%の確率で攻撃力ｘ{}倍の{}属性で反撃。'.format(fmt_mult(ls.chance * 100), mult, attribute)

    def random_shield_threshold_text(self, ls):
        threshold_text = self.fmt_stats_type_attr_bonus(ls, skip_attr_all=True)
        threshold_text += self.threshold_hp(ls.threshold, ls.above)
        if ls.chance == 1:
            return threshold_text + '。'
        else:
            chance = fmt_mult(ls.chance * 100)
            return '{}%の確率で{}。'.format(chance, threshold_text).lower()

    def egg_drop_text(self, ls):
        return '卵ドロップ率ｘ{}倍。'.format(fmt_mult(ls.multiplier))

    def coin_drop_text(self, ls):
        return '入手コインｘ{}倍。'.format(fmt_mult(ls.multiplier))

    def rank_exp_rate_text(self, ls):
        return 'ランク経験値ｘ{}倍。'.format(fmt_mult(ls.multiplier))

    def skill_used_text(self, ls):
        return 'スキル使用時、{}。'.format(self.fmt_stats_type_attr_bonus(ls, skip_attr_all=True))

    def exact_combo_text(self, ls):
        return '{}コンボちょっとで攻撃力が{}倍。'.format(ls.combos, fmt_mult(ls.atk))

    def attribute_match_text(self, ls):
        skill_text = self.matching_n_or_more_attr(ls.match_attributes, ls.min_attr, is_range=ls.max_attr > ls.min_attr)
        skill_text += 'で' + self.fmt_stats_type_attr_bonus(ls, reduce_join_txt='、', skip_attr_all=True,
                                                           atk=ls.min_atk, rcv=ls.min_rcv)

        if ls.max_atk > ls.min_atk:
            skill_text += '、'
            if ls.match_attributes == [0, 1, 2, 3, 4, 5]:
                skill_text += '最大5色+回復で{}倍'.format(fmt_mult(ls.max_atk))
            elif ls.max_attr < 5 and (len(ls.match_attributes) < 5 or 5 in ls.match_attributes):
                skill_text += '最大{}色で{}倍'.format(ls.max_attr, fmt_mult(ls.max_atk))
            else:
                if ls.match_attributes == [0, 1, 2, 3, 4]:
                    skill_text += '最大{}色で{}倍'.format(ls.max_attr, fmt_mult(ls.max_atk))
                elif ls.match_attributes == [0, 1, 2, 3, 4, 5]:
                    skill_text += '最大{}色({}色+回復)で{}倍'.format(ls.max_attr, ls.max_attr - 1, fmt_mult(ls.max_atk))
                elif len(ls.match_attributes) > ls.max_attr:
                    skill_text += '{}個ところまで{}倍'.format(str(ls.max_attr), fmt_mult(ls.max_atk))
                else:
                    skill_text += '同時攻撃で{}倍'.format(self.attributes_to_str(ls.match_attributes))
        return skill_text + '。'

    def scaling_attribute_match_text(self, ls):
        min_atk = ls.min_atk
        min_attr = ls.min_attr

        if min_atk < ls.max_atk:
            if ls.min_atk == 1:
                min_atk = 1 + (ls.max_atk - ls.min_atk) / (ls.max_attr - ls.min_attr)
                min_attr += 1
        else:
            return self.attribute_match_text(ls)

        skill_text = self.matching_n_or_more_attr(ls.match_attributes, ls.min_attr)
        skill_text += 'で' + self.fmt_stats_type_attr_bonus(ls, reduce_join_txt='、', skip_attr_all=True,
                                                            atk=1, rcv=1) + '。'

        skill_text += self.matching_n_or_more_attr(ls.match_attributes, min_attr, is_range=ls.max_attr > min_attr)
        skill_text += 'で' + self.fmt_stats_type_attr_bonus(ls, reduce_join_txt='、', skip_attr_all=True,
                                                           atk=min_atk, shield=0)

        if ls.max_atk > ls.min_atk:
            skill_text += '、'
            if ls.match_attributes == [0, 1, 2, 3, 4, 5]:
                skill_text += '最大5色+回復で{}倍'.format(fmt_mult(ls.max_atk))
            elif ls.max_attr < 5 and (len(ls.match_attributes) < 5 or 5 in ls.match_attributes):
                skill_text += '最大{}色で{}倍'.format(ls.max_attr, fmt_mult(ls.max_atk))
            else:
                if ls.match_attributes == [0, 1, 2, 3, 4]:
                    skill_text += '最大{}色で{}倍'.format(ls.max_attr, fmt_mult(ls.max_atk))
                elif ls.match_attributes == [0, 1, 2, 3, 4, 5]:
                    skill_text += '最大{}色({}色+回復)で{}倍'.format(ls.max_attr, ls.max_attr - 1, fmt_mult(ls.max_atk))
                elif len(ls.match_attributes) > ls.max_attr:
                    skill_text += '{}個ところまで{}倍'.format(str(ls.max_attr), fmt_mult(ls.max_atk))
                else:
                    skill_text += '同時攻撃で{}倍'.format(self.attributes_to_str(ls.match_attributes))
        return skill_text + '。'


    def multi_attribute_match_text(self, ls):
        if not ls.match_attributes:
            return ''

        stat_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt='、', skip_attr_all=True,
                                                   atk=ls.min_atk,
                                                   rcv=ls.min_rcv)

        if len(set(ls.match_attributes)) == 1:
            skill_text = '{}の{}コンボ'.format(self.ATTRIBUTES[ls.match_attributes[0]], ls.min_match)
            if not len(ls.match_attributes) != ls.min_match:
                skill_text += '以上'
            skill_text += 'で{}'.format(stat_text)
            if len(ls.match_attributes) != ls.min_match:
                skill_text += '、最大{}コンボで{}倍'.format(len(ls.match_attributes), fmt_mult(ls.max_atk))
        else:
            skill_text = '{}'.format(self.attributes_to_str(ls.match_attributes[:ls.min_match], concat='、'))
            if len(ls.match_attributes) > ls.min_match:
                if ls.min_match == 1:
                    skill_text += 'が{}ドロップを消すと{}'.format(self.attributes_to_str(ls.match_attributes[1:]), stat_text)
                else:
                    skill_text += '({})のコンボ消すと{}'.format(self.attributes_to_str(ls.match_attributes[1:]), stat_text)
            else:
                skill_text += 'の同時攻撃で{}'.format(stat_text)
            if ls.max_atk > ls.min_atk:
                skill_text += 'の、最大{}で{}倍'.format(self.attributes_to_str(ls.match_attributes), fmt_mult(ls.max_atk))
        return skill_text + '。'

    def combo_match_text(self, ls):
        if ls.min_combos == 0:
            return ''
        skill_text = '{}コンボ以上で'.format(ls.min_combos)
        skill_text += self.fmt_stats_type_attr_bonus(ls, reduce_join_txt='、', skip_attr_all=True, atk=ls.min_atk,
                                                     rcv=ls.min_rcv)
        if ls.min_combos != ls.max_combos and ls.max_combos:
            skill_text += '、最大{}コンボで{}倍'.format(ls.max_combos, fmt_mult(ls.atk))
        return skill_text + '。'

    def passive_stats_type_atk_all_hp_text(self, ls):
        skill_text = '総HPが{}%減少するが、{}タイプの攻撃力が{}倍。'.format(fmt_mult((1 - ls.hp) * 100),
                                                          self.typing_to_str(ls.types),
                                                          fmt_mult(ls.atk))
        return skill_text

    def mass_match_text(self, ls):
        stat_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt='、', skip_attr_all=True,
                                                   atk=ls.min_atk, rcv=ls.min_rcv)
        skill_text = 'を{}個{}つなげて消すと{}'.format(ls.min_count,
                                              '以上' if ls.max_count != ls.min_count else '',
                                              stat_text)
        attr_text = self.fmt_multi_attr(ls.match_attributes) or 'ドロップ'
        skill_text = attr_text + skill_text
        if ls.max_count != ls.min_count and ls.max_count > 0:
            skill_text += '、最大{}個で{}倍'.format(ls.max_count, fmt_mult(ls.atk))
        return skill_text + '。'

    def team_build_bonus_text(self, ls):
        return '[{}]がチームにいると{}。'.format(self.concat_list(ls.monster_ids),
                                        self.fmt_stats_type_attr_bonus(ls))

    def dual_passive_stat_text(self, ls):
        skill_text = []
        skill_text.append(self.fmt_stats_type_attr_bonus(None,
                                                         attributes=ls.attributes_1,
                                                         types=ls.types_1,
                                                         hp=ls.hp_1,
                                                         atk=ls.atk_1,
                                                         rcv=ls.rcv_1))

        skill_text.append(self.fmt_stats_type_attr_bonus(None,
                                                         attributes=ls.attributes_2,
                                                         types=ls.types_2,
                                                         hp=ls.hp_2,
                                                         atk=ls.atk_2,
                                                         rcv=ls.rcv_2))

        if ls.atk_1 != 1 and ls.atk_2 != 1 and ls.types_1 == ls.types_2 == []:
            skill_text.append('両方の属性を持つ場合、攻撃力が{}倍'.format(fmt_mult(ls.atk)))

        return self.concat_list_semicolons(skill_text) + '。'

    def dual_threshold_stats_text(self, ls):
        skill_parts = []
        if str(ls.atk_1) != '1' or ls.rcv_1 != 1 or ls.shield_1 != 0:
            skill_text = self.threshold_hp(ls.threshold_1, ls.above_1)
            skill_text += self.fmt_stats_type_attr_bonus(None, reduce_join_txt='、', skip_attr_all=True,
                                                         atk=ls.atk_1,
                                                         rcv=ls.rcv_1,
                                                         types=ls.types,
                                                         attributes=ls.attributes,
                                                         hp=ls.hp,
                                                         shield=ls.shield_1)
            skill_parts.append(skill_text)

        if ls.threshold_2 != 0:
            skill_text = self.threshold_hp(ls.threshold_2, ls.above_2)
            skill_text += self.fmt_stats_type_attr_bonus(None, reduce_join_txt='、', skip_attr_all=True,
                                                         atk=ls.atk_2,
                                                         rcv=ls.rcv_2,
                                                         types=ls.types,
                                                         attributes=ls.attributes,
                                                         hp=ls.hp,
                                                         shield=ls.shield_2)
            skill_parts.append(skill_text)
        return self.concat_list_semicolons(skill_parts) + '。'

    def heart_tpa_stats_text(self, ls):
        return '回復ドロップを4個つなげ消すと回復力が{}倍。'.format(fmt_mult(ls.rcv))

    def five_orb_one_enhance_text(self, ls):
        return '強化ドロップを含めてを5個消した属性の攻撃力が{}倍。'.format(fmt_mult(ls.atk))

    def heart_cross_shield_text(self, ls):
        multiplier_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt='、')
        return '回復の5個十字消しで{}。'.format(multiplier_text)

    def heart_cross_combo_text(self, ls):
        return '回復の5個十字消しで{}コンボ加算。'.format(ls.bonus_combos)

    def color_cross_combo_text(self, ls):
        attrs = self.attributes_to_str(ls.attributes, concat='か').replace('、', 'か')
        return '{}の5個十字消しで{}コンボ加算。'.format(attrs, ls.bonus_combos)

    def multi_play_text(self, ls):
        multiplier_text = self.fmt_stats_type_attr_bonus(ls)
        return 'マルチプレイ時に{}。'.format(multiplier_text)

    def color_cross_text(self, ls):
        atk = fmt_mult(ls.multiplier)
        attrs = self.attributes_to_str(ls.attributes, concat='か').replace('、', 'か')
        return '{}の5個十字消し1個につき攻撃力が{}倍。'.format(attrs, atk)

    def collab_bonus_text(self, ls):
        collab_name = self._COLLAB_MAP.get(ls.collab_id, '〈不明なコラボ：{}〉'.format(ls.collab_id))
        return '{}キャラのみでチームを組むと、{}。'.format(collab_name, self.fmt_stats_type_attr_bonus(ls))

    def group_bonus_text(self, ls):
        group_name = self._GROUP_MAP.get(ls.group_id, '〈不明なグループ：{}〉'.format(ls.group_id))
        return '{}キャラのみでチームを組むと、{}。'.format(group_name, self.fmt_stats_type_attr_bonus(ls))

    def orb_remain_text(self, ls):
        skill_text = self.fmt_stats_type_attr_bonus(ls, atk=ls.min_atk)
        if ls.base_atk in [0, 1]:
            return skill_text
        if skill_text:
            skill_text += '。'
        skill_text += 'パズル後の残りドロップ数が{}個'.format(ls.orb_count)
        if ls.bonus_atk != 0:
            skill_text += 'で攻撃力{}倍、0個のところまで{}倍'.format(fmt_mult(ls.base_atk), fmt_mult(ls.max_bonus_atk))
        else:
            skill_text += '以下で攻撃力が{}倍'.format(fmt_mult(ls.base_atk))
        return skill_text + '。'

    def multi_mass_match_text(self, ls):
        stat_text = self.fmt_multiplier_text(1, ls.atk, 1)
        if ls.atk in [0, 1]:
            stat_text = ''
        skill_text = '{}を{}個以上{}つなげて消しと{}、{}コンボ加算。'.format(
            self.fmt_multi_attr(ls.attributes, conj='と' if ls.conj_and else 'か'),
            ls.min_match,
            '同時に' if len(ls.attributes) > 1 and ls.conj_and else '',
            stat_text,
            ls.bonus_combo)
        return skill_text

    def l_match_text(self, ls):
        stat_text = self.concat_list([self.fmt_multiplier_text(1, ls.atk, ls.rcv), self.fmt_reduct_text(ls.shield)])
        if self.fmt_multi_attr(ls.attributes):
            skill_text = '{}の5個L字消しで{}'.format(self.fmt_multi_attr(ls.attributes), stat_text)
        else:
            skill_text = 'ドロップの5個L字消しで{}'.format(stat_text)
        return skill_text + '。'

    def add_combo_att_text(self, ls):
        attr_condition_text = self.matching_n_or_more_attr(ls.attributes, ls.min_attr)
        skill_text = '{}で'.format(attr_condition_text)
        if ls.atk not in [0, 1]:
            skill_text += self.fmt_multiplier_text(1, ls.atk, 1) + '、'
        skill_text += '{}コンボ加算。'.format(ls.bonus_combo)
        return skill_text

    def orb_heal_text(self, ls):
        skill_parts = []
        if ls.atk != 1:
            skill_parts.append(self.fmt_multiplier_text(1, ls.atk, 1))
        if ls.shield:
            skill_parts.append(self.fmt_reduct_text(ls.shield))
        if ls.unbind_amt != 0:
            skill_parts.append('覚醒無効を{}ターン回復'.format(ls.unbind_amt))
        skill_text = '回復ドロップで{}以上回復すると'.format(ls.heal_amt)
        skill_text += self.concat_list(skill_parts)
        return skill_text + '。'

    def rainbow_bonus_damage_text(self, ls):
        attr_condition_text = self.matching_n_or_more_attr(ls.attributes, ls.min_attr)
        skill_text = '{}、固定{}ダメージ。'.format(attr_condition_text, ls.bonus_damage)
        return skill_text

    def mass_match_bonus_damage_text(self, ls):
        skill_text = 'を{}個以上つなげて消しと固定{}ダメージ'.format(ls.min_match, ls.bonus_damage)
        if self.fmt_multi_attr(ls.attributes):
            skill_text = self.fmt_multi_attr(ls.attributes) + skill_text
        else:
            skill_text = 'ドロップ' + skill_text
        return skill_text + '。'

    def color_combo_bonus_damage_text(self, ls):
        if len(ls.attributes) and ls.attributes[1:] != ls.attributes[:-1]:
            if ls.min_combo == 1:
                skill_text = '{}ドロップを消すと固定{}ダメージ'.format(self.fmt_multi_attr(list(set(ls.attributes)), conj='が'),
                                                         ls.bonus_damage)
            else:
                skill_text = '{}同時攻撃で固定{}ダメージ'.format(self.fmt_multi_attr(list(set(ls.attributes)), conj=''),
                                                      ls.bonus_damage)
        else:
            skill_text = '{}コンボ以上で固定{}ダメージ'.format(ls.min_combo, ls.bonus_damage)
            if ls.attributes:
                skill_text = '{}の'.format(self.fmt_multi_attr(list(set(ls.attributes)))) + skill_text

        return skill_text + '。'

    def color_combo_bonus_combo_text(self, ls):
        if len(ls.attributes) and ls.attributes[1:] != ls.attributes[:-1]:
            if ls.min_combo == 1:
                cond = '{}の同時攻擊'.format(self.fmt_multi_attr(list(set(ls.attributes)), conj=''))
            else:
                cond = '{}の同時攻擊'.format(self.fmt_multi_attr(list(set(ls.attributes))))
        elif not ls.attributes:
            cond = '{}の{}コンボ以上'.format(self.fmt_multi_attr(list(set(ls.attributes))), ls.min_combo)
        else:
            cond = '{}コンボ以上'.format(ls.min_combo)
        return cond + "で{}コンボ加算。".format(ls.bonus_combos)

    def combo_bonus_damage_text(self, ls):
        return 'ドロップを{}個以上つなげて消すと固定{:,}ダメージ'.format(ls.min_combos, ls.bonus_damage)

    def l_match_combo_text(self, ls):
        return '{}ドロップの5個L字消しで{}コンボ加算'.format(self.fmt_multi_attr(ls.attributes), ls.extra_combos)

    def full_text(self, text, tags=None):
        tags = tags or []
        if isinstance(text, (str, type(None))):
            text = [text or '']
        f_text = ''.join(filter(None, sorted([self.TAGS[tag].format(args) for tag, args in tags])))
        f_text += ''.join(text)
        return f_text

    def tag_only_text(self, ls):
        return ''


__all__ = ['JpLSTextConverter']
