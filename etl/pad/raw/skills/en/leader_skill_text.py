import logging
import json
import os

from pad.raw.skills.skill_common import *
from pad.raw.skills.en.skill_common import *

human_fix_logger = logging.getLogger('human_fix')

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
SERIES = json.load(open(os.path.join(__location__, "../../../storage_processor/series.json")))


class EnLSTextConverter(EnBaseTextConverter):
    _COLLAB_MAP = {x['collab_id']: x['name_en'] for x in SERIES if 'collab_id' in x}
    _GROUP_MAP = {
        0: 'Pixel Evolutions',
        1: 'Super Reincarnated Evolutions',
        2: 'Reincarnated or Super Reincarnated Evolutions',
    }

    TAGS = {
        Tag.NO_SKYFALL: '[No skyfall]',
        Tag.DISABLE_POISON: '[Disable Poison & Mortal Poison orb effects]',
        Tag.BOARD_7X6: '[Board becomes 7x6]',
        Tag.FIXED_TIME: '[Fixed {:d} second movetime]',
        Tag.ERASE_P: '[Unable to erase {:d} orbs or less]',
    }

    def threshold_hp(self, thresh, above):
        thresh = int(thresh * 100)
        if thresh == 100:
            return ' when HP is {}'.format('full' if above else 'not full')
        elif thresh == 1:
            return ''
        else:
            return ' when {} {}% HP'.format('above' if above else 'below', thresh)

    def matching_n_or_more_attr(self, attr, n_attr, is_range=False):
        skill_text = ' when matching '
        if attr == [0, 1, 2, 3, 4]:
            skill_text += '{} or more colors'.format(n_attr)
        elif attr == [0, 1, 2, 3, 4, 5]:
            skill_text += '{} or more colors ({}+heal)'.format(n_attr, n_attr - 1)
        elif len(attr) > n_attr and is_range:
            skill_text += '{} of {}'.format(str(n_attr), self.attributes_to_str(attr))
        elif len(attr) > n_attr:
            skill_text += '{}+ of {} at once'.format(str(n_attr), self.attributes_to_str(attr, concat='or'))
        else:
            skill_text += '{} at once'.format(self.attributes_to_str(attr))
        return skill_text

    def passive_stats_text(self, ls, **kwargs):
        return self.fmt_stats_type_attr_bonus(ls, **kwargs)

    def hp_reduction_optional_atk(self, hp: float, attributes: List[int], atk: float):
        text = self.fmt_multiplier_text(hp, 1, 1)
        if atk != 1:
            text += '; ' + self.fmt_stats_type_attr_bonus(None, attributes=attributes, atk=atk)
        return text

    def after_attack_text(self, ls):
        return '{}x ATK additional damage when matching orbs'.format(fmt_mult(ls.multiplier))

    def heal_on_text(self, ls):
        return '{}x RCV additional heal when matching orbs'.format(fmt_mult(ls.multiplier))

    def resolve_text(self, ls):
        return 'May survive when HP is reduced to 0 (HP>{}%)'.format(fmt_mult(ls.threshold * 100))

    def bonus_time_text(self, ls):
        skill_text = []
        skill_text.append(self.fmt_stats_type_attr_bonus(ls))
        if ls.time:
            skill_text.append('Increase orb movement time by {} seconds'.format(fmt_mult(ls.time)))
        return self.concat_list_semicolons(skill_text)

    def taiko_text(self, ls):
        return 'Turn orb sound effects into Taiko noises'

    def threshold_stats_text(self, ls):
        return '{}{}'.format(self.passive_stats_text(ls, reduce_join_txt=' and '),
                             self.threshold_hp(ls.threshold, ls.above))

    def counter_attack_text(self, ls):
        attribute = self.ATTRIBUTES[ls.attributes[0]]
        mult = fmt_mult(ls.multiplier)
        if ls.chance == 1:
            return '{}x {} counterattack'.format(mult, attribute)
        return '{}% chance to counterattack with {}x {} damage'.format(fmt_mult(ls.chance * 100), mult, attribute)

    def random_shield_threshold_text(self, ls):
        threshold_text = self.passive_stats_text(ls, skip_attr_all=True)
        threshold_text += self.threshold_hp(ls.threshold, ls.above)
        if ls.chance == 1:
            return threshold_text
        else:
            chance = fmt_mult(ls.chance * 100)
            return '{}% chance to {}'.format(chance, threshold_text).lower()

    def egg_drop_text(self, ls):
        return '{}x Egg Drop rate'.format(fmt_mult(ls.multiplier))

    def coin_drop_text(self, ls):
        return '{}x Coin Drop rate'.format(fmt_mult(ls.multiplier))

    def rank_exp_rate_text(self, ls):
        return '{}x Rank EXP'.format(fmt_mult(ls.multiplier))

    def skill_used_text(self, ls):
        return '{} on the turn a skill is used'.format(self.fmt_stats_type_attr_bonus(ls, skip_attr_all=True))

    def exact_combo_text(self, ls):
        return '{}x ATK when exactly {} combos'.format(fmt_mult(ls.atk), ls.combos)

    def attribute_match_text(self, ls):
        skill_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True,
                                                    atk=ls.min_atk, rcv=ls.min_rcv)
        skill_text += self.matching_n_or_more_attr(ls.match_attributes, ls.min_attr, is_range=ls.max_attr > ls.min_attr)

        if ls.max_atk > ls.min_atk:
            if ls.match_attributes == [0, 1, 2, 3, 4, 5]:
                skill_text += ' up to {}x at 5 colors+heal'.format(fmt_mult(ls.max_atk))
            elif ls.max_attr < 5 and (len(ls.match_attributes) < 5 or 5 in ls.match_attributes):
                skill_text += ' up to {}x when matching {}'.format(fmt_mult(ls.max_atk), ls.max_attr)
            else:
                skill_text += ' up to {}x at '.format(fmt_mult(ls.max_atk))
                if ls.match_attributes == [0, 1, 2, 3, 4]:
                    skill_text += '{} colors'.format(ls.max_attr)
                elif ls.match_attributes == [0, 1, 2, 3, 4, 5]:
                    skill_text += '{} colors ({}+heal)'.format(ls.max_attr, ls.max_attr - 1)
                elif len(ls.match_attributes) > ls.max_attr:
                    skill_text += '{}+ of {} at once'.format(str(ls.max_attr),
                                                             self.attributes_to_str(ls.match_attributes, concat='or'))
                else:
                    skill_text += '{} at once'.format(self.attributes_to_str(ls.match_attributes))
        return skill_text

    def scaling_attribute_match_text(self, ls):
        min_atk = ls.min_atk
        min_attr = ls.min_attr

        if min_atk < ls.max_atk:
            if ls.min_atk == 1:
                min_atk = 1 + (ls.max_atk - ls.min_atk) / (ls.max_attr - ls.min_attr)
                min_attr += 1
        else:
            return self.attribute_match_text(ls)

        skill_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True,
                                                    atk=1, rcv=1)
        skill_text += self.matching_n_or_more_attr(ls.match_attributes, ls.min_attr) + '; '

        skill_text += self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True,
                                                    atk=min_atk, shield=0)
        skill_text += self.matching_n_or_more_attr(ls.match_attributes, min_attr,
                                                   is_range=ls.max_attr > min_attr)

        if ls.max_atk > min_atk:
            if ls.match_attributes == [0, 1, 2, 3, 4, 5]:
                skill_text += ' up to {}x at 5 colors+heal'.format(fmt_mult(ls.max_atk))
            elif ls.max_attr < 5 and (len(ls.match_attributes) < 5 or 5 in ls.match_attributes):
                skill_text += ' up to {}x when matching {}'.format(fmt_mult(ls.max_atk), ls.max_attr)
            else:
                skill_text += ' up to {}x at '.format(fmt_mult(ls.max_atk))
                if ls.match_attributes == [0, 1, 2, 3, 4]:
                    skill_text += '{} colors'.format(ls.max_attr)
                elif ls.match_attributes == [0, 1, 2, 3, 4, 5]:
                    skill_text += '{} colors ({}+heal)'.format(ls.max_attr, ls.max_attr - 1)
                elif len(ls.match_attributes) > ls.max_attr:
                    skill_text += '{}+ of {} at once'.format(str(ls.max_attr),
                                                             self.attributes_to_str(ls.match_attributes, concat='or'))
                else:
                    skill_text += '{} at once'.format(self.attributes_to_str(ls.match_attributes))
        return skill_text

    def multi_attribute_match_text(self, ls):
        if not ls.match_attributes:
            return ''

        skill_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True,
                                                    atk=ls.min_atk,
                                                    rcv=ls.min_rcv)

        if len(set(ls.match_attributes)) == 1:
            skill_text += ' when matching {}'.format(ls.min_match)
            if not len(ls.match_attributes) != ls.min_match:
                skill_text += '+'
            skill_text += ' {} combos'.format(self.ATTRIBUTES[ls.match_attributes[0]])
            if len(ls.match_attributes) != ls.min_match:
                skill_text += ', up to {}x at {} {} combos'.format(fmt_mult(ls.max_atk), len(ls.match_attributes),
                                                                   self.ATTRIBUTES[ls.match_attributes[0]])
        else:
            skill_text += ' when matching {}'.format(self.attributes_to_str(ls.match_attributes[:ls.min_match]))
            if len(ls.match_attributes) > ls.min_match:
                if ls.min_match == 1:
                    skill_text += ' or {}'.format(self.attributes_to_str(ls.match_attributes[1:]))
                else:
                    skill_text += ' (or {})'.format(self.attributes_to_str(ls.match_attributes[1:]))
            if ls.max_atk > ls.min_atk:
                skill_text += ' up to {}x when matching {}'.format(fmt_mult(ls.max_atk),
                                                                   self.attributes_to_str(ls.match_attributes))
        return skill_text

    def combo_match_text(self, ls):
        if ls.min_combos == 0:
            return ''
        skill_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True, atk=ls.min_atk,
                                                    rcv=ls.min_rcv)
        skill_text += ' when {} or more combos'.format(ls.min_combos)
        if ls.min_combos != ls.max_combos and ls.max_combos:
            skill_text += ' up to {}x at {} combos'.format(fmt_mult(ls.atk), ls.max_combos)
        return skill_text

    def passive_stats_type_atk_all_hp_text(self, ls):
        skill_text = 'Reduce total HP by {}%; {}x ATK for '.format(fmt_mult((1 - ls.hp) * 100), fmt_mult(ls.atk))
        skill_text += self.typing_to_str(ls.types) + ' type'
        return skill_text

    def mass_match_text(self, ls):
        skill_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True,
                                                    atk=ls.min_atk, rcv=ls.min_rcv)
        skill_text += ' when matching {}'.format(ls.min_count)
        if ls.max_count != ls.min_count:
            skill_text += ' or more connected'
        if self.fmt_multi_attr(ls.match_attributes):
            skill_text += ' {}'.format(self.fmt_multi_attr(ls.match_attributes))
        skill_text += ' orbs'
        if ls.max_count != ls.min_count and ls.max_count > 0:
            skill_text += ' up to {}x at {} orbs'.format(fmt_mult(ls.atk), ls.max_count)
        return skill_text

    def team_build_bonus_text(self, ls):
        return '{} if [{}] is on the team'.format(self.fmt_stats_type_attr_bonus(ls),
                                                  self.concat_list(ls.monster_ids))

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
            skill_text.append('{}x ATK for allies with both Att.'.format(fmt_mult(ls.atk)))

        return self.concat_list_semicolons(skill_text)

    def dual_threshold_stats_text(self, ls):
        skill_parts = []
        if str(ls.atk_1) != '1' or ls.rcv_1 != 1 or ls.shield_1 != 0:
            skill_text = self.fmt_stats_type_attr_bonus(None, reduce_join_txt=' and ', skip_attr_all=True,
                                                        atk=ls.atk_1,
                                                        rcv=ls.rcv_1,
                                                        types=ls.types,
                                                        attributes=ls.attributes,
                                                        hp=ls.hp,
                                                        shield=ls.shield_1)
            if ls.threshold_1 == 1:
                skill_text += ' when HP {} full'.format('is' if ls.above_1 else 'is not')
            else:
                skill_text += ' when {} '.format('above' if ls.above_1 else 'below')
                skill_text += '{}% HP'.format(fmt_mult(ls.threshold_1 * 100))
            skill_parts.append(skill_text)

        if ls.threshold_2 != 0:
            skill_text = self.fmt_stats_type_attr_bonus(None, reduce_join_txt=' and ', skip_attr_all=True,
                                                        atk=ls.atk_2,
                                                        rcv=ls.rcv_2,
                                                        types=ls.types,
                                                        attributes=ls.attributes,
                                                        hp=ls.hp,
                                                        shield=ls.shield_2)
            if ls.threshold_2 == 1:
                skill_text += ' when HP {} full'.format('is' if ls.above_2 else 'is not')
            else:
                skill_text += ' when {} '.format('above' if ls.above_2 else 'below')
                skill_text += '{}% HP'.format(fmt_mult(ls.threshold_2 * 100))
            skill_parts.append(skill_text)
        return self.concat_list_semicolons(skill_parts)

    def heart_tpa_stats_text(self, ls):
        return '{}x RCV when matching 4 Heal orbs'.format(fmt_mult(ls.rcv))

    def five_orb_one_enhance_text(self, ls):
        return '{}x ATK for matched Att. when matching 5 Orbs with 1+ enhanced'.format(fmt_mult(ls.atk))

    def heart_cross_shield_text(self, ls):
        multiplier_text = self.passive_stats_text(ls, reduce_join_txt=' and ')
        return '{} when matching 5 Heal orbs in a cross formation'.format(multiplier_text)

    def heart_cross_combo_text(self, ls):
        return 'Increase combo by {} when matching 5 Heal orbs in a cross formation'.format(ls.bonus_combos)

    def color_cross_combo_text(self, ls):
        attrs = self.attributes_to_str(ls.attributes, concat='or')
        return 'Increase combo by {} for each cross of 5 {} orbs'.format(ls.bonus_combos, attrs)

    def multi_play_text(self, ls):
        multiplier_text = self.passive_stats_text(ls)
        return '{} when in multiplayer mode'.format(multiplier_text)

    def color_cross_text(self, ls):
        atk = fmt_mult(ls.multiplier)
        attrs = self.attributes_to_str(ls.attributes, concat='or')
        return '{}x ATK for each cross of 5 {} orbs'.format(atk, attrs)

    def collab_bonus_text(self, ls):
        if ls.collab_id not in self._COLLAB_MAP:
            human_fix_logger.warning('Missing collab name for %s', ls.collab_id)
        collab_name = self._COLLAB_MAP.get(ls.collab_id, '<not populated:{}>'.format(ls.collab_id))
        return '{} when all subs are from {}'.format(self.fmt_stats_type_attr_bonus(ls), collab_name)

    def group_bonus_text(self, ls):
        if ls.group_id not in self._GROUP_MAP:
            human_fix_logger.warning('Missing group name for %s', ls.group_id)
        group_name = self._GROUP_MAP.get(ls.group_id, '<not populated:{}>'.format(ls.group_id))
        return '{} when all subs are {}'.format(self.fmt_stats_type_attr_bonus(ls), group_name)

    def orb_remain_text(self, ls):
        skill_text = self.fmt_stats_type_attr_bonus(ls, atk=ls.min_atk)
        if ls.base_atk in [0, 1]:
            return skill_text
        if skill_text:
            skill_text += '; '
        skill_text += '{}x ATK when there are {} or fewer orbs remaining'.format(fmt_mult(ls.base_atk), ls.orb_count)
        if ls.bonus_atk != 0:
            skill_text += ' up to {}x ATK when 0 orbs left'.format(fmt_mult(ls.max_bonus_atk))
        return skill_text

    def multi_mass_match_text(self, ls):
        if ls.atk not in [0, 1]:
            skill_text = self.fmt_multiplier_text(1, ls.atk, 1)
            if ls.bonus_combo:
                skill_text += ' and increase combo by {}'.format(ls.bonus_combo)
        else:
            skill_text = 'Increase combo by {}'.format(ls.bonus_combo)
        skill_text += ' when matching {} or more connected '.format(ls.min_match)
        skill_text += self.fmt_multi_attr(ls.attributes, conj='and' if ls.conj_and else 'or') + ' orbs at once'
        return skill_text

    def l_match_text(self, ls):
        skill_text = self.concat_list_and(
            [self.fmt_multiplier_text(1, ls.atk, ls.rcv), self.fmt_reduct_text(ls.shield)])
        if not skill_text:
            skill_text = '???'
        if self.fmt_multi_attr(ls.attributes):
            skill_text += ' when matching 5 {} orbs in an L shape'.format(self.fmt_multi_attr(ls.attributes))
        else:
            skill_text += ' when matching 5 orbs in an L shape'
        return skill_text

    def add_combo_att_text(self, ls):
        attr_condition_text = self.matching_n_or_more_attr(ls.attributes, ls.min_attr)
        skill_text = ''
        if ls.atk not in [0, 1]:
            skill_text += self.fmt_multiplier_text(1, ls.atk, 1)
            if ls.bonus_combo:
                skill_text += ' and increase combo by {}'.format(ls.bonus_combo)
        elif ls.bonus_combo:
            skill_text += 'Increase combo by {}'.format(ls.bonus_combo)
        skill_text += attr_condition_text
        return skill_text

    def orb_heal_text(self, ls):
        skill_parts = []
        if ls.atk != 1:
            skill_parts.append(self.fmt_multiplier_text(1, ls.atk, 1))
        if ls.shield:
            skill_parts.append(self.fmt_reduct_text(ls.shield))
        if ls.unbind_amt != 0:
            skill_parts.append('reduce awoken skill binds by {:,} turns'.format(ls.unbind_amt))
        skill_text = self.concat_list_and(skill_parts)
        skill_text += ' when recovering more than {:,} HP from Heal orbs'.format(ls.heal_amt)
        return skill_text

    def rainbow_bonus_damage_text(self, ls):
        attr_condition_text = self.matching_n_or_more_attr(ls.attributes, ls.min_attr)
        skill_text = '{:,} additional true damage{}'.format(ls.bonus_damage, attr_condition_text)
        return skill_text

    def mass_match_bonus_damage_text(self, ls):
        skill_text = '{:,} additional true damage when matching {} or more'.format(ls.bonus_damage, ls.min_match)
        if self.fmt_multi_attr(ls.attributes):
            skill_text += ' {} orbs'.format(self.fmt_multi_attr(ls.attributes))
        else:
            skill_text += ' orbs'
        return skill_text

    def color_combo_bonus_damage_text(self, ls):
        if len(ls.attributes) and ls.attributes[1:] != ls.attributes[:-1]:
            skill_text = '{:,} additional true damage when matching {}'.format(ls.bonus_damage,
                                                                               self.fmt_multi_attr(
                                                                                   list(set(ls.attributes)),
                                                                                   conj='or' if ls.min_combo < len(
                                                                                       ls.attributes) else 'and'))
        else:
            skill_text = '{:,} additional true damage when matching {} or more'.format(ls.bonus_damage, ls.min_combo)
            if ls.attributes:
                skill_text += ' {} combos'.format(self.fmt_multi_attr(list(set(ls.attributes))))
            else:
                skill_text += ' combos'
        return skill_text

    def color_combo_bonus_combo_text(self, ls):
        if len(ls.attributes) and ls.attributes[1:] != ls.attributes[:-1]:
            skill_text = 'Increase combo by {} when matching {}'.format(ls.bonus_combos,
                                                                        self.fmt_multi_attr(list(set(ls.attributes)),
                                                                                            conj='or' if ls.min_combo < len(
                                                                                                ls.attributes) else 'and'))
        else:
            skill_text = 'Increase combo by {} when matching {} or more'.format(ls.bonus_combos, ls.min_combo)
            if ls.attributes:
                skill_text += ' {} combos'.format(self.fmt_multi_attr(list(set(ls.attributes))))
            else:
                skill_text += ' combos'
        return skill_text

    def combo_bonus_damage_text(self, ls):
        return '{:,} additional true damage when matching {} or more combos'.format(ls.bonus_damage, ls.min_combos)

    def l_match_combo_text(self, ls):
        skill_text = 'Add {} combos when matching 5'.format(ls.extra_combos)
        if self.fmt_multi_attr(ls.attributes):
            skill_text += ' {}'.format(self.fmt_multi_attr(ls.attributes))
        return skill_text + ' orbs in an L shape'

    def full_text(self, text, tags=None):
        tags = tags or []
        if isinstance(text, (str, type(None))):
            text = [text or '']
        text = self.concat_list_semicolons(text)
        tag_text = ''.join(filter(None, sorted([self.TAGS[tag].format(args) for tag, args in tags])))
        return '{} {}'.format(tag_text, text).strip(' ')

    def tag_only_text(self, ls):
        return ''


__all__ = ['EnLSTextConverter']
