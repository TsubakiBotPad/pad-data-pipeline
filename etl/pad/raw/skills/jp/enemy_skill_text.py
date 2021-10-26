import logging

from pad.raw.skills.jp.skill_common import JpBaseTextConverter, minmax
from pad.raw.skills.skill_common import Absorb, OrbShape, Source, Status, TargetType, Unit

human_fix_logger = logging.getLogger('human_fix')

TARGET_NAMES = {
    TargetType.unset: '○○',

    # Specific Subs
    TargetType.random: 'ランダムで{}体',
    TargetType.self_leader: 'リーダー',
    TargetType.both_leader: 'リーダーとフレン',
    TargetType.friend_leader: 'フレンド',
    TargetType.subs: 'ランダムでサブ{}体',
    TargetType.attrs: '属性',
    TargetType.types: 'タイプ',
    TargetType.card: '{}体',
    TargetType.all: '全体',

    # Specific Players/Enemies (For Recovery)
    TargetType.player: 'プレイヤー',
    TargetType.enemy: '敵',
    TargetType.enemy_ally: '敵の仲間',

    # Full Team Aspect
    TargetType.awokens: '覚醒スキル',
    TargetType.actives: 'スキル',
}


def targets_to_str(targets):
    return targets if isinstance(targets, str) \
        else JpBaseTextConverter().concat_list_and([TARGET_NAMES[x] for x in targets])


ORB_SHAPES = {
    OrbShape.column: '上',
    OrbShape.row: '左',
}


def orbshape_to_str(shapes):
    return JpBaseTextConverter().concat_list_and([ORB_SHAPES[x] for x in shapes])


UNITS = {
    Unit.unknown: '○○',
    Unit.seconds: '秒',
    Unit.percent: '%',
    Unit.none: '',
}

SOURCE_FUNCS = {
    Source.all_sources: lambda x: '受ける',
    Source.types: JpBaseTextConverter().typing_to_str,
    Source.attrs: JpBaseTextConverter().attributes_to_str,
}


