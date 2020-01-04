import logging
import json
import os
import sys

from pad.raw.skills.en.skill_common import EnBaseTextConverter
from pad.raw.skills.leader_skill_text import LSTextConverter

human_fix_logger = logging.getLogger('human_fix')

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
SERIES = json.load(open(os.path.join(__location__, "../../../storage_processor/series.json")))

def capitalize_first(x: str):
    if not x:
        return x
    return x[0].upper() + x[1:]
    
class EnLSTextConverter(LSTextConverter, EnBaseTextConverter):
    _COLLAB_MAP = {x['collab_id']: x['name_na'] for x in SERIES if 'collab_id' in x}

    def n_attr_or_heal(self, attr, n_attr, format_string, is_range=False):
        if attr == [0, 1, 2, 3, 4]:
            return format_string.format(n_attr) + ' colors'
        elif attr == [0, 1, 2, 3, 4, 5]:
            return format_string.format(n_attr) + ' colors ({}+heal)'.format(n_attr - 1)
        attr_text = self.attributes_format(attr)
        if len(attr) > n_attr and is_range:
            return '{} of {}'.format(str(n_attr), attr_text)
        elif len(attr) > n_attr:
            return '{}+ of {} at once'.format(str(n_attr), attr_text)
        return '{} at once'.format(attr_text)

    def matching_n_or_more_attr(self, attr, min_attr, is_range=False):
        return ' when matching ' + self.n_attr_or_heal(attr, min_attr, '{} or more', is_range=is_range)

    def up_to_n_attr(self, attr, max_attr, mult):
        if attr == [0, 1, 2, 3, 4, 5]:
            return ' up to {}x at 5 colors+heal'.format(mult)
        if max_attr < 5 and (len(attr) < 5 or 5 in attr):
            return ' up to {}x when matching {}'.format(mult, max_attr)
        return ' up to {}x at '.format(mult) + self.n_attr_or_heal(attr, max_attr, '{}')

    def chance_to_text(self, chance, to_do):
        return '{}% chance to {}'.format(chance, to_do).capitalize()

    def threshold_stats_text(self, intro, above, threshold):
        skill_text = intro
        threshold_value = int(threshold)
        if threshold_value == 100:
            skill_text += ' when HP is {}'.format('full' if above else 'not full')
        elif threshold_value == 1:
            pass
        else:
            skill_text += ' when above ' if above else ' when below '
            skill_text += threshold + '% HP'
        return skill_text

    def dual_threshold_stats_part_full_hp_text(self, intro, above):
        skill_text = intro
        skill_text += ' when HP {} full'.format('is' if above else 'is not')
        return skill_text

    def dual_threshold_stats_part_threshold_text(self, intro, above, threshold):
        skill_text = intro
        skill_text += ' when {} '.format('above' if above else 'below')
        skill_text += '{}% HP'.format(threshold)
        return skill_text

    def combo_match_text(self, intro, min_combos, max_combos, up_to, max_mult):
        skill_text = intro
        skill_text += ' when {} or more combos'.format(min_combos)
        if up_to:
            skill_text += ' up to {}x at {} combos'.format(max_mult, max_combos)
        return skill_text

    def attribute_match_text(self, intro, attr_text, max_attr_text):
        return intro + attr_text + max_attr_text

    def multi_of_one_attribute_match_text(self, intro, min_match, attr_text, max_mult, max_match):
        skill_text = intro
        skill_text += ' when matching {}'.format(min_match)
        if not max_mult:
            skill_text += '+'
        skill_text += ' {} combos'.format(attr_text)
        if not max_mult:
            return skill_text
        skill_text += ', up to {}x at {} {} combos'.format(max_mult, max_match, attr_text)
        return skill_text

    def multi_of_dif_attribute_match_text(self, intro, min_colors, alt_colors, max_mult, all_colors):
        skill_text = intro
        skill_text += ' when matching {}'.format(min_colors)
        if alt_colors:
            skill_text += '({})'.format(alt_colors)
        if max_mult:
            skill_text += ' up to {}x when matching {}'.format(max_mult, all_colors)
        return skill_text

    def mass_match_text(self, intro, min_count, or_more, attr, max_count, max_mult):
        skill_text = intro
        skill_text += ' when matching {}'.format(min_count)
        if or_more:
            skill_text += ' or more connected'
        skill_text += '{} orbs'.format(attr)
        if not max_mult:
            return skill_text
        skill_text += ' up to {}x at {} orbs'.format(max_mult, max_count)
        return skill_text

    def after_attack_text(self, mult):
        return '{}x ATK additional damage when matching orbs'.format(mult)

    def heal_on_text(self, mult):
        return '{}x RCV additional heal when matching orbs'.format(mult)

    def resolve_text(self, percent):
        return 'May survive when HP is reduced to 0 (HP>{}%)'.format(percent)

    def bonus_time_text(self, intro, time):
        skill_text = intro + '; ' if intro else ''
        return skill_text + 'Increase orb movement time by {} seconds'.format(time)

    def counter_attack_text(self, is_guaranteed, chance, mult, attribute):
        if is_guaranteed:
            return '{}x {} counterattack'.format(mult, attribute)
        return '{}% chance to counterattack with {}x {} damage'.format(chance, mult, attribute)

    def egg_drop_text(self, mult):
        return '{}x Egg Drop rate'.format(mult)

    def coin_drop_text(self, mult):
        return '{}x Coin Drop rate'.format(mult)

    def skill_used_text(self, intro):
        return intro + ' on the turn a skill is used'

    def exact_combo_text(self, mult, combos):
        return '{}x ATK when exactly {} combos'.format(mult, combos)

    def passive_stats_type_atk_all_hp_text(self, hp_pct, atk_mult, type_text):
        skill_text = 'Reduce total HP by {}%; {}x ATK for '.format(hp_pct, atk_mult)
        skill_text += type_text + ' type'
        return skill_text

    def team_build_bonus_text(self, intro, card):
        return intro + ' if {} is on the team'.format(card)

    def rank_exp_rate_text(self, mult):
        return '{}x Rank EXP'.format(mult)

    def heart_tpa_stats_text(self, mult):
        return '{}x RCV when matching 4 Heal orbs'.format(mult)

    def five_orb_one_enhance_text(self, mult):
        return '{}x ATK for matched Att. when matching 5 Orbs with 1+ enhanced'.format(mult)

    def heart_cross_text(self, multiplier_text, reduct_text):
        skill_parts = [
            multiplier_text,
            reduct_text + ' when matching 5 Heal orbs in a cross formation'
        ]
        return self.concat_list_and(skill_parts)

    def multi_play_text(self, mult):
        return '{} when in multiplayer mode'.format(mult)

    def dual_passive_stat_text(self, bonus1, bonus2, both_atk):
        skill_parts = [
            bonus1,
            bonus2,
            '{}x ATK for allies with both Att.'.format(both_atk) if both_atk else None
        ]
        return self.concat_list_semicolons(skill_parts)

    def color_cross_text(self, atk, attrs):
        return '{}x ATK for each cross of 5 {} orbs'.format(atk, self.concat_list(attrs))

    def orb_remain_text(self, intro, base_atk, orb_count, max_atk):
        skill_text = '{}x ATK when there are {} or fewer orbs remaining'.format(base_atk, orb_count)
        if max_atk:
            skill_text += ' up to {}x ATK when 0 orbs left'.format(max_atk)
        return self.concat_list_semicolons([intro, skill_text])

    def get_collab_name(self, collab_id):
        if collab_id not in self._COLLAB_MAP:
            human_fix_logger.warning('Missing collab name for %s', collab_id)
        return self._COLLAB_MAP.get(collab_id, '<not populated:{}>'.format(collab_id))

    def collab_bonus_text(self, bonus, name):
        return '{} when all cards are from {}'.format(bonus, name)

    def multi_mass_match_text(self, atk, bonus_combo, min_match, num_attr):
        if atk not in [0, 1]:
            skill_text = self.fmt_multiplier_text(1, atk, 1) + ' and increase '
        else:
            skill_text = 'Increase '
        skill_text += 'combo by {} when matching {} or more connected'.format(
            bonus_combo,
            min_match
        )
        skill_text += self.fmt_multi_attr(num_attr, conjunction='and') + ' orbs at once'
        return skill_text

    def l_match_text(self, mult_text, reduct_text, attr):
        if mult_text:
            skill_text = mult_text
            if reduct_text:
                skill_text += ' and ' + reduct_text
        elif reduct_text:
            skill_text = mult_text
        else:
            skill_text = '???'
        skill_text += ' when matching 5' + attr + ' orbs in L shape'
        return skill_text

    def add_combo_att_text(self, mult, attr_condition_text, bonus_combo):
        skill_parts = [
            mult,
            'increase combo by {}{}'.format(bonus_combo, attr_condition_text)
        ]
        return self.concat_list_and(skill_parts)

    def orb_heal_text(self, atk, mult, reduct_text, unbind_amt, heal_amt):
        skill_parts = [mult, reduct_text]
        if unbind_amt:
            unbind_text = 'reduce awoken skill binds by {} turns'.format(unbind_amt)
            skill_parts.append(unbind_text)
        skill_text = self.concat_list_and(skill_parts)
        skill_text += ' when recovering more than {} HP from Heal orbs'.format(heal_amt)
        return skill_text

    def rainbow_bonus_damage_text(self, bonus_damage, attr_condition_text):
        skill_text = '{} additional damage{}'.format(bonus_damage, attr_condition_text)
        return skill_text

    def mass_match_bonus_damage_text(self, bonus_damage, min_match, attr_text):
        skill_text = '{} additional damage when matching {} or more'.format(bonus_damage, min_match)

        if attr_text:
            skill_text += '{} orbs'.format(attr_text)
        else:
            skill_text += ' orbs'

        return skill_text

    def color_combo_bonus_damage_text(self, bonus_damage, min_combo, attr_text):
        skill_text = '{} additional damage when attacking with {} or more'.format(bonus_damage, min_combo)
        if attr_text:
            skill_text += '{} combos'.format(attr_text)
        else:
            skill_text += ' combos'
        return skill_text

    def taiko_text(self):
        return 'Turn orb sound effects into Taiko noises'

    
    def full_text(self, text, tags=[]):
        if isinstance(text, (str,type(None))):
            text = [text or '']
        text = '; '.join(filter(None, text))
        tag_text = ''.join(filter(None, sorted([self.TAGS[tag].format(args) for tag, args in tags])))
        if tag_text:
            if text:
                return '{} {}'.format(tag_text, text)
            else:
                return tag_text
        return text
