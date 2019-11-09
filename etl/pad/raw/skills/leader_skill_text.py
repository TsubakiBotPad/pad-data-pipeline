from pad.raw.skills.leader_skill_common import ThresholdType, Tag, AttributeDict
from pad.raw.skills.skill_common import BaseTextConverter, fmt_mult, multi_getattr, I13NotImplemented


class LsTextConverter(BaseTextConverter):
    TAGS = {
        Tag.NO_SKYFALL: '[No skyfall]',
        Tag.DISABLE_POISON: '[Disable Poison & Mortal Poison orb effects]',
        Tag.BOARD_7X6: '[Board becomes 7x6]',
        Tag.FIXED_4S: '[Fixed 4 second movetime]',
        Tag.FIXED_5S: '[Fixed 5 second movetime]',
        Tag.ERASE_4P: '[Unable to erase 3 orbs or less]',
        Tag.ERASE_5P: '[Unable to erase 4 orbs or less]',
    }

    def tag_only_convert(self, ls):
        return None

    def passive_stats_convert(self, ls):
        return self.fmt_stats_type_attr_bonus(ls)

    def n_attr_or_heal(self, attr, n_attr, format_string, is_range=False):
        raise I13NotImplemented()

    def matching_n_or_more_attr(self, attr, min_attr, is_range=False):
        raise I13NotImplemented()

    def up_to_n_attr(self, attr, max_attr, mult):
        raise I13NotImplemented()
    
    @staticmethod
    def concat_list(list_to_concat):
        raise I13NotImplemented()

    def threshold_stats_convert(self, ls):
        intro = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True)
        above = ls.threshold_type == ThresholdType.ABOVE
        threshold = fmt_mult(ls.threshold * 100)
        is_100 = ls.threshold == 1
        return self.threshold_stats_text(intro, above, threshold, is_100)
    
    def threshold_stats_text(self, intro, above, threshold, is_100):
        raise I13NotImplemented()

    def combo_match_convert(self, ls):
        min_combos = ls.min_combos
        max_combos = getattr(ls, 'max_combos', min_combos)
        min_atk_mult = getattr(ls, 'min_atk', ls.atk)
        min_rcv_mult = getattr(ls, 'min_rcv', ls.rcv)

        if ls.atk == 1 and ls.rcv == 1 and min_combos == 0:
            return None
        intro = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True, atk=min_atk_mult,
                                                    rcv=min_rcv_mult)
        up_to = min_combos != max_combos
        max_mult = fmt_mult(ls.atk)
        return self.combo_match_text(intro, min_combos, max_combos, up_to, max_mult)
    
    def combo_match_text(self, intro, min_combos, max_combos, up_to, max_mult):
        raise I13NotImplemented()

    def attribute_match_convert(self, ls):
        min_attr = ls.min_attr
        max_attr = getattr(ls, 'max_attr', min_attr)
        attr = multi_getattr(ls, 'match_attributes', 'attributes')
        min_mult = getattr(ls, 'min_atk', ls.atk)
        min_rcv_mult = getattr(ls, 'min_rcv', ls.rcv)
        max_mult = getattr(ls, 'max_atk', ls.atk)

        intro = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True,
                                                    atk=min_mult, rcv=min_rcv_mult)
        attr_text = self.matching_n_or_more_attr(attr, min_attr, is_range=max_attr > min_attr)
        max_attr_text = self.up_to_n_attr(attr, max_attr, fmt_mult(max_mult)) if max_mult > min_mult else ''

        return self.attribute_match_text(intro, attr_text, max_attr_text)
    
    def attribute_match_text(self, intro, attr_text, max_attr_text):
        raise I13NotImplemented()

    def multi_attribute_match_convert(self, ls):
        attributes = multi_getattr(ls, 'match_attributes', 'attributes')
        if not attributes:
            return ''

        min_atk_mult = multi_getattr(ls, 'min_atk', 'atk')
        min_rcv_mult = multi_getattr(ls, 'min_rcv', 'rcv')
        min_match = multi_getattr(ls, 'min_attr', 'min_combo', 'min_match')
        max_mult = multi_getattr(ls, 'max_atk', 'atk')

        skill_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True,
                                                    atk=min_atk_mult,
                                                    rcv=min_rcv_mult)

        if all(x == attributes[0] for x in attributes):
            match_or_more = len(attributes) == min_match
            skill_text += ' when matching {}'.format(min_match)
            if match_or_more:
                skill_text += '+'
            try:
                skill_text += ' {} combos'.format(self.ATTRIBUTES[attributes[0]])
            except Exception as ex:
                print(ex)
            if not match_or_more:
                skill_text += ', up to {}x at {} {} combos'.format(
                    fmt_mult(max_mult), len(attributes), self.ATTRIBUTES[attributes[0]])

        else:
            min_colors = '+'.join([self.ATTRIBUTES[a] for a in attributes[:min_match]])
            skill_text += ' when matching {}'.format(min_colors)
            if len(attributes) > min_match:
                alt_colors = '+'.join([self.ATTRIBUTES[a] for a in attributes[1:min_match + 1]])
                skill_text += '({})'.format(alt_colors)

            if max_mult > min_atk_mult:
                all_colors = '+'.join([self.ATTRIBUTES[a] for a in attributes])
                skill_text += ' up to {}x when matching {}'.format(fmt_mult(max_mult), all_colors)

        return skill_text

    def mass_match_convert(self, ls):
        min_count = ls.min_count
        max_count = getattr(ls, 'max_count', 0)

        min_atk_mult = getattr(ls, 'min_atk', ls.atk)
        min_rcv_mult = getattr(ls, 'min_rcv', ls.rcv)
        max_atk = ls.atk
        attributes = multi_getattr(ls, 'match_attributes', 'attributes')

        skill_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True,
                                                    atk=min_atk_mult, rcv=min_rcv_mult)

        skill_text += ' when matching ' + str(min_count)
        if max_count != min_count:
            skill_text += ' or more connected'

        skill_text += self.fmt_multi_attr(attributes) + ' orbs'

        if max_count != min_count and max_count > 0:
            skill_text += ' up to {}x at {} orbs'.format(fmt_mult(max_atk), max_count)

        return skill_text

    def after_attack_convert(self, ls):
        return self.after_attack_text(fmt_mult(ls.multiplier))

    def after_attack_text(self, mult):
        raise I13NotImplemented()

    def heal_on_convert(self, ls):
        return self.heal_on_text(fmt_mult(ls.multiplier))

    def heal_on_text(self, mult):
        raise I13NotImplemented()

    def resolve_convert(self, ls):
        return self.resolve_text(str(ls.threshold * 100).rstrip('0').rstrip('.'))
    
    def resolve_text(self, percent):
        raise I13NotImplemented()

    def bonus_time_convert(self, ls):
        intro = self.fmt_stats_type_attr_bonus(ls)
        if not ls.time:
            return intro
        time = fmt_mult(ls.time)
        return self.bonus_time_text(intro, time)
    
    def bonus_time_text(self, intro, time):
        raise I13NotImplemented()

    def counter_attack_convert(self, ls):
        attribute = self.ATTRIBUTES[ls.attributes[0]]
        is_guaranteed = ls.chance == 1
        mult = str(ls.multiplier).rstrip('0').rstrip('.')
        chance = fmt_mult(ls.chance * 100)
        return self.counter_attack_text(is_guaranteed, chance, mult, attribute)
    
    def counter_attack_text(self, is_guaranteed, chance, mult, attribute):
        raise I13NotImplemented()

    def egg_drop_convert(self, ls):
        return self.egg_drop_text(fmt_mult(ls.multiplier))
    
    def egg_drop_text(self, mult):
        raise I13NotImplemented()

    def coin_drop_convert(self, ls):
        return self.coin_drop_text(fmt_mult(ls.multiplier))
    
    def coin_drop_text(self, mult):
        raise I13NotImplemented()

    def skill_used_convert(self, ls):
        intro = self.fmt_stats_type_attr_bonus(ls, skip_attr_all=True)
        return self.skill_used_text(intro)
    
    def skill_used_text(self, intro):
        raise I13NotImplemented()
    
    def exact_combo_convert(self, ls):
        return self.exact_combo_text(fmt_mult(ls.atk), str(ls.combos))
    
    def exact_combo_text(self, mult, combos):
        raise I13NotImplemented()

    def passive_stats_type_atk_all_hp_convert(self, ls):
        hp_pct = fmt_mult((1 - ls.hp) * 100)
        atk_mult = fmt_mult(ls.atk)
        type_text = ''
        for i in ls.types[:-1]:
            type_text += self.TYPES[i] + ', '
        type_text += self.TYPES[int(ls.types[-1])]
        return self.passive_stats_type_atk_all_hp_text(hp_pct, atk_mult, type_text)
    
    def passive_stats_type_atk_all_hp_text(self, hp_pct, atk_mult, type_text):
        raise I13NotImplemented()

    def team_build_bonus_convert(self, ls):
        intro = self.fmt_stats_type_attr_bonus(ls)
        card = '[{}]'.format(', '.join(map(str, ls.monster_ids)))
        return self.team_build_bonus_text(intro, card)
    
    def team_build_bonus_text(self, intro, card):
        raise I13NotImplemented()

    def rank_exp_rate_convert(self, ls):
        return self.rank_exp_rate_text(fmt_mult(ls.multiplier))

    def rank_exp_rate_text(self, mult):
        raise I13NotImplemented()

    def heart_tpa_stats_convert(self, ls):
        return self.heart_tpa_stats_text(fmt_mult(ls.rcv))
    
    def heart_tpa_stats_text(self, mult):
        raise I13NotImplemented()

    def five_orb_one_enhance_convert(self, ls):
        return self.five_orb_one_enhance_text(fmt_mult(ls.atk))
    
    def five_orb_one_enhance_text(self, mult):
        raise I13NotImplemented()

    def heart_cross_convert(self, ls):
        multiplier_text = self.fmt_multiplier_text(1, ls.atk, ls.rcv)
        reduct_text = self.fmt_reduct_text(ls.shield)
        return self.heart_cross_text(multiplier_text, reduct_text)
    
    def heart_cross_text(self, multiplier_text, reduct_text):
        raise I13NotImplemented()

    def multi_play_convert(self, ls):
        return self.multi_play_text(self.fmt_stats_type_attr_bonus(ls))
    
    def multi_play_text(self, mult):
        raise I13NotImplemented()

    def dual_passive_stat_convert(self, ls):
        c1 = AttributeDict({
            'attributes': getattr(ls, 'attributes_1', []),
            'types': getattr(ls, 'types_1', []),
            'hp': ls.hp_1,
            'atk': ls.atk_1,
            'rcv': ls.rcv_1,
            'shield': 0,
        })
        c2 = AttributeDict({
            'attributes': getattr(ls, 'attributes_2', []),
            'types': getattr(ls, 'types_2', []),
            'hp': ls.hp_2,
            'atk': ls.atk_2,
            'rcv': ls.rcv_2,
            'shield': 0,
        })
        skill_text = self.fmt_stats_type_attr_bonus(c1) + '; ' + self.fmt_stats_type_attr_bonus(c2)
        if not c1.types and not c1.types and c1.atk != 1 and c2.atk != 1:
            skill_text += '; ' + fmt_mult(ls.atk) + 'x ATK for allies with both Att.'

        return skill_text

    def dual_threshold_stats_convert(self, ls):
        c1 = AttributeDict({
            'attributes': ls.attributes,
            'types': ls.types,
            'threshold': ls.threshold_1,
            'above': ls.threshold_type_1 == ThresholdType.ABOVE,
            'hp': ls.hp,
            'atk': ls.atk_1,
            'rcv': getattr(ls, 'rcv_1', ls.rcv),
            'shield': getattr(ls, 'shield_1', ls.shield),
        })

        c2 = AttributeDict({
            'attributes': ls.attributes,
            'types': ls.types,
            'threshold': ls.threshold_2,
            'above': ls.threshold_type_2 == ThresholdType.ABOVE,
            'hp': ls.hp,
            'atk': ls.atk_2,
            'rcv': getattr(ls, 'rcv_2', ls.rcv),
            'shield': getattr(ls, 'shield_2', ls.shield),
        })

        # TODO: this could use some cleanup
        skill_text = ''
        if c1.atk != 0 or c1.rcv != 1 or c1.shield != 0:
            if c1.atk == 0:
                c1.atk = 1
            if c1.threshold == 1:
                skill_text = self.fmt_stats_type_attr_bonus(c1, reduce_join_txt=' and ', skip_attr_all=True)
                skill_text += ' when HP is full' if c1.above else ' when HP is not full'
            else:
                skill_text = self.fmt_stats_type_attr_bonus(c1, reduce_join_txt=' and ', skip_attr_all=True)
                skill_text += ' when above ' if c1.above else ' when below '
                skill_text += fmt_mult(c1.threshold * 100) + '% HP'

        if c2.threshold != 0:
            if skill_text != '':
                skill_text += '; '
            if c2.threshold == 1:
                skill_text += self.fmt_stats_type_attr_bonus(c2, reduce_join_txt=' and ', skip_attr_all=True)
                skill_text += ' when HP is full' if c2.above else ' when HP is not full'
            else:
                skill_text += self.fmt_stats_type_attr_bonus(c2, reduce_join_txt=' and ', skip_attr_all=True)
                skill_text += ' when above ' if c2.above else ' when below '
                skill_text += fmt_mult(c2.threshold * 100) + '% HP'

        return skill_text

    def color_cross_convert(self, ls):
        atk = fmt_mult(ls.crosses[0].atk)
        attr_list = [self.ATTRIBUTES[ls.crosses[i].attribute] for i in range(0, len(ls.crosses))]
        return self.color_cross_text(atk, attr_list)

    def color_cross_text(self, atk, attr_list):
        raise I13NotImplemented()

    def minimum_orb_convert(self, ls):
        skill_text = self.fmt_stats_type_attr_bonus(ls)
        return skill_text

    def orb_remain_convert(self, ls):
        intro = self.fmt_stats_type_attr_bonus(ls, atk=ls.min_atk)
        if ls.base_atk in [0, 1]:
            return intro
        base_atk = fmt_mult(ls.base_atk)
        orb_count = str(ls.orb_count)
        max_atk = fmt_mult(ls.atk) if ls.bonus_atk != 0 else None
        return self.orb_remain_text(intro, base_atk, orb_count, max_atk)
    
    def orb_remain_text(self, intro, base_atk, orb_count, max_atk):
        raise I13NotImplemented()

    def collab_bonus_convert(self, ls):
        return self.collab_bonus_text(self.fmt_stats_type_attr_bonus(ls), self.get_collab_name(ls.collab_id))
    
    def get_collab_name(self, collab_id):
        raise I13NotImplemented()
    
    def collab_bonus_text(self, bonus, name):
        raise I13NotImplemented()

    def multi_mass_match_convert(self, ls):
        return self.multi_mass_match_text(ls.atk, ls.bonus_combo, ls.min_match, ls.attributes)
    
    def multi_mass_match_text(self, atk, bonus_combo, min_match, num_attr):
        raise I13NotImplemented()

    def l_match_convert(self, ls):
        mult_text = self.fmt_multiplier_text(1, ls.atk, ls.rcv)
        reduct_text = self.fmt_reduct_text(ls.shield)
        attr = self.fmt_multi_attr(ls.attributes)
        return self.l_match_text(mult_text, reduct_text, attr)
    
    def l_match_text(self, mult_text, reduct_text, attr):
        raise I13NotImplemented()

    def add_combo_att_convert(self, ls):
        attr_condition_text = self.matching_n_or_more_attr(ls.attributes, ls.min_attr)
        return self.add_combo_att_text(attr_condition_text, ls.atk, ls.bonus_combo)

    def add_combo_att_text(self, attr_condition_text, atk, bonus_combo):
        raise I13NotImplemented()

    def orb_heal_convert(self, ls):
        atk = ls.atk
        mult = self.fmt_multiplier_text(1, atk, 1)
        shield = ls.shield
        reduct_text = self.fmt_reduct_text(shield) if shield != 0 else None
        return self.orb_heal_text(atk, mult, shield, reduct_text, ls.unbind_amt, ls.heal_amt)
    
    def orb_heal_text(self, atk, mult, shield, reduct_text, unbind_amt, heal_amt):
        raise I13NotImplemented()

    def rainbow_bonus_damage_convert(self, ls):
        attr_condition_text = self.matching_n_or_more_attr(ls.attributes, ls.min_attr)
        return self.rainbow_bonus_damage_text(ls.bonus_damage, attr_condition_text)
    
    def rainbow_bonus_damage_text(self, bonus_damage, attr_condition_text):
        raise I13NotImplemented()

    def mass_match_bonus_damage_convert(self, ls):
        attr_text = self.fmt_multi_attr(ls.attributes)
        return self.mass_match_bonus_damage_text(ls.bonus_damage, ls.min_match, attr_text)
    
    def mass_match_bonus_damage_text(self, bonus_damage, min_match, attr_text):
        raise I13NotImplemented()

    def taiko_convert(self, ls):
        return self.taiko_text()
    
    def taiko_text(self):
        raise I13NotImplemented()
