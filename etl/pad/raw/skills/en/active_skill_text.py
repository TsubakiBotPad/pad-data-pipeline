from pad.raw.skills.en.skill_common import *
import logging

human_fix_logger = logging.getLogger('human_fix')

ROW_INDEX = {
    0: 'the top row',
    1: 'the 2nd row from the top',
    2: 'the middle row',
    3: 'the 2nd row from the bottom',
    4: 'the bottom row',
}

COLUMN_INDEX = {
    0: 'the far left column',
    1: 'the 2nd column from the left',
    2: 'the 3rd column from the left',
    3: 'the 3rd column from the right',
    4: 'the 2nd column from the right',
    5: 'the far right column',
}


class EnASTextConverter(EnBaseTextConverter):
    def fmt_repeated(self, text, amount):
        return '{} {:s}'.format(text, pluralize2('time', amount))

    def fmt_mass_atk(self, mass_attack):
        return 'all enemies' if mass_attack else 'an enemy'

    def fmt_duration(self, duration, max_duration=None):
        if max_duration and duration != max_duration:
            return 'For {}~{:s}, '.format(duration, pluralize2('turn', max_duration))
        else:
            return 'For {:s}, '.format(pluralize2('turn', duration))

    def attr_nuke_convert(self, act):
        return 'Deal ' + fmt_mult(act.multiplier) + 'x ATK ' + self.ATTRIBUTES[int(
            act.attribute)] + ' damage to ' + self.fmt_mass_atk(act.mass_attack)

    def fixed_attr_nuke_convert(self, act):
        return 'Deal ' + '{:,}'.format(act.damage) + ' ' + self.ATTRIBUTES[int(
            act.attribute)] + ' damage to ' + self.fmt_mass_atk(act.mass_attack)

    def self_att_nuke_convert(self, act):
        return 'Deal ' + fmt_mult(act.multiplier) + \
               'x ATK damage to ' + self.fmt_mass_atk(act.mass_attack)

    def shield_convert(self, act):
        return self.fmt_duration(act.duration) + self.fmt_reduct_text(act.shield)

    def elemental_shield_convert(self, act):
        skill_text = self.fmt_duration(act.duration)
        if act.shield == 1:
            skill_text += 'void all ' + self.ATTRIBUTES[int(act.attribute)] + ' damage'
        else:
            skill_text += 'reduce ' + \
                          self.ATTRIBUTES[int(act.attribute)] + ' damage by ' + \
                          fmt_mult(act.shield * 100) + '%'
        return skill_text

    def drain_attack_convert(self, act):
        skill_text = 'Deal ' + \
                     fmt_mult(act.atk_multiplier) + 'x ATK damage to ' + self.fmt_mass_atk(act.mass_attack)
        if act.recover_multiplier == 1:
            skill_text += ' and recover the same amount as HP'
        else:
            skill_text += ' and recover ' + \
                          fmt_mult(act.recover_multiplier * 100) + '% of the damage as HP'
        return skill_text

    def poison_convert(self, act):
        return 'Poison all enemies (' + fmt_mult(act.multiplier) + 'x ATK)'

    def ctw_convert(self, act):
        return 'Freely move orbs for {:s}'.format(pluralize2('second', act.duration))

    def gravity_convert(self, act):
        return 'Reduce enemies\' remaining HP by ' + fmt_mult(act.percentage_hp * 100) + '%'

    def heal_active_convert(self, act):
        hp = getattr(act, 'hp', 0)
        rcv_mult = getattr(act, 'rcv_multiplier_as_hp', 0)
        php = getattr(act, 'percentage_max_hp', 0)
        trcv_mult = getattr(act, 'team_rcv_multiplier_as_hp', 0)
        unbind = getattr(act, 'card_bind', 0)
        awoken_unbind = getattr(act, 'awoken_bind', 0)

        skill_text = ('Recover ' + '{:,}'.format(hp) + ' HP' if hp != 0 else
                      ('Recover ' + fmt_mult(rcv_mult) + 'x RCV as HP' if rcv_mult != 0 else
                       ('Recover all HP' if php == 1 else
                        ('Recover ' + fmt_mult(php * 100) + '% of max HP' if php > 0 else
                         ('Recover HP equal to ' + fmt_mult(trcv_mult) + 'x team\'s total RCV' if trcv_mult > 0 else
                          '')))))

        if unbind or awoken_unbind:
            if skill_text:
                skill_text += '; '
            skill_text += ('Remove all binds and awoken skill binds' if (unbind >= 9999 and awoken_unbind) else
                           ('Reduce binds and awoken skill binds by {:s}'.format(pluralize2('turn', awoken_unbind)) if (
                                   unbind and awoken_unbind) else
                            ('Remove all binds' if unbind >= 9999 else
                             ('Reduce binds by {:s}'.format(pluralize2('turn', unbind)) if unbind else
                              ('Remove all awoken skill binds' if awoken_unbind >= 9999 else
                               ('Reduce awoken skill binds by {:s}'.format(pluralize2('turn', awoken_unbind))))))))
        return skill_text

    def delay_convert(self, act):
        return 'Delay enemies\' next attack by {:s}'.format(pluralize2('turn', act.turns))

    def defense_reduction_convert(self, act):
        return self.fmt_duration(act.duration) + \
               'reduce enemies\' defense by ' + fmt_mult(act.shield * 100) + '%'

    def double_orb_convert(self, act):
        if len(act.to_attr) == 1:
            skill_text = 'Change {} and {} orbs to {} orbs'.format(self.ATTRIBUTES[int(act.from_attr[0])],
                                                                   self.ATTRIBUTES[int(act.from_attr[1])],
                                                                   self.ATTRIBUTES[int(act.to_attr[0])])
        else:
            skill_text = 'Change {} orbs to {} orbs; Change {} orbs to {} orbs'.format(
                self.ATTRIBUTES[int(act.from_attr[0])],
                self.ATTRIBUTES[int(act.to_attr[0])],
                self.ATTRIBUTES[int(act.from_attr[1])],
                self.ATTRIBUTES[int(act.to_attr[1])])

        return skill_text

    def damage_to_att_enemy_convert(self, act):
        return 'Deal ' + '{:,}'.format(act.damage) + ' ' + self.ATTRIBUTES[int(
            act.attack_attribute)] + ' damage to all ' + self.ATTRIBUTES[int(act.enemy_attribute)] + ' Att. enemies'

    def rcv_boost_convert(self, act):
        return self.fmt_duration(act.duration) + fmt_mult(act.multiplier) + 'x RCV'

    def attribute_attack_boost_convert(self, act):
        skill_text = ''
        if act.rcv_boost:
            skill_text += self.fmt_duration(act.duration) + fmt_mult(act.multiplier) + 'x RCV'
        if skill_text:
            skill_text += '; '
        skill_text += self.fmt_duration(act.duration) + self.fmt_stats_type_attr_bonus(act, atk=act.multiplier)
        return skill_text

    def mass_attack_convert(self, act):
        return self.fmt_duration(act.duration) + 'all attacks become mass attack'

    def enhance_convert(self, act):
        for_attr = act.orbs
        skill_text = ''

        if for_attr:
            if not len(for_attr) == 6:
                color_text = self.concat_list_and([self.ATTRIBUTES[i] for i in for_attr])
                skill_text = 'Enhance all ' + color_text + ' orbs'
            else:
                skill_text = 'Enhance all orbs'
        return skill_text

    def lock_convert(self, act):
        for_attr = act.orbs
        amount_text = 'all' if act.count >= 42 else str(act.count)
        color_text = '' if len(for_attr) == 10 else self.attributes_to_str(for_attr)
        result = 'Lock {} {} orbs'.format(amount_text, color_text)
        return ' '.join(result.split())

    def laser_convert(self, act):
        return 'Deal ' + '{:,}'.format(act.damage) + \
               ' fixed damage to ' + self.fmt_mass_atk(act.mass_attack)

    def no_skyfall_convert(self, act):
        return self.fmt_duration(act.duration) + 'no skyfall'

    def enhance_skyfall_convert(self, act):
        return self.fmt_duration(act.duration) + 'enhanced orbs are more likely to appear by ' + \
               fmt_mult(act.percentage_increase * 100) + '%'

    def auto_heal_convert(self, act):
        skill_text = ''
        unbind = act.card_bind
        awoken_unbind = act.awoken_bind
        if act.duration:
            skill_text += self.fmt_duration(act.duration) + 'recover ' + \
                          fmt_mult(act.percentage_max_hp * 100) + '% of max HP'
        if unbind or awoken_unbind:
            if skill_text:
                skill_text += '; '
            skill_text += ('Remove all binds and awoken skill binds' if (unbind >= 9999 and awoken_unbind) else
                           ('Reduce binds and awoken skill binds by {:s}'.format(pluralize2('turn', awoken_unbind)) if (
                                   unbind and awoken_unbind) else
                            ('Remove all binds' if unbind >= 9999 else
                             ('Reduce binds by {:s}'.format(pluralize2('turn', unbind)) if unbind else
                              ('Remove all awoken skill binds' if awoken_unbind >= 9999 else
                               ('Reduce awoken skill binds by {:s}'.format(pluralize2('turn', awoken_unbind))))))))

        return skill_text

    def absorb_mechanic_void_convert(self, act):
        if act.attribute_absorb and act.damage_absorb:
            return self.fmt_duration(act.duration) + \
                   'bypass damage absorb shield and att. absorb shield effects'
        elif act.attribute_absorb and not act.damage_absorb:
            return self.fmt_duration(act.duration) + 'bypass att. absorb shield effects'
        elif not act.attribute_absorb and act.damage_absorb:
            return self.fmt_duration(act.duration) + 'bypass damage absorb shield effects'
        else:
            return None

    def void_mechanic_convert(self, act):
        return self.fmt_duration(act.duration) + 'bypass void damage shield effects'

    def true_gravity_convert(self, act):
        return 'Deal damage equal to ' + \
               fmt_mult(act.percentage_max_hp * 100) + '% of enemies\' max HP'

    def extra_combo_convert(self, act):
        return self.fmt_duration(act.duration) + \
               'increase combo count by ' + str(act.combos)

    def awakening_heal_convert(self, act):
        skill_text = 'Heal {:d}x RCV for each '.format(int(act.amount_per))
        awakens = [self.AWAKENING_MAP[a] for a in act.awakenings]
        skill_text += self.concat_list_and(filter(None, awakens))
        skill_text += ' awakening skill on the team'
        return skill_text

    def awakening_attack_boost_convert(self, act):
        skill_text = self.fmt_duration(act.duration) + 'increase ATK by ' + \
                     fmt_mult(act.amount_per * 100) + '% for each '
        awakens = [self.AWAKENING_MAP[a] for a in act.awakenings]
        skill_text += self.concat_list_and(filter(None, awakens))
        skill_text += ' awakening skill on the team'
        return skill_text

    def awakening_shield_convert(self, act):
        skill_text = self.fmt_duration(act.duration) + 'reduce damage taken by ' + \
                     fmt_mult(act.amount_per * 100) + '% for each '
        awakens = [self.AWAKENING_MAP[a] for a in act.awakenings]
        skill_text += self.concat_list_and(filter(None, awakens))
        skill_text += ' awakening skill on the team'
        return skill_text

    def change_enemies_attribute_convert(self, act):
        return 'Change all enemies to ' + self.ATTRIBUTES[act.attribute] + ' Att.'

    def haste_convert(self, act):
        return 'Charge all allies\' skills by {:s}'.format(pluralize2('turn', act.turns, act.max_turns))

    def random_orb_change_convert(self, act):
        from_attr = act.from_attr
        to_attr = act.to_attr
        skill_text = 'Change '
        if from_attr == self.ALL_ATTRS:
            skill_text += 'all orbs to '
        else:
            skill_text += self.concat_list_and([self.ATTRIBUTES[i] for i in from_attr]) + ' orbs to '
        skill_text += self.concat_list_and([self.ATTRIBUTES[i] for i in to_attr]) + ' orbs'
        return skill_text

    def attack_attr_x_team_atk_convert(self, act):
        skill_text = 'Deal ' + self.ATTRIBUTES[act.attack_attribute] + \
                     ' damage equal to ' + fmt_mult(act.multiplier) + 'x of team\'s total '
        skill_text += self.concat_list_and([self.ATTRIBUTES[a] for a in act.team_attributes]) + ' ATK to '
        skill_text += self.fmt_mass_atk(act.mass_attack)
        return skill_text

    def spawn_orb_convert(self, act):
        skill_text = 'Create {} '.format(act.amount)
        skill_text += self.concat_list_and([self.ATTRIBUTES[o] for o in act.orbs])
        skill_text += ' ' + pluralize('orb', act.amount)
        if act.orbs != act.excluding_orbs and act.excluding_orbs != []:
            templist = set(act.excluding_orbs) - set(act.orbs)
            skill_text += ' over non '
            skill_text += self.concat_list_and([self.ATTRIBUTES[o] for o in templist]) + ' orbs'
        elif len(act.excluding_orbs) == 0:
            skill_text += ' over any ' + pluralize('orb', act.amount)
        return skill_text

    def double_spawn_orb_convert(self, act):
        skill_text = self.spawn_orb_convert(act)
        skill_text += ', and create {} '.format(act.amount2)
        skill_text += self.concat_list_and([self.ATTRIBUTES[o] for o in act.orbs2])
        skill_text += ' ' + pluralize('orb', act.amount2)
        if act.orbs != act.excluding_orbs2 and act.excluding_orbs2 != []:
            templist = set(act.excluding_orbs2) - set(act.orbs2)
            skill_text += ' over non '
            skill_text += self.concat_list_and([self.ATTRIBUTES[o] for o in templist]) + ' orbs'
        elif len(act.excluding_orbs2) == 0:
            skill_text += ' over any ' + pluralize('orb', act.amount2)
        return skill_text

    def move_time_buff_convert(self, act):
        if act.static == 0:
            return self.fmt_duration(act.duration) + \
                   fmt_mult(act.percentage) + 'x orb move time'
        elif act.percentage == 0:
            return self.fmt_duration(act.duration) + \
                   'increase orb move time by {:s}'.format(pluralize2('second', fmt_mult(act.static)))
        raise ValueError()

    def row_change_convert(self, act):
        return self._line_change_convert(act.rows, ROW_INDEX)

    def column_change_convert(self, act):
        return self._line_change_convert(act.columns, COLUMN_INDEX)

    def _line_change_convert(self, lines, index):
        skill_text = []
        # TODO: simplify this
        lines = [(index[line.index], self.attributes_to_str(line.attrs)) for line in lines]
        skip = 0
        for c, line in enumerate(lines):
            if skip:
                skip -= 1
                continue
            elif c == len(lines) - 1 or lines[c + 1][1] != line[1]:
                skill_text.append('change {} to {} orbs'.format(*line))
            else:
                while c + skip < len(lines) and lines[c + skip][1] == line[1]:
                    skip += 1
                formatted = ' and '.join(map(lambda l: l[0], lines[c:c + skip]))
                skill_text.append("change {} to {} orbs".format(formatted, line[1]))
                skip -= 1
        return capitalize_first(' and '.join(skill_text))

    def change_skyfall_convert(self, act):
        skill_text = self.fmt_duration(act.duration, act.max_duration)
        rate = fmt_mult(act.percentage * 100)

        if rate == '100':
            skill_text += 'only {} orbs will appear'.format(self.concat_list_and(self.ATTRIBUTES[i] for i in act.orbs))
        else:
            skill_text += '{} orbs are more likely to appear by {}%'.format(
                self.concat_list_and(self.ATTRIBUTES[i] for i in act.orbs),
                rate)
        return skill_text

    def random_nuke_convert(self, act):
        if act.minimum_multiplier != act.maximum_multiplier:
            return 'Randomized ' + self.ATTRIBUTES[act.attribute] + ' damage to ' + self.fmt_mass_atk(
                act.mass_attack) + '(' + fmt_mult(act.minimum_multiplier) + '~' + fmt_mult(
                act.maximum_multiplier) + 'x)'
        else:
            return 'Deal ' + fmt_mult(act.maximum_multiplier) + 'x ' + \
                   self.ATTRIBUTES[act.attribute] + ' damage to ' + self.fmt_mass_atk(act.mass_attack)

    def counterattack_convert(self, act):
        return self.fmt_duration(act.duration) + fmt_mult(act.multiplier) + \
               'x ' + self.ATTRIBUTES[act.attribute] + ' counterattack'

    def board_change_convert(self, act):
        skill_text = 'Change all orbs to '
        skill_text += self.concat_list_and([self.ATTRIBUTES[a] for a in act.to_attr]) + ' orbs'
        return skill_text

    def suicide_random_nuke_convert(self, act):
        skill_text = self.suicide_convert(act) + '; '
        skill_text += 'Deal ' + minmax(act.maximum_multiplier, act.minimum_multiplier, fmt=True) \
                      + 'x ' + self.ATTRIBUTES[act.attribute] + ' damage to ' + self.fmt_mass_atk(act.mass_attack)
        return skill_text

    def suicide_nuke_convert(self, act):
        skill_text = self.suicide_convert(act) + '; '
        skill_text += 'Deal ' + '{:,}'.format(act.damage) + ' ' + self.ATTRIBUTES[
            act.attribute] + ' damage to ' + self.fmt_mass_atk(
            act.mass_attack)
        return skill_text

    def suicide_convert(self, act):
        if act.hp_remaining == 0:
            return 'Reduce HP to 1'
        else:
            return 'Reduce HP by ' + fmt_mult((1 - act.hp_remaining) * 100) + '%'

    def type_attack_boost_convert(self, act):
        skill_text = self.fmt_duration(act.duration) + fmt_mult(act.multiplier) + 'x ATK for '
        skill_text += self.concat_list_and([self.TYPES[t] for t in act.types]) + ' '
        skill_text += pluralize('type', len(act.types))
        return skill_text

    def grudge_strike_convert(self, act):
        skill_text = 'Deal ' + self.ATTRIBUTES[act.attribute] + ' damage to ' + self.fmt_mass_atk(
            act.mass_attack) + ' depending on HP level (' + fmt_mult(
            act.low_multiplier) + 'x at 1 HP and ' + fmt_mult(act.high_multiplier) + 'x at 100% HP)'
        return skill_text

    def drain_attr_attack_convert(self, act):
        skill_text = 'Deal ' + fmt_mult(act.atk_multiplier) + 'x ATK ' + \
                     self.ATTRIBUTES[act.attribute] + ' damage to ' + self.fmt_mass_atk(act.mass_attack)
        if act.recover_multiplier == 1:
            skill_text += ' and recover the amount as HP'
        else:
            skill_text += ' and recover ' + \
                          fmt_mult(act.recover_multiplier * 100) + '% of the damage as HP'
        return skill_text

    def attribute_change_convert(self, act):
        return 'Change own Att. to ' + \
               self.ATTRIBUTES[act.attribute] + ' for ' + str(act.duration) + ' turns'

    def multi_hit_laser_convert(self, act):
        return 'Deal ' + '{:,}'.format(act.damage) + ' damage to ' + \
               self.fmt_mass_atk(act.mass_attack)

    def hp_nuke_convert(self, act):
        return "Deal {} damage equal to {}x of team's total HP to {}".format(self.ATTRIBUTES[act.attribute],
                                                                             fmt_mult(act.multiplier),
                                                                             self.fmt_mass_atk(act.mass_attack))

    def fixed_pos_convert(self, act):
        board = [
            list(act.row_pos_1),
            list(act.row_pos_2),
            list(act.row_pos_3),
            list(act.row_pos_4),
            list(act.row_pos_5),
        ]

        orb_count = 0

        output = []
        for row_num in board:
            orb_count += len(row_num)

        board_repr = []
        for row in board:
            board_repr.append(''.join(['0' if n in row else 'X'
                                       for n in range(6)]))
        board_repr = '\n'.join(board_repr)

        skill_text = ''
        if orb_count == 0 or set(sum(board, [])) - {0, 1, 2, 3, 4, 5}:
            return ''
        if orb_count == 4:
            if len(board[0]) == len(board[4]) == 2:
                skill_text += 'Create 4 {} orbs at the corners of the board'.format(
                    self.ATTRIBUTES[act.attribute])
        if not (orb_count % 5):
            for row_num in range(1, len(board) - 1):  # Check for cross
                if len(board[row_num]) == 3 and len(board[row_num - 1]) == \
                        len(board[row_num + 1]) == 1:  # Check for cross
                    row_pos = row_num
                    col_pos = board[row_num][1]
                    shape = 'cross'
                    result = (shape, row_pos, col_pos)
                    output.append(result)
                    del board[row_num][1]
            for row_num in range(0, len(board)):  # Check for L
                if len(board[row_num]) == 3:
                    row_pos = row_num
                    if row_num < 2:
                        col_pos = board[row_num + 1][0]
                        del board[row_num + 1][0]
                    elif row_num > 2:
                        col_pos = board[row_num - 1][0]
                        del board[row_num - 1][0]
                    elif len(board[row_num + 1]) > 0:
                        col_pos = board[row_num + 1][0]
                        del board[row_num + 1][0]
                    else:
                        col_pos = board[row_num - 1][0]
                        del board[row_num - 1][0]

                    shape = 'L shape'
                    result = (shape, row_pos, col_pos)
                    output.append(result)

        if not (orb_count % 9):
            for row_num in range(1, len(board) - 1):  # Check for square
                if len(board[row_num]) == len(board[row_num - 1]) == len(board[row_num + 1]) == 3:
                    row_pos = row_num
                    col_pos = board[row_num][1]
                    shape = 'square'
                    result = (shape, row_pos, col_pos)
                    output.append(result)
                    del board[row_num][1]

        if orb_count == 7:  # TODO: Find a way to cover special cases
            if board == [[3, 4, 5], [3, 5], [5], [5], []]:
                return 'Create a 7-shape of {} orbs in the upper right corner'.format(self.ATTRIBUTES[act.attribute])
        if orb_count == 6:
            if board == [[0, 1, 2], [0, 1, 2], [], [], []]:
                return 'Create a 3x2 rectangle of {} orbs in the upper left corner'.format(
                    self.ATTRIBUTES[act.attribute])

        if orb_count == 18:
            if len(board[0]) == len(board[4]) == len(board[1]) + len(board[2]) + len(board[3]) == 6:
                skill_text += 'Change the outermost orbs of the board to {} orbs'.format(
                    self.ATTRIBUTES[act.attribute])

        if output:
            for entry in output:
                if skill_text:
                    skill_text += '; '
                skill_text += 'Create {} of {} orbs with its center at {} and {}'.format(indef_article(entry[0]),
                                                                                         self.ATTRIBUTES[act.attribute],
                                                                                         ROW_INDEX[entry[1]],
                                                                                         COLUMN_INDEX[entry[2]])

        if not skill_text:
            human_fix_logger.error(
                'Unknown board shape in {} ({}):\n{} \n{}'.format(
                    act.name, act.skill_id, act.raw_description, board_repr))

        return skill_text

    def match_disable_convert(self, act):
        return 'Reduce unable to match orbs effect by {:s}'.format(pluralize2('turn', act.duration))

    def board_refresh(self, act):
        return 'Replace all orbs'

    def leader_swap(self, act):
        return 'Becomes Team leader; changes back when used again'

    def unlock_all_orbs(self, act):
        return 'Unlock all orbs'

    def unlock_board_path_toragon(self, act):
        return 'Unlock all orbs; Change all orbs to Fire, Water, Wood, and Light orbs; Show path to 3 combos'

    def random_skill(self, act):
        random_skills_text = []
        for idx, s in enumerate(act.random_skills, 1):
            random_skills_text.append('{}) {}'.format(idx, s.full_text(self)))
        return 'Activate a random skill from the list: {}'.format(self.concat_list_and(random_skills_text))

    def change_monster(self, act):
        return "Changes to [{}] for the duration of the dungeon".format(act.change_to)

    def skyfall_lock(self, act):
        attrs = self.attributes_to_str(act.orbs) if act.orbs else 'all'
        return self.fmt_duration(act.duration) + attrs + " orbs appear locked"

    def spawn_spinner(self, turns: int, speed: float, count: int):
        return 'Random {:d} orbs change every {:.1f}s for {:s}' \
            .format(count, speed, pluralize2('turn', turns))

    def ally_active_disable(self, turns: int):
        return 'Disable team active skills for {:s}'.format(pluralize2('turn', turns))

    def ally_active_delay(self, turns: int):
        return 'Delay team active skills by {:s}'.format(pluralize2('turn', turns))

    def create_unmatchable(self, act):
        skill_text = self.fmt_duration(act.duration)
        if act.orbs:
            skill_text += " " +self.concat_list_and(self.ATTRIBUTES[i] for i in act.orbs)
        return skill_text + " orbs are unmatchable."

    def two_part_active(self, strs):
        return '; '.join(strs)


__all__ = ['EnASTextConverter']
