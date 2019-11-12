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

        intro = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True,
                                                    atk=min_atk_mult,
                                                    rcv=min_rcv_mult)

        if all(x == attributes[0] for x in attributes):
            attr_text = self.ATTRIBUTES[attributes[0]]
            max_mult = fmt_mult(max_mult) if len(attributes) != min_match else None
            max_match = len(attributes)
            return self.multi_of_one_attribute_match_text(intro, min_match, attr_text, max_mult, max_match)
        min_colors = self.attributes_format(attributes[:min_match], sep='+')
        alt_colors = self.attributes_format(attributes[1:], sep='+') if len(attributes) > min_match else None
        all_colors = self.attributes_format(attributes, sep='+')
        max_mult = fmt_mult(max_mult) if max_mult > min_atk_mult else None
        return self.multi_of_dif_attribute_match_text(intro, min_colors, alt_colors, max_mult, all_colors)

    def multi_of_one_attribute_match_text(self, intro, min_match, attr_text, max_mult, max_match):
        raise I13NotImplemented()
    
    def multi_of_dif_attribute_match_text(self, intro, min_colors, alt_colors, max_mult, all_colors):
        raise I13NotImplemented()

    def mass_match_convert(self, ls):
        min_count = ls.min_count
        max_count = getattr(ls, 'max_count', 0)

        min_atk_mult = getattr(ls, 'min_atk', ls.atk)
        min_rcv_mult = getattr(ls, 'min_rcv', ls.rcv)
        max_atk = ls.atk
        attributes = multi_getattr(ls, 'match_attributes', 'attributes')

        intro = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True,
                                                    atk=min_atk_mult, rcv=min_rcv_mult)
        or_more = max_count != min_count
        attr = self.fmt_multi_attr(attributes)
        max_mult = fmt_mult(max_atk) if max_count != min_count and max_count > 0 else None
        return self.mass_match_text(intro, min_count, or_more, attr, max_count, max_mult)

    def mass_match_text(self, intro, min_count, or_more, attr, max_count, max_mult):
        raise I13NotImplemented()

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
        bonus1 = self.fmt_stats_type_attr_bonus(c1)
        bonus2 = self.fmt_stats_type_attr_bonus(c2)
        has_both_condition = not c1.types and not c1.types and c1.atk != 1 and c2.atk != 1
        both_atk = fmt_mult(ls.atk) if has_both_condition else None
        return self.dual_passive_stat_text(bonus1, bonus2, both_atk)
    
    def dual_passive_stat_text(self, bonus1, bonus2, both_atk):
        raise I13NotImplemented()

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
        
        skill_parts = []
        if c1.atk != 0 or c1.rcv != 1 or c1.shield != 0:
            if c1.atk == 0:
                c1.atk = 1
            skill_parts.append(self.dual_threshold_stats_part_convert(c1))

        if c2.threshold != 0:
            skill_parts.append(self.dual_threshold_stats_part_convert(c2))

        return self.concat_list_semicolons(skill_parts)
    
    def dual_threshold_stats_part_convert(self, c):
        intro = self.fmt_stats_type_attr_bonus(c, reduce_join_txt=' and ', skip_attr_all=True)
        if c.threshold == 1:
            return self.dual_threshold_stats_part_full_hp_text(intro, c.above)
        threshold = fmt_mult(c.threshold * 100)
        return self.dual_threshold_stats_part_threshold_text(intro, c.above, threshold)
        
    def dual_threshold_stats_part_full_hp_text(self, intro, above):
        raise I13NotImplemented()

    def dual_threshold_stats_part_threshold_text(self, intro, above, threshold):
        raise I13NotImplemented()
    
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
        mult = self.fmt_multiplier_text(1, ls.atk, 1) if ls.atk not in [0, 1] else None
        return self.add_combo_att_text(mult, attr_condition_text, ls.bonus_combo)

    def add_combo_att_text(self, mult, attr_condition_text, bonus_combo):
        raise I13NotImplemented()

    def orb_heal_convert(self, ls):
        atk = ls.atk
        mult = self.fmt_multiplier_text(1, atk, 1) if atk and atk != 1 else None
        reduct_text = self.fmt_reduct_text(ls.shield) if ls.shield else None
        unbind_amt = ls.unbind_amt if ls.unbind_amt != 0 else None
        return self.orb_heal_text(atk, mult, reduct_text, unbind_amt, ls.heal_amt)
    
    def orb_heal_text(self, atk, mult, reduct_text, unbind_amt, heal_amt):
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
