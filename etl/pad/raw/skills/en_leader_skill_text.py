from pad.raw.skills.en_skill_common import EnBaseTextConverter
from pad.raw.skills.leader_skill_text import LsTextConverter


class EnLsTextConverter(LsTextConverter, EnBaseTextConverter):
    _COLLAB_MAP = {
        0: '',
        1: 'Ragnarok Online Collab',
        2: 'Taiko no Tatsujin Collab',
        3: 'ECO Collab',
        5: 'Gunma\'s Ambition Collab',
        6: 'Final Fantasy Crystal Defender Collab',
        7: 'Famitsu Collab',
        8: 'Princess Punt Sweet Collab',
        9: 'Android Collab',
        10: 'Batman Collab',
        11: 'Capybara-san Collab',
        12: 'GungHo Collab',
        13: 'GungHo Collab',
        14: 'Evangelion Collab',
        15: 'Seven Eleven Collab',
        16: 'Clash of Clan Collab',
        17: 'Groove Coaster Collab',
        18: 'RO ACE Collab',
        19: 'Dragon\'s Dogma Collab',
        20: 'Takaoka City Collab',
        21: 'Monster Hunter 4G Collab',
        22: 'Shinrabansho Choco Collab',
        23: 'Thirty One Icecream Collab',
        24: 'Angry Bird Collab',
        26: 'Hunter x Hunter Collab',
        27: 'Hello Kitty Collab',
        28: 'PAD Battle Tournament Collab',
        29: 'BEAMS Collab',
        30: 'Dragon Ball Z Collab',
        31: 'Saint Seiya Collab',
        32: 'GungHo Collab',
        33: 'GungHo Collab',
        34: 'GungHo Collab',
        35: 'Gungho Collab',
        36: 'Bikkuriman Collab',
        37: 'Angry Birds Collab',
        38: 'DC Universe Collab',
        39: 'Sangoku Tenka Trigger Collab',
        40: 'Fist of the North Star Collab',
        41: 'Chibi Series',
        44: 'Chibi Keychain Series',
        45: 'Final Fantasy Collab',
        46: 'Ghost in Shell Collab',
        47: 'Duel Masters Collab',
        48: 'Attack on Titans Collab',
        49: 'Ninja Hattori Collab',
        50: 'Shounen Sunday Collab',
        51: 'Crows Collab',
        52: 'Bleach Collab',
        53: 'DC Universe Collab',
        55: 'Ace Attorney Collab',
        56: 'Kenshin Collab',
        57: 'Pepper Collab',
        58: 'Kinnikuman Collab',
        59: 'Napping Princess Collab',
        60: 'Magazine All-Stars Collab',
        61: 'Monster Hunter Collab',
        62: 'Special edition MP series',
        64: 'DC Universe Collab',
        65: 'Full Metal Alchemist Collab',
        66: 'King of Fighters \'98 Collab',
        67: 'Yu Yu Hakusho Collab',
        68: 'Persona Collab',
        69: 'Coca Cola Collab',
        70: 'Magic: The Gathering Collab',
        71: 'GungHo Collab',
        72: 'GungHo Collab',
        74: 'Power Pro Collab',
        76: 'Sword Art Online Collab',
        77: 'Kamen Rider Collab',
        78: 'Yo-kai Watch World Collab',
        83: 'Shaman King Collab',
        85: 'Samurai Spirits',
        86: 'Power Rangers',
        10001: 'Dragonbounds & Dragon Callers',
    }

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

    def threshold_stats_text(self, intro, above, threshold, is_100):
        skill_text = intro
        if is_100:
            skill_text += ' when HP is {}'.format('full' if above else 'not full')
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
            print('Missing collab name for', collab_id)
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

    def taiko_text(self):
        return 'Turn orb sound effects into Taiko noises'
