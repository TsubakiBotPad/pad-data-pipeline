from pad.raw.skills.leader_skill_common import ThresholdType, Tag, AttributeDict
from pad.raw.skills.skill_common import BaseTextConverter, fmt_mult, multi_getattr


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

    def threshold_stats_convert(self, ls):
        above = ls.threshold_type == ThresholdType.ABOVE
        skill_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True)
        if ls.threshold != 1:
            skill_text += ' when above ' if above else ' when below '
            skill_text += fmt_mult(ls.threshold * 100) + '% HP'
        else:
            skill_text += ' when '
            skill_text += 'HP is full' if above else 'HP is not full'
        return skill_text

    def combo_match_convert(self, ls):
        min_combos = ls.min_combos
        max_combos = getattr(ls, 'max_combos', min_combos)
        min_atk_mult = getattr(ls, 'min_atk', ls.atk)
        min_rcv_mult = getattr(ls, 'min_rcv', ls.rcv)

        if ls.atk == 1 and ls.rcv == 1 and min_combos == 0:
            return None

        skill_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True, atk=min_atk_mult,
                                                    rcv=min_rcv_mult)
        skill_text += ' when {} or more combos'.format(min_combos)

        if min_combos != max_combos:
            skill_text += ' up to {}x at {} combos'.format(fmt_mult(ls.atk), max_combos)

        return skill_text

    def attribute_match_convert(self, ls):

        min_attr = ls.min_attr
        max_attr = getattr(ls, 'max_attr', min_attr)
        attr = multi_getattr(ls, 'match_attributes', 'attributes')
        min_mult = getattr(ls, 'min_atk', ls.atk)
        min_rcv_mult = getattr(ls, 'min_rcv', ls.rcv)
        max_mult = getattr(ls, 'max_atk', ls.atk)

        skill_text = self.fmt_stats_type_attr_bonus(ls, reduce_join_txt=' and ', skip_attr_all=True,
                                                    atk=min_mult, rcv=min_rcv_mult)

        if attr == [0, 1, 2, 3, 4]:
            skill_text += ' when matching {} or more colors'.format(min_attr)
            if max_mult > min_mult:
                skill_text += ' up to {}x at {} colors'.format(fmt_mult(max_mult), max_attr)
        elif attr == [0, 1, 2, 3, 4, 5]:
            skill_text += ' when matching {} or more colors ({}+heal)'.format(
                min_attr, min_attr - 1)
            if max_mult > min_mult:
                skill_text += ' up to {}x at 5 colors+heal'.format(
                    fmt_mult(max_mult), min_attr - 1)
        elif max_attr > min_attr and max_mult != min_mult:
            attr_text = self.attributes_format(attr)
            skill_text += ' when matchin {} of {} up to {}x when matching {}'.format(str(min_attr), attr_text, fmt_mult(max_mult), len(attr))
        elif min_attr == max_attr and len(attr) > min_attr:
            attr_text = self.attributes_format(attr)
            skill_text += ' when matching ' + str(min_attr) + '+ of {} at once'.format(attr_text)
        else:
            attr_text = self.attributes_format(attr)
            skill_text += ' when matching {} at once'.format(attr_text)

        return skill_text

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
        skill_text = fmt_mult(ls.multiplier) + 'x ATK additional damage when matching orbs'
        return skill_text

    def heal_on_convert(self, ls):
        skill_text = fmt_mult(ls.multiplier) + 'x RCV additional heal when matching orbs'
        return skill_text

    def resolve_convert(self, ls):
        skill_text = 'May survive when HP is reduced to 0 (HP>' + str(ls.threshold * 100).rstrip('0').rstrip('.') + '%)'
        return skill_text

    def bonus_time_convert(self, ls):
        skill_text = self.fmt_stats_type_attr_bonus(ls)

        if ls.time:
            if skill_text:
                skill_text += '; '

            skill_text += 'Increase orb movement time by ' + fmt_mult(ls.time) + ' seconds'

        return skill_text

    def counter_attack_convert(self, ls):
        attribute = self.ATTRIBUTES[ls.attributes[0]]
        if ls.chance == 1:
            skill_text = fmt_mult(ls.multiplier) + \
                         'x ' + attribute + ' counterattack'
        else:
            mult = str(ls.multiplier).rstrip('0').rstrip('.')
            skill_text = fmt_mult(
                ls.chance * 100) + '% chance to counterattack with ' + mult + 'x ' + attribute + ' damage'

        return skill_text

    def egg_drop_convert(self, ls):
        skill_text = fmt_mult(ls.multiplier) + 'x Egg Drop rate'
        return skill_text

    def coin_drop_convert(self, ls):
        skill_text = fmt_mult(ls.multiplier) + 'x Coin Drop rate'
        return skill_text

    def skill_used_convert(self, ls):
        skill_text = self.fmt_stats_type_attr_bonus(ls, skip_attr_all=True)
        skill_text += ' on the turn a skill is used'
        return skill_text

    def exact_combo_convert(self, ls):
        skill_text = fmt_mult(ls.atk) + 'x ATK when exactly ' + str(ls.combos) + ' combos'
        return skill_text

    def passive_stats_type_atk_all_hp_convert(self, ls):
        hp_pct = fmt_mult((1 - ls.hp) * 100)
        atk_mult = fmt_mult(ls.atk)
        skill_text = 'Reduce total HP by ' + hp_pct + '%; ' + atk_mult + 'x ATK for '
        for i in ls.types[:-1]:
            skill_text += self.TYPES[i] + ', '
        skill_text += self.TYPES[int(ls.types[-1])] + ' type'

        return skill_text

    def team_build_bonus_convert(self, ls):
        skill_text = self.fmt_stats_type_attr_bonus(ls)
        id_text = '[{}]'.format(', '.join(map(str, ls.monster_ids)))
        skill_text += ' if ' + id_text + ' is on the team'
        return skill_text

    def rank_exp_rate_convert(self, ls):
        skill_text = fmt_mult(ls.multiplier) + 'x Rank EXP'
        return skill_text

    def heart_tpa_stats_convert(self, ls):
        skill_text = fmt_mult(ls.rcv) + 'x RCV when matching 4 Heal orbs'
        return skill_text

    def five_orb_one_enhance_convert(self, ls):
        skill_text = fmt_mult(ls.atk) + 'x ATK for matched Att. when matching 5 Orbs with 1+ enhanced'
        return skill_text

    def heart_cross_convert(self, ls):
        skill_text = ''

        multiplier_text = self.fmt_multiplier_text(1, ls.atk, ls.rcv)
        if multiplier_text:
            skill_text += multiplier_text

        reduct_text = self.fmt_reduct_text(ls.shield)
        if reduct_text:
            skill_text += ' and ' + reduct_text if skill_text else reduct_text.capitalize()

        skill_text += ' when matching 5 Heal orbs in a cross formation'

        return skill_text

    def multi_play_convert(self, ls):
        skill_text = self.fmt_stats_type_attr_bonus(ls) + ' when in multiplayer mode'
        return skill_text

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
        if len(ls.crosses) == 1:
            skill_text = fmt_mult(ls.crosses[0].atk) + 'x ATK for each cross of 5 ' + \
                         self.ATTRIBUTES[ls.crosses[0].attribute] + ' orbs'

        else:
            skill_text = fmt_mult(ls.crosses[0].atk) + 'x ATK for each cross of 5 '
            for i in range(0, len(ls.crosses))[:-1]:
                skill_text += self.ATTRIBUTES[ls.crosses[i].attribute] + ', '
            skill_text += self.ATTRIBUTES[ls.crosses[-1].attribute] + ' orbs'

        return skill_text

    def minimum_orb_convert(self, ls):
        skill_text = self.fmt_stats_type_attr_bonus(ls)
        return skill_text

    def orb_remain_convert(self, ls):
        skill_text = self.fmt_stats_type_attr_bonus(ls, atk=ls.min_atk)
        if skill_text:
            skill_text += '; '

        if ls.base_atk not in [0, 1]:
            skill_text += fmt_mult(ls.base_atk) + 'x ATK when there are ' + \
                          str(ls.orb_count) + ' or fewer orbs remaining'
            if ls.bonus_atk != 0:
                skill_text += ' up to ' + fmt_mult(ls.atk) + 'x ATK when 0 orbs left'

        return skill_text

    def collab_bonus_convert(self, ls):
        COLLAB_MAP = {
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
            10001: 'Dragonbounds & Dragon Callers',
        }

        collab_id = ls.collab_id
        if collab_id not in COLLAB_MAP:
            print('Missing collab name for', collab_id)

        collab_name = COLLAB_MAP.get(collab_id, '<not populated>')
        skill_text = self.fmt_stats_type_attr_bonus(ls) + ' when all cards are from ' + collab_name

        return skill_text

    def multi_mass_match_convert(self, ls):
        if ls.atk not in [0, 1]:
            skill_text = self.fmt_multiplier_text(1, ls.atk, 1) + ' and increase '
        else:
            skill_text = 'Increase '
        skill_text += 'combo by {} when matching {} or more connected'.format(ls.bonus_combo, ls.min_match)
        skill_text += self.fmt_multi_attr(ls.attributes, conjunction='and') + ' orbs at once'

        return skill_text

    def l_match_convert(self, ls):
        mult_text = self.fmt_multiplier_text(1, ls.atk, ls.rcv)
        reduct_text = self.fmt_reduct_text(ls.shield)
        if mult_text:
            skill_text = mult_text
            if reduct_text:
                skill_text += ' and ' + reduct_text
        elif reduct_text:
            skill_text = mult_text
        else:
            skill_text = '???'
        skill_text += ' when matching 5' + self.fmt_multi_attr(ls.attributes) + ' orbs in L shape'
        return skill_text

    def add_combo_att_convert(self, ls):
        attr = ls.attributes
        min_attr = ls.min_attr

        if ls.atk not in [0, 1]:
            skill_text = self.fmt_multiplier_text(1, ls.atk, 1) + ' and increase combo by {}'.format(
                ls.bonus_combo)
        else:
            skill_text = 'Increase combo by {}'.format(ls.bonus_combo)
        if attr == [0, 1, 2, 3, 4]:
            skill_text += ' when matching {} or more colors'.format(min_attr)
        elif attr == [0, 1, 2, 3, 4, 5]:
            skill_text += ' when matching {} or more colors ({}+heal)'.format(min_attr,
                                                                              min_attr - 1)
        else:
            attr_text = self.attributes_format(attr)
            skill_text += ' when matching {} at once'.format(attr_text)

        return skill_text

    def orb_heal_convert(self, ls):
        skill_text = ''

        if ls.atk != 1 and ls.atk != 0:
            skill_text += self.fmt_multiplier_text(1, ls.atk, 1)

        if ls.shield != 0:
            reduct_text = self.fmt_reduct_text(ls.shield)
            if skill_text:
                if ls.unbind_amt == 0:
                    skill_text += ' and '
                else:
                    skill_text += ', '
                skill_text += reduct_text
            else:
                skill_text += reduct_text[0].upper() + reduct_text[1:]

        if ls.unbind_amt != 0:
            skill_text += ' and reduce' if skill_text else 'Reduce'
            skill_text += ' awoken skill binds by {} turns'.format(ls.unbind_amt)

        skill_text += ' when recovering more than {} HP from Heal orbs'.format(ls.heal_amt)

        return skill_text

    def rainbow_bonus_damage_convert(self, ls):
        skill_text = '{} additional damage'.format(ls.bonus_damage)

        attr = ls.attributes
        min_attr = ls.min_attr

        if attr == [0, 1, 2, 3, 4]:
            skill_text += ' when matching {} or more colors'.format(min_attr)
        elif attr == [0, 1, 2, 3, 4, 5]:
            skill_text += ' when matching {} or more colors ({}+heal)'.format(
                min_attr, min_attr - 1)
        elif min_attr == ls.max_attr and len(attr) > min_attr:
            attr_text = self.attributes_format(attr)
            skill_text += ' when matching ' + str(min_attr) + '+ of {} at once'.format(attr_text)
        else:
            attr_text = self.attributes_format(attr)
            skill_text += ' when matching {} at once'.format(attr_text)
        return skill_text

    def mass_match_bonus_damage_convert(self, ls):
        skill_text = '{} additional damage when matching {} or more'.format(ls.bonus_damage, ls.min_match)
        attr_text = self.fmt_multi_attr(ls.attributes)
        if attr_text:
            skill_text += '{} orbs'.format(attr_text)
        else:
            skill_text += ' orbs'

        return skill_text

    def taiko_convert(self, ls):
        return 'Turn orb sound effects into Taiko noises'
