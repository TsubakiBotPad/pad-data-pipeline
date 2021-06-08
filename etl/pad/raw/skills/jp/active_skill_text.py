from pad.raw.skills.jp.skill_common import *

def fmt_mult(x):
    return str(round(float(x), 2)).rstrip('0').rstrip('.')


ROW_INDEX = {
    0: '最上段',
    1: '上から2行目',
    2: '上から3行目',
    3: '下から2行目',
    4: '最下段',
}

COLUMN_INDEX = {
    0: '最左端',
    1: '左から2列目',
    2: '左から3列目',
    3: '右から3列目',
    4: '右から2列目',
    5: '最右端',
}


def half_to_full(n):
    o = ''
    c = '０１２３４５６７８９'
    for num in str(n):
        o += c[int(num)]
    return o


class JpASTextConverter(JpBaseTextConverter):
    def fmt_repeated(self, text, amount):
        return '{}ｘ{}回'.format(text, amount)

    def fmt_mass_atk(self, mass_attack):
        return '敵全体' if mass_attack else '敵1体'

    def fmt_duration(self, duration, max_duration=None):
        if max_duration and duration != max_duration:
            return '{}~{}ターンの間、'.format(duration, max_duration)
        else:
            return '{}ターンの間、'.format(duration)

    def attr_nuke_convert(self, act):
        return '{}に攻撃力ｘ{}倍の{}属性攻撃'.format(
            self.fmt_mass_atk(act.mass_attack), fmt_mult(act.multiplier), self.ATTRIBUTES[int(act.attribute)])

    def fixed_attr_nuke_convert(self, act):
        return '{}に{}の{}属性攻撃'.format(
            self.fmt_mass_atk(act.mass_attack), self.big_number(act.damage), self.ATTRIBUTES[int(act.attribute)])

    def self_att_nuke_convert(self, act):
        return '{}に攻撃力ｘ{}倍攻撃'.format(self.fmt_mass_atk(act.mass_attack), fmt_mult(act.multiplier))

    def shield_convert(self, act):
        return self.fmt_duration(act.duration) + self.fmt_reduct_text(act.shield)

    def elemental_shield_convert(self, act):
        if act.shield == 1:
            return '{}ターンの間、{}属性の攻撃を無効化'.format(
                act.duration, self.attributes_to_str([int(act.attribute)]))
        else:
            return '{}ターンの間、{}属性のダメージを{}％減少'.format(
                act.duration, self.attributes_to_str([int(act.attribute)]), fmt_mult(act.shield * 100))

    def drain_attack_convert(self, act):
        skill_text = '{}に攻撃力ｘ{}倍で攻撃し、ダメージ'.format(self.fmt_mass_atk(act.mass_attack), fmt_mult(act.atk_multiplier))
        if act.recover_multiplier == 1:
            skill_text += '分のHP回復'
        else:
            skill_text += '{}％分のHP回復'.format(fmt_mult(act.recover_multiplier * 100))
        return skill_text

    def poison_convert(self, act):
        return '敵全体を毒にする（攻撃力ｘ{}倍）'.format(fmt_mult(act.multiplier))

    def ctw_convert(self, act):
        return '{}秒間、時を止めてドロップを動かせる'.format(act.duration)

    def gravity_convert(self, act):
        return '敵の現HPの{}％分のダメージ'.format(fmt_mult(act.percentage_hp * 100))

    def heal_active_convert(self, act):
        hp = getattr(act, 'hp', 0)
        rcv_mult = getattr(act, 'rcv_multiplier_as_hp', 0)
        php = getattr(act, 'percentage_max_hp', 0)
        trcv_mult = getattr(act, 'team_rcv_multiplier_as_hp', 0)
        unbind = getattr(act, 'card_bind', 0)
        awoken_unbind = getattr(act, 'awoken_bind', 0)

        skill_text = ('HPを{}回復'.format(self.big_number(hp)) if hp != 0 else
                      ('回復力ｘ{}倍のHPを回復'.format(fmt_mult(rcv_mult)) if rcv_mult != 0 else
                       ('HPを全回復' if php == 1 else
                        ('最大HP{}％分回復'.format(fmt_mult(php * 100)) if php > 0 else
                         ('チームの総回復力ｘ{}倍のHPを回復'.format(fmt_mult(trcv_mult)) if trcv_mult > 0 else
                          (''))))))

        if unbind or awoken_unbind:
            if skill_text:
                skill_text += '。'
            skill_text += ('バインドと覚醒無効を全回復' if unbind >= 9999 and awoken_unbind else
                           ('バインドと覚醒無効を{}ターン回復'.format(awoken_unbind) if unbind and awoken_unbind else
                            ('バインドを全回復' if unbind >= 9999 else
                             ('バインドを{}ターン回復'.format(unbind) if unbind else
                              ('覚醒無効を全回復' if awoken_unbind >= 9999 else
                               ('覚醒無効を{}ターン回復'.format(awoken_unbind)))))))
        return skill_text

    def delay_convert(self, act):
        return '敵の行動を{}ターン遅らせる'.format(act.turns)

    def defense_reduction_convert(self, act):
        return '{}ターンの間、敵の防御力が{}％下がる'.format(act.duration, fmt_mult(act.shield * 100))

    def double_orb_convert(self, act):
        if len(act.to_attr) == 1:
            skill_text = '{}と{}ドロップを{}ドロップに変化'.format(
                self.ATTRIBUTES[int(act.from_attr[0])],
                self.ATTRIBUTES[int(act.from_attr[1])],
                self.ATTRIBUTES[int(act.to_attr[0])])
        else:
            skill_text = '{}ドロップを{}ドロップに、{}ドロップを{}ドロップに変化'.format(
                self.ATTRIBUTES[int(act.from_attr[0])],
                self.ATTRIBUTES[int(act.to_attr[0])],
                self.ATTRIBUTES[int(act.from_attr[1])],
                self.ATTRIBUTES[int(act.to_attr[1])])

        return skill_text

    def damage_to_att_enemy_convert(self, act):
        return '{}属性の敵に{}属性の{}ダメージ'.format(
            self.ATTRIBUTES[int(act.enemy_attribute)],
            self.ATTRIBUTES[int(act.attack_attribute)],
            act.damage)

    def rcv_boost_convert(self, act):
        return '{}ターンの間、回復力が{}倍'.format(act.duration, fmt_mult(act.multiplier))

    def attribute_attack_boost_convert(self, act):
        skill_text = ''
        if act.rcv_boost:
            skill_text += self.rcv_boost_convert(act) + '。'
        skill_text += self.fmt_duration(act.duration) + self.fmt_stats_type_attr_bonus(act, atk=act.multiplier)
        return skill_text

    def mass_attack_convert(self, act):
        return '{}ターンの間、攻撃が全体攻撃になる'.format(act.duration)

    def enhance_convert(self, act):
        for_attr = act.orbs
        skill_text = ''

        if for_attr:
            if not len(for_attr) == 6:
                skill_text = '{}ドロップを強化'.format(self.attributes_to_str(for_attr))
            else:
                skill_text = '全ドロップを強化'
        return skill_text

    def lock_convert(self, act):
        for_attr = act.orbs
        amount_text = '全' if act.count >= 42 else 'ランダムで{}個'.format(act.count)
        color_text = '' if len(for_attr) == 10 else self.attributes_to_str(for_attr)
        return '{}{}ドロップをロック'.format(amount_text, color_text)

    def laser_convert(self, act):
        return '{}に{}の固定ダメージ'.format(
            self.fmt_mass_atk(act.mass_attack), self.big_number(act.damage))

    def no_skyfall_convert(self, act):
        return '{}ターンの間、落ちコンしなくなる'.format(act.duration)

    def enhance_skyfall_convert(self, act):
        return '{}ターンの間、強化ドロップを{}％の確率で落ちてくる'.format(
            act.duration, fmt_mult(act.percentage_increase * 100))

    def auto_heal_convert(self, act):
        skill_text = ''
        unbind = act.card_bind
        awoken_unbind = act.awoken_bind
        if act.duration:
            skill_text += '{}ターンの間、最大HPの{}％分回復'.format(
                act.duration, fmt_mult(act.percentage_max_hp * 100))
        if unbind or awoken_unbind:
            if skill_text:
                skill_text += '。'
            skill_text += ('バインドと覚醒無効を全回復' if unbind >= 9999 and awoken_unbind else
                           ('バインドと覚醒無効を{}ターン回復'.format(awoken_unbind) if unbind and awoken_unbind else
                            ('バインドを全回復' if unbind >= 9999 else
                             ('バインドを{}ターン回復'.format(unbind) if unbind else
                              ('覚醒無効を全回復' if awoken_unbind >= 9999 else
                               ('覚醒無効を{}ターン回復'.format(awoken_unbind)))))))
        return skill_text

    def absorb_mechanic_void_convert(self, act):
        if act.attribute_absorb and act.damage_absorb:
            return self.fmt_duration(act.duration) + 'ダメージ吸収と属性吸収を無効化する'
        elif act.attribute_absorb and not act.damage_absorb:
            return self.fmt_duration(act.duration) + '属性吸収を無効化する'
        elif not act.attribute_absorb and act.damage_absorb:
            return self.fmt_duration(act.duration) + 'ダメージ吸収を無効化する'
        else:
            return ''

    def void_mechanic_convert(self, act):
        return self.fmt_duration(act.duration) + 'ダメージ無効を貫通する'

    def true_gravity_convert(self, act):
        return '敵の最大HPの{}％分のダメージ'.format(fmt_mult(act.percentage_max_hp * 100))

    def extra_combo_convert(self, act):
        return self.fmt_duration(act.duration) + '{}コンボ加算される'.format(act.combos)

    def awakening_heal_convert(self, act):
        skill_text = 'チーム内の'
        awakens = [self.AWAKENING_MAP[a] for a in act.awakenings]
        skill_text += self.concat_list_and(filter(None, awakens))
        skill_text += 'の覚醒数1つにつき回復力ｘ{}倍をHP回復'.format(act.amount_per)
        return skill_text

    def awakening_attack_boost_convert(self, act):
        skill_text = self.fmt_duration(act.duration) + 'チーム内の'
        awakens = [self.AWAKENING_MAP[a] for a in act.awakenings]
        skill_text += self.concat_list_and(filter(None, awakens))
        skill_text += 'の覚醒数1つにつき攻撃力が{}％上がる'.format(fmt_mult(act.amount_per * 100))
        return skill_text

    def awakening_shield_convert(self, act):
        skill_text = self.fmt_duration(act.duration) + 'チーム内の'
        awakens = [self.AWAKENING_MAP[a] for a in act.awakenings]
        skill_text += self.concat_list_and(filter(None, awakens))
        skill_text += 'の覚醒数1つにつき受けるダメージを{}％減少'.format(fmt_mult(act.amount_per * 100))
        return skill_text

    def change_enemies_attribute_convert(self, act):
        return '敵全体が{}属性に変化'.format(self.ATTRIBUTES[act.attribute])

    def haste_convert(self, act):
        return '自分以外の味方スキルが{}ターンの溜まる'.format(minmax(act.turns, act.max_turns))

    def random_orb_change_convert(self, act):
        from_attr = act.from_attr
        to_attr = act.to_attr
        if from_attr == self.ALL_ATTRS:
            skill_text = '全'
        else:
            skill_text = self.attributes_to_str(from_attr)
        skill_text += 'ドロップを{}ドロップに変化'.format(self.attributes_to_str(to_attr))
        return skill_text

    def attack_attr_x_team_atk_convert(self, act):
        return '{}にチームの{}属性の総攻撃力ｘ{}倍の{}属性攻撃'.format(
            self.fmt_mass_atk(act.mass_attack),
            self.attributes_to_str(act.team_attributes),
            fmt_mult(act.multiplier),
            self.ATTRIBUTES[act.attack_attribute])

    def spawn_orb_convert(self, act):
        to_orbs = self.attributes_to_str(act.orbs)
        excl_orbs = self.attributes_to_str(set(act.excluding_orbs) - set(act.orbs))
        if act.orbs != act.excluding_orbs and act.excluding_orbs != []:
            if len(act.orbs) > 1:
                s_text = '{}以外ランダムで{}を{}個ずつ生成'
            else:
                s_text = '{}以外{}ドロップを{}個生成'
            return s_text.format(excl_orbs, to_orbs, act.amount)
        else:
            if len(act.orbs) > 1:
                s_text = 'ランダムで{}を{}個ずつ生成'
            else:
                s_text = '{}ドロップを{}個生成'
            return s_text.format(to_orbs, act.amount)

    def double_spawn_orb_convert(self, act):
        s_text = self.spawn_orb_convert(act) + "。"
        to_orbs = self.attributes_to_str(act.orbs2)
        excl_orbs = self.attributes_to_str(set(act.excluding_orbs2) - set(act.orbs2))
        if act.orbs2 != act.excluding_orbs2 and act.excluding_orbs2 != []:
            if len(act.orbs2) > 1:
                s_text += '{}以外ランダムで{}を{}個ずつ生成'
            else:
                s_text += '{}以外{}ドロップを{}個生成'
            return s_text.format(excl_orbs, to_orbs, act.amount2)
        else:
            if len(act.orbs2) > 1:
                s_text += 'ランダムで{}を{}個ずつ生成'
            else:
                s_text += '{}ドロップを{}個生成'
            return s_text.format(to_orbs, act.amount2)

    def move_time_buff_convert(self, act):
        s_text = self.fmt_duration(act.duration) + 'ドロップ操作時間が'
        if act.static == 0:
            return s_text + '{}倍'.format(fmt_mult(act.percentage))
        elif act.percentage == 0:
            return s_text + '{}秒に延長'.format(fmt_mult(act.static))
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
                skill_text.append('{}を{}に'.format(*line))
            else:
                while c + skip < len(lines) and lines[c + skip][1] == line[1]:
                    skip += 1
                formatted = 'と'.join(map(lambda x: x[0], lines[c:c + skip]))
                skill_text.append("{}を{}に".format(formatted, line[1]))
                skip -= 1
        output = '、'.join(skill_text)
        if output:
            output = output[:-1] + 'ドロップに変化'
        return output

    def change_skyfall_convert(self, act):
        skill_text = self.fmt_duration(act.duration, act.max_duration)
        rate = fmt_mult(act.percentage * 100)

        if rate == '100':
            skill_text += '{}ドロップのみ落ちてくる'.format(self.attributes_to_str(act.orbs))
        else:
            if all(map(lambda x: x in list(range(6)), act.orbs)):
                skill_text += '{}ドロップが{}％落ちやすくなる'.format(self.attributes_to_str(act.orbs), rate)
            else:
                skill_text += '{}が{}％の確率で落ちてくる'.format(self.attributes_to_str(act.orbs), rate)
        return skill_text

    def no_orb_skyfall_convert(self, act):
        skill_text = self.fmt_duration(act.duration)
        skill_text += 'no {} orbs will appear'.format(self.concat_list_and(self.ATTRIBUTES[i] for i in act.orbs))
        return skill_text

    def random_nuke_convert(self, act):
        return '{}に攻撃力ｘ{}倍の{}属性攻撃'.format(
            self.fmt_mass_atk(act.mass_attack),
            minmax(fmt_mult(act.minimum_multiplier), fmt_mult(act.maximum_multiplier)),
            self.ATTRIBUTES[act.attribute])

    def counterattack_convert(self, act):
        return '{}ターンの間、受けたダメージｘ{}倍の{}属性反撃'.format(
            act.duration, fmt_mult(act.multiplier), self.ATTRIBUTES[act.attribute])

    def board_change_convert(self, act):
        return '全ドロップを{}ドロップに変化'.format(self.attributes_to_str(act.to_attr))

    def suicide_random_nuke_convert(self, act):
        return self.suicide_convert(act) + '。' + self.random_nuke_convert(act)

    def suicide_nuke_convert(self, act):
        skill_text = self.suicide_convert(act) + '。'
        skill_text += '{}に{}属性の{}ダメージ'.format(
            self.fmt_mass_atk(act.mass_attack), self.ATTRIBUTES[act.attribute], self.big_number(act.damage))
        return skill_text

    def suicide_convert(self, act):
        if act.hp_remaining == 0:
            return 'HPが1になる'
        else:
            return 'HPが{}％減少'.format(fmt_mult((1 - act.hp_remaining) * 100))

    def type_attack_boost_convert(self, act):
        return '{}ターンの間、{}タイプの攻撃力が{}倍'.format(
            act.duration, self.typing_to_str(act.types), fmt_mult(act.multiplier))

    def grudge_strike_convert(self, act):
        return '残りHPが応じ{}に{}属性ダメージを与え（HP1のとき攻撃力ｘ{}倍、満タン{}倍）'.format(
            self.fmt_mass_atk(act.mass_attack),
            self.ATTRIBUTES[act.attribute],
            fmt_mult(act.low_multiplier),
            fmt_mult(act.high_multiplier))

    def drain_attr_attack_convert(self, act):
        skill_text = '{}に攻撃力ｘ{}倍の{}属性攻撃し、ダメージ'.format(
            self.fmt_mass_atk(act.mass_attack), fmt_mult(act.atk_multiplier), self.ATTRIBUTES[int(act.attribute)])

        if act.recover_multiplier == 1:
            skill_text += '分のHP回復'
        else:
            skill_text += 'の{}％分のHP回復'.format(fmt_mult(act.recover_multiplier * 100))
        return skill_text

    def attribute_change_convert(self, act):
        return '{}ターンの間、自分の属性が{}属性に変化'.format(
            act.duration, self.ATTRIBUTES[act.attribute])

    def multi_hit_laser_convert(self, act):
        return '{}に{}ダメージ'.format(self.fmt_mass_atk(act.mass_attack), act.damage)

    def hp_nuke_convert(self, act):
        return "{}にチームの総HPｘ{}倍の{}属性攻撃".format(
            self.fmt_mass_atk(act.mass_attack),
            fmt_mult(act.multiplier),
            self.ATTRIBUTES[act.attribute])

    def fixed_pos_convert(self, act):
        board = [[], [], [], [], []]
        board[0] = list(act.row_pos_1)
        board[1] = list(act.row_pos_2)
        board[2] = list(act.row_pos_3)
        board[3] = list(act.row_pos_4)
        board[4] = list(act.row_pos_5)
        orb_count = 0

        output = []
        for x in board:
            orb_count += len(x)

        skill_text = ''
        shape = "<UNDEFINED>"
        if orb_count == 4:
            if len(board[0]) == len(board[4]) == 2:
                skill_text += '盤面4隅に{}ドロップを1個ずつ生成。'.format(self.ATTRIBUTES[act.attribute])
        if not (orb_count % 5):
            for x in range(1, len(board) - 1):  # Check for cross
                if len(board[x]) == 3 and len(board[x - 1]) == len(board[x + 1]) == 1:  # Check for cross
                    row_pos = x
                    col_pos = board[x][1]
                    shape = '十字形'
                    result = (shape, row_pos, col_pos)
                    output.append(result)
                    del board[x][1]
            for x in range(0, len(board)):  # Check for L
                if len(board[x]) == 3:
                    row_pos = x
                    if x < 2:
                        col_pos = board[x + 1][0]
                        del board[x + 1][0]
                    elif x > 2:
                        col_pos = board[x - 1][0]
                        del board[x - 1][0]
                    elif len(board[x + 1]) > 0:
                        col_pos = board[x + 1][0]
                        del board[x + 1][0]
                    else:
                        col_pos = board[x - 1][0]
                        del board[x - 1][0]

                    shape = 'L字形'
                    result = (shape, row_pos, col_pos)
                    output.append(result)

        if not (orb_count % 9):
            for x in range(1, len(board) - 1):  # Check for square
                if len(board[x]) == len(board[x - 1]) == len(board[x + 1]) == 3:
                    row_pos = x
                    col_pos = board[x][1]
                    shape = '正方形'
                    result = (shape, row_pos, col_pos)
                    output.append(result)
                    del board[x][1]
        if orb_count == 18:
            if len(board[0]) == len(board[4]) == len(board[1]) + len(board[2]) + len(board[3]) == 6:
                skill_text += '盤面外周を{}ドロップに変化。'.format(self.ATTRIBUTES[act.attribute])

        if output:
            for entry in output:
                if skill_text:
                    skill_text += '。'
                skill_text += '{}と{}の中心に{}の{}ドロップを1つ生成'.format(
                    ROW_INDEX[entry[1]],
                    COLUMN_INDEX[entry[2]],
                    shape,
                    self.ATTRIBUTES[act.attribute])

        return skill_text

    def match_disable_convert(self, act):
        return '消せないドロップ状態を{}ターン回復'.format(act.duration)

    def board_refresh(self, act):
        return 'ランダムでドロップを入れ替える'

    def leader_swap(self, act):
        return 'リーダーと入れ替わる；もう一度使うとサブに戻る'

    def unlock_all_orbs(self, act):
        return '全ドロップのロック状態を解除'

    def unlock_board_path_toragon(self, act):
        return '全ドロップのロック状態を解除し、火、水、木と光ドロップに変化。3コンボ分のルートを表示。'

    def random_skill(self, act):
        random_skills_text = []
        for idx, s in enumerate(act.random_skills, 1):
            random_skills_text.append('{}、{}'.format(half_to_full(idx), s.full_text(self)))
        return '下からスキルをランダムて発動：{}'.format("；".join(random_skills_text))

    def change_monster(self, act):
        return "[{}]に変身する".format(act.change_to)

    def skyfall_lock(self, act):
        attrs = self.attributes_to_str(act.orbs) if act.orbs else ''
        return "{}ターンの間、{}ドロップがロック状態で落ちてくる".format(act.duration, attrs)

    def spawn_spinner(self, turns: int, speed: float, count: int):
        return '{}ターンの間、ランダムで{}箇所のマスがが{}秒毎に変化する' \
            .format(turns, count, speed)

    def ally_active_disable(self, turns: int):
        return '{}ターンの間、スキル使用不可。'.format(turns)

    def ally_active_delay(self, turns: int):
        return '味方スキルが{}ターン減少。'.format(turns)

    def create_unmatchable(self, act):
        skill_text = self.fmt_duration(act.duration) + self.concat_list_and(self.ATTRIBUTES[i] for i in act.orbs)
        skill_text += 'ドロップが消せなくなる。'
        return skill_text

    def two_part_active(self, strs):
        return '。'.join(strs)


__all__ = ['JpASTextConverter']