class JpESTextConverter(JpBaseTextConverter):
    def not_set(self):
        return '詳細はありません'

    def default_attack(self):
        return '通常攻撃'

    def condition(self, chance, hp=None, one_time=False):
        output = ""
        if hp:
            output += '{}%HP以下'.format(hp)
        if 0 < chance < 100 and not one_time:
            output += '{}%の確率'.format(chance)
        output += 'で' if output else ''
        if one_time:
            output += '一度だけ使用'
        return output or None

    def attack(self, mult, min_hit=1, max_hit=1):
        if mult is None:
            return None
        output = '{}%ダメージ'. \
            format(minmax(int(min_hit) * int(mult), int(max_hit) * int(mult)))
        if min_hit and max_hit != 1:
            output += ' ({}連続攻撃、{}%ごと)'.format(minmax(min_hit, max_hit), mult)
        return output

    def skip(self):
        return '何もしない'

    def bind(self, min_turns, max_turns, target_count=None, target_types=TargetType.card, source: Source = None):
        if isinstance(target_types, TargetType):
            target_types = [target_types]
        elif source is not None:
            source_target = TargetType.attrs if source == Source.attrs \
                else TargetType.types if source == Source.types \
                else TargetType.unset
            target_types = SOURCE_FUNCS[source]([target_types]) + TARGET_NAMES[source_target]
        targets = targets_to_str(target_types).format(target_count)
        if targets == '覚醒スキル':
            return '{}ターンの間、覚醒スキル無効化'.format(minmax(min_turns, max_turns), targets)
        elif targets == 'スキル':
            return '{}ターンの間、スキル使用不可'.format(minmax(min_turns, max_turns), targets)
        return '{}ターンの間、{}がバインド'.format(minmax(min_turns, max_turns), targets)

    def orb_change(self, orb_from, orb_to, random_count=None, exclude_hearts=False, random_type_count=None):
        if not isinstance(orb_from, list):
            orb_from = [orb_from]
        orb_from = self.attributes_to_str(orb_from)
        if not isinstance(orb_to, list):
            orb_to = [orb_to]
        orb_to = self.attributes_to_str(orb_to)
        output = ''

        if exclude_hearts:
            output += '回復ドロップ以外'

        if random_count is not None:
            if orb_from == 'ランダム属性の':
                output += 'ランダムで{}個のドロップ'.format(random_count)
            else:
                output += '{}ドロップ{}個'.format(orb_from, random_count)
        elif random_type_count is not None:
            output += 'ランダムで{}色'.format(random_type_count)
        else:
            output += '{}ドロップ'.format(orb_from)
        output += 'を{}ドロップに変化'.format(orb_to)

        return output

    def blind(self):
        return '全ドロップを真っ暗にする'

    def blind_sticky_random(self, turns, nmin, nmax):
        if nmin == 42:
            return '{}ターンの間、全ドロップが超暗闇になる'.format(turns)
        else:
            return '{}ターンの間、ランダムで{}個のドロップを超暗闇にする'.format(turns, minmax(nmin, nmax))

    def blind_sticky_fixed(self, turns):
        return '{}ターンの間、特定のドロップが超暗闇にする'.format(turns)

    def blind_sticky_skyfall(self, turns, chance, b_turns):
        return '{}ターンの間、{}%の確率を超暗闇ドロップ{}ターンが発生'.format(turns, chance, b_turns)

    def dispel_buffs(self):
        return 'こちらにかかっている状態変化を解除'

    def recover(self, min_amount, max_amount, target_type, player_threshold=None):
        target = targets_to_str([target_type])
        if player_threshold and player_threshold != 100:
            return '{}%HP以下で{}のHPが{}回復'.format(player_threshold, target, minmax(min_amount, max_amount, True))
        else:
            return '{}のHPが{}回復'.format(target, minmax(min_amount, max_amount, True))

    def enrage(self, mult, turns):
        output = '攻撃力が{}%に上昇'.format(mult)
        output = ('{}ターンの間、'.format(turns) if turns else '次の攻撃の') + output
        return output

    def status_shield(self, turns):
        return '{}ターンの間、状態異常無効化'.format(turns)

    def debuff(self, d_type, amount, unit, turns):
        amount = amount or 0
        unit = UNITS[unit]
        turns = turns or 0
        if d_type == Status.movetime:
            return '{}ターンの間、操作時間{:.0f}{}'.format(turns, amount, unit)
        elif d_type == Status.rcv:
            return '{}ターンの間、回復力を{:.0f}{}になる'.format(turns, amount, unit)
        else:
            human_fix_logger.error("無効なデバフタイプ： {}".format(d_type))
            return 'これが表示された場合は、パパガイド管理者に警告してください。'

    def end_battle(self):
        return '自爆'

    def change_attribute(self, attributes):
        if len(attributes) == 1:
            return '自分の属性が{}に変化する'.format(self.ATTRIBUTES[attributes[0]])
        else:
            return '自分の属性が{}のうちいずれかに変化する' + self.attributes_to_str(attributes)

    def gravity(self, percent):
        return '現HPの{}%のダメージ'.format(percent)

    def absorb(self, abs_type: Absorb, condition, min_turns, max_turns=None):
        if abs_type == Absorb.attr:
            source = self.attributes_to_str(condition)
            return '{}ターンの間、{}属性のダメージを吸収'.format(minmax(min_turns, max_turns), source)
        elif abs_type == Absorb.combo:
            source = '{}コンボ以下の攻撃'.format(condition)
        elif abs_type == Absorb.damage:
            source = '{}以上のダメージ'.format(self.big_number(condition))
        else:
            raise ValueError("未知の吸収タイプ: {}".format(abs_type))

        return '{}ターンの間、{}を吸収'.format(minmax(min_turns, max_turns), source)

    def skyfall(self, attributes, chance, min_turns, max_turns=None, locked=False):
        lock = 'ロックされた' if locked else ''
        return '{}ターンの間、{}{}ドロップを+{}%に落ちてくる' \
            .format(minmax(min_turns, max_turns), lock, self.attributes_to_str(attributes), chance)

    def void(self, threshold, turns):
        return '{}ターンの間、{}以上のダメージを無効化'.format(turns, self.big_number(threshold))

    def damage_reduction(self, source_type: Source, source=None, percent=None, turns=None):
        source = (SOURCE_FUNCS[source_type])(source)
        if source_type == Source.attrs:
            source += '属性からの攻撃'
        elif source_type == Source.types:
            source += 'タイプからの攻撃'
        elif source_type == Source.all_sources:
            source += 'ダメージ'
        turns = '{}ターンの間、'.format(turns) if turns else ''
        if percent is None:
            return '{}{}を無効化する'.format(turns, source)
        else:
            return '{}{}からの攻撃を{}%減少'.format(turns, source, percent)

    def invuln_off(self):
        return 'ダメージを与えられるようになる'

    def resolve(self, percent):
        return 'HP{}%以上のとき、大ダメージを受けてもHP1で耐える'.format(percent)

    def superresolve(self, percent, remaining):
        return 'HP{}%以上のとき、大ダメージを受けてもHP{}%で耐える'.format(percent, remaining)

    def leadswap(self, turns):
        return '{}ターンの間、リーダーを交代'.format(turns)

    def row_col_spawn(self, position_type, positions, attributes):
        return '{}から{}列目のドロップが{}ドロップに変化' \
            .format(ORB_SHAPES[position_type],
                    self.concat_list_and(positions),
                    self.attributes_to_str(attributes))

    def row_col_multi(self, desc_arr):
        return self.concat_list_semicolons(desc_arr)

    def board_change(self, attributes):
        return '全ドロップを{}に変化'.format(self.attributes_to_str(attributes))

    def random_orb_spawn(self, count, attrs):
        if count == 42:
            return self.board_change(attrs)
        else:
            return '{}ドロップを{}個{}生成' \
                .format(self.attributes_to_str(attrs), count, '')

    def fixed_orb_spawn(self, attributes):
        return '特定の位置に{}ドロップを生成'.format(self.attributes_to_str(attributes))

    def skill_delay(self, min_turns, max_turns):
        return 'スキルターンを{}ターン遅延'.format(minmax(min_turns, max_turns))

    def orb_lock(self, count, attributes):
        if count == 42 and attributes == self.ATTRS_EXCEPT_BOMBS:
            return '全ドロップをロック'
        elif count == 42:
            return '{}ドロップをロック'.format(self.attributes_to_str(attributes))
        elif attributes == self.ATTRS_EXCEPT_BOMBS:
            return 'ランダムで{}個ドロップをロック'.format(count)
        else:
            return 'ランダムで{}個{}ドロップをロック'.format(count, self.attributes_to_str(attributes))

    def orb_seal(self, turns, position_type, positions):
        return '{}ターンの間、{}から{}列目のドロップが操作不可' \
            .format(turns, ORB_SHAPES[position_type], self.concat_list_and(positions))

    def cloud(self, turns, width, height, x, y):
        if width == 6 and height == 1:
            shape = '横1列'
        elif width == 1 and height == 5:
            shape = '縦1列'
        elif width == height:
            shape = '{}×{}マスの正方形'.format(width, height)
        else:
            shape = '{}×{}マスの長方形'.format(width, height)
        pos = []
        if x is not None and shape != '横1列':
            pos.append('左から{}列目'.format(x))
        if y is not None and shape != '縦1列':
            pos.append('上から{}列目'.format(y))
        if len(pos) == 0:
            pos.append('ランダムで')
        return '{}ターンの間、{}の{}を雲で隠す'.format(turns, '、'.join(pos), shape)

    def fixed_start(self):
        return 'ドロップ操作開始位置をランダムで固定される'

    def turn_change(self, turn_counter, threshold=None):
        if threshold:
            return '{}%HP以下で行動ターンが{}に変わる'.format(threshold, turn_counter)
        else:
            return '行動ターンが{}に変わる'.format(turn_counter)

    def attribute_block(self, turns, attributes):
        return '{}ターンの間、{}ドロップを消せなくなる'.format(turns, self.attributes_to_str(attributes))

    def spinners(self, turns, speed, random_num=None):
        if random_num is None:
            return '{:.1f}ターンの間、特定の位置のマスが{}秒毎に変化する' \
                .format(turns, speed / 100)
        else:
            return '{}ターンの間、ランダムで{}箇所のマスがが{}秒毎に変化する' \
                .format(turns, random_num, speed / 100)

    def max_hp_change(self, turns, max_hp, percent):
        if percent:
            return '{}ターンの間、最大HPを{}%で固定される'.format(turns, max_hp)
        else:
            return '{}ターンの間、最大HPを{}で固定される'.format(turns, max_hp)

    def fixed_target(self, turns):
        return '{}ターンの間、攻撃ターゲットを自身に固定する'.format(turns)

    def death_cry(self, message):
        if message is None:
            return '死亡効果を表示'
        else:
            return '「{}」を表示'.format(message)

    def attribute_exists(self, atts):
        return '盤面に{}ドロップをある場合に使用'.format(self.attributes_to_str(atts))

    def countdown(self, counter):
        return '「{}」を表示してターンをスキップ'.format(counter)

    def use_skillset(self, skill_set_id):
        return 'Use skill set #{}'.format(skill_set_id)

    def gacha_fever(self, attribute, orb_req):
        return 'フィーバーモード: {}ドロップが{}個消す'.format(self.ATTRIBUTES[attribute], orb_req)

    def lead_alter(self, turns, target):
        return '{}ターンの間、リーダーが[{}]になる'.format(turns, target)

    def force_board_size(self, turns: int, size_param: int):
        size = {1: '7ｘ6', 2: '5ｘ4', 3: '6ｘ5'}.get(size_param, 'unknown')
        return '{}ターンの間、盤面が{}になる'.format(turns, size)

    def no_skyfall(self, turns):
        return '{}ターンの間、落ちコンしなくなる'.format(turns)

    def combo_skyfall(self, turns, chance):
        return '{}ターンの間、{}%の確率でコンボドロップが発生'.format(turns, chance)

    def debuff_atk(self, turns, amount):
        return '{}ターンの間、攻撃力が{}%減少'.format(turns, amount)

    def target_skill_haste(self, min_turns, max_turns, target):
        return f'{TARGET_NAMES[target].format(4)}のスキルが{minmax(min_turns, max_turns)}ターン溜まる'

    def target_skill_delay(self, min_turns, max_turns, target):
        return f'{TARGET_NAMES[target].format(4)}のスキルが{minmax(min_turns, max_turns)}ターン減らす'

    def disable_assists(self, turns):
        return '{}ターンの間、アシストが無効になった'.format(turns)

    def branch(self, condition, compare, value, rnd):
        return 'Branch on {} {} {}, target rnd {}'.format(condition, compare, value, rnd)

    def join_skill_descs(self, descs):
        return '＋'.join(descs)
