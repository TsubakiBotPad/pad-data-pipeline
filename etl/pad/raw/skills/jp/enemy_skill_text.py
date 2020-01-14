from pad.raw.skills.jp.skill_common import *
import logging

human_fix_logger = logging.getLogger('human_fix')

def concat_list_and(l):
    l = [str(i) for i in l if i]
    if len(l) == 0:
        return ""
    elif len(l) == 1:
        return l[0]
    elif len(l) == 2:
        return "と".join(l)
    return "、".join(l)

def concat_list_or(l):
    l = [str(i) for i in l if i]
    if len(l) == 0:
        return ""
    elif len(l) == 1:
        return l[0]
    elif len(l) == 2:
        return "まだは".join(l)
    return "、".join(l)
    
ATTRIBUTE_MAP = {
   -9: 'ロックされた爆弾',
   -1: 'ランダム属性の',
 None: '火',
    0: '火',
    1: '水',
    2: '木',
    3: '光',
    4: '闇',
    5: '回復',
    6: 'お邪魔',
    7: '毒',
    8: '猛毒',
    9: '爆弾',
}


def attributes_to_str(attributes):
    return concat_list_and([ATTRIBUTE_MAP[x] for x in attributes])


TYPING_MAP = {
    0: '進化用',
    1: 'バランス',
    2: '体力',
    3: '回復',
    4: 'ドラゴン',
    5: '神',
    6: '攻撃',
    7: '悪魔',
    8: 'マシン',
   12: '覚醒用',
   14: '強化合成用',
   15: '売却用',
}


def typing_to_str(types):
    return concat_list_and([TYPING_MAP[x] for x in types])


TARGET_NAMES = {
    TargetType.unset: '○○',
    
    #Specific Subs
    TargetType.random: 'ランダムで{}体',
    TargetType.self_leader: 'リーダー',
    TargetType.both_leader: 'リーダーとフレン',
    TargetType.friend_leader: 'フレンド',
    TargetType.subs: 'ランダムでサブ{}体',
    TargetType.attrs: '属性',
    TargetType.types: 'タイプ',
    TargetType.card: 'card',

    #Specific Players/Enemies (For Recovery)
    TargetType.player: 'プレイヤー',
    TargetType.enemy: '敵',
    TargetType.enemy_ally: '敵の仲間',

    #Full Team Aspect
    TargetType.awokens: '覚醒スキル',
    TargetType.actives: 'スキル',
}


def targets_to_str(targets):
    return  targets if isinstance(targets,str)\
                    else concat_list_and([TARGET_NAMES[x] for x in targets])

ORB_SHAPES = {
    OrbShape.column: '上',
    OrbShape.row: '左',
}

def orbshape_to_str(shapes):
    return concat_list_and([ORB_SHAPES[x] for x in shapes])

UNITS = {
    Unit.unknown: '○○',
    Unit.seconds: '秒',
    Unit.percent: '%',
    Unit.none: '',
}

SOURCE_FUNCS = {
    Source.all_sources: lambda x: '受ける',
    Source.types: typing_to_str,
    Source.attrs: attributes_to_str,
}
    

class JpESTextConverter(JpBaseTextConverter):
    @staticmethod
    def not_set():
        return '詳細はありません'

    @staticmethod
    def default_attack():
        return '通常攻撃'
    
    @staticmethod
    def condition(chance, hp=None, one_time=False):
        output = ""
        if hp:
            output += '{}%HP以下'.format(hp)
        if 0 < chance < 100 and not one_time:
            output += '{}%の確率'.format(chance)
        output += 'で' if output else ''
        if one_time:
            output += '一度だけ使用'
        return output or None

    @staticmethod
    def attack(mult, min_hit=1, max_hit=1):
        if mult is None:
            return None
        output = '{}%ダメージ'. \
            format(minmax(int(min_hit) * int(mult), int(max_hit) * int(mult)))
        if min_hit and max_hit != 1:
            output += ' ({}連続攻撃、{}%ごと)'.format(minmax(min_hit, max_hit), mult)
        return output

    @staticmethod
    def skip():
        return '何もしない'

    @staticmethod
    def bind(min_turns, max_turns, target_count=None, target_types=TargetType.card, source:Source = None):
        if isinstance(target_types, TargetType): target_types = [target_types]
        elif source is not None:
            target_types = SOURCE_FUNCS[source]([target_types])+TARGET_NAMES[TargetType(source.value)]
        targets = targets_to_str(target_types).format(target_count)
        if targets == '覚醒スキル':
            return '{}ターンの間、覚醒スキル無効化'.format(minmax(min_turns, max_turns), targets)
        elif targets == 'スキル':
            return '{}ターンの間、スキル使用不可'.format(minmax(min_turns, max_turns), targets)
        return '{}ターンの間、{}がバインド'.format(minmax(min_turns, max_turns), targets)

    @staticmethod
    def orb_change(orb_from, orb_to, random_count=None, exclude_hearts=False):
        if not isinstance(orb_from, list):
            orb_from = [orb_from]
        orb_from = attributes_to_str(orb_from)
        if not isinstance(orb_to, list):
            orb_to = [orb_to]
        orb_to = attributes_to_str(orb_to)
             
        if random_count is not None:
            if orb_from == 'ランダム属性の':
                output = 'ランダムで{}個のドロップ'.format(random_count)
            else:
                output = '{}ドロップ{}個'.format(orb_from,random_count)
        else:
            output = '{}ドロップ'.format(orb_from)
        output += 'を{}ドロップに変化'.format(orb_to)
            
        return output

    @staticmethod
    def blind():
        return '全ドロップを真っ暗にする'
    
    @staticmethod
    def blind_sticky_random(turns, nmin, nmax):
        if nmin == 42:
            return '{}ターンの間、全ドロップが超暗闇になる'.format(turns)
        else:
            return '{}ターンの間、ランダムで{}個のドロップを超暗闇にする'.format(turns,minmax(nmin, nmax))

    @staticmethod
    def blind_sticky_fixed(turns):
        return '{}ターンの間、特定のドロップが超暗闇にする'.format(turns)

    @staticmethod
    def dispel_buffs():
        return 'こちらにかかっている状態変化を解除'
    
    @staticmethod
    def recover(min_amount, max_amount, target_type):
        target = targets_to_str([target_type])
        return '{}のHPが{}回復'.format(target, minmax(min_amount, max_amount, True))

    @staticmethod
    def enrage(mult, turns):
        output = '攻撃力が{}%に上昇'.format(mult)
        output = ('{}ターンの間、'.format(turns) if turns else '次の攻撃の') + output
        return output

    @staticmethod
    def status_shield(turns):
        return '{}ターンの間、状態異常無効化'.format(turns)

    @staticmethod
    def debuff(d_type, amount, unit, turns):
        amount = amount or 0
        unit = UNITS[unit]
        turns = turns or 0
        if d_type == Status.movetime:
            return '{}ターンの間、操作時間{:+.0f}{}'.format(turns, amount, unit)
        elif d_type == Status.rcv:
            return '{}ターンの間、回復力を{:.0f}{}になる'.format(turns, amount, unit)
        else:
            human_fix_logger.error("無効なデバフタイプ： {}".format(d_type))
            return 'これが表示された場合は、パパガイド管理者に警告してください。'

    @staticmethod
    def end_battle():
        return '自爆'

    @staticmethod
    def change_attribute(attributes):
        if len(attributes) == 1:
            return '自分の属性が{}に変化する'.format(ATTRIBUTE_MAP[attributes[0]])
        else:
            return '自分の属性が{}のうちいずれかに変化する' + attributes_to_str(attributes)

    @staticmethod
    def gravity(percent):
        return '現HPの{}%のダメージ'.format(percent)

    @staticmethod
    def absorb(abs_type: Absorb, condition, min_turns, max_turns=None):
        if abs_type == Absorb.attr:
            source = attributes_to_str(condition)
            return '{}ターンの間、{}属性のダメージを吸収' .format(minmax(min_turns, max_turns), source)
        elif abs_type == Absorb.combo:
            source = '{}コンボ以下の攻撃'.format(condition)
        elif abs_type == Absorb.damage:
            source = '{}以上のダメージ'.format(JpESTextConverter.big_number(condition))
        else:
            human_fix_logger.warning("未知の吸収タイプ: {}".format(abs_type))
            
        return '{}ターンの間、{}を吸収'.format(minmax(min_turns, max_turns), source)

    @staticmethod
    def skyfall(attributes, chance, min_turns, max_turns=None, locked=False):
        lock = 'ロックされた' if locked else ''
        return '{}ターンの間、{}{}ドロップを+{}%に落ちてくる' \
            .format(minmax(min_turns, max_turns), lock, attributes_to_str(attributes), chance)

    @staticmethod
    def void(threshold, turns):
        return '{}ターンの間、{}以上のダメージを無効化'.format(JpESTextConverter.big_number(turns), threshold)

    @staticmethod
    def damage_reduction(source_type: Source, source = None, percent=None, turns=None):
        source = (SOURCE_FUNCS[source_type])(source)
        if source_type == Source.attrs:
            source += '属性からの攻撃'
        elif source_type == Source.types:
            source += 'タープからの攻撃'
        elif source_type == Source.all_sources:
            source += 'ダメージ'
        turns = '{}ターンの間、'.format(turns) if turns else ''
        if percent is None:
            return '{}{}を無効化する' \
                   .format(turns, source)
        else:
            return '{}{}からの攻撃を{}%減少'.format(turns, source, percent)

    @staticmethod
    def invuln_off():
        return 'ダメージを与えられるようになる'

    @staticmethod
    def resolve(percent):
        return 'HP{}%以上のとき、大ダメージを受けてもHP1で耐える'.format(percent)

    @staticmethod
    def leadswap(turns):
        return '{}ターンの間、リーダーを交代'.format(turns)

    @staticmethod
    def row_col_spawn(position_type, positions, attributes):
        return '{}から{}列目のドロップが{}ドロップに変化' \
               .format(ORB_SHAPES[position_type],
                       concat_list_and(positions),
                       attributes_to_str(attributes))

    @staticmethod
    def row_col_multi(desc_arr):
        return JpESTextConverter.concat_list_semicolons(desc_arr)

    @staticmethod
    def board_change(attributes):
        return '全ドロップを{}に変化'.format(attributes_to_str(attributes))

    @staticmethod
    def random_orb_spawn(count, attrs):
        if count == 42:
            return JpESTextConverter.board_change(attrs)
        else:
            return '{}ドロップを{}個{}生成' \
                   .format(attributes_to_str(attrs), count, 'ずつ' if len(attrs)>1 else '')

    @staticmethod
    def fixed_orb_spawn(attributes):
        return '特定の位置に{}ドロップを生成'.format(attributes_to_str(attributes))

    @staticmethod
    def skill_delay(min_turns, max_turns):
        return 'スキルターンを{}ターン遅延'.format(minmax(min_turns, max_turns))

    @staticmethod
    def orb_lock(count, attributes):
        if count == 42 and attributes == JpESTextConverter.ATTRS_EXCEPT_BOMBS:
            return '全ドロップをロック'
        elif count == 42:
            return '{}ドロップをロック'.format(attributes_to_str(attributes))
        elif attributes == JpESTextConverter.ATTRS_EXCEPT_BOMBS:
            return 'ランダムで{}個ドロップをロック'.format(count)
        else:
            return 'ランダムで{}個{}ドロップをロック'.format(count, attributes_to_str(attributes))

    @staticmethod
    def orb_seal(turns, position_type, positions):
        return '{}ターンの間、{}から{}列目のドロップが操作不可' \
            .format(turns, ORB_SHAPES[position_type], concat_list_and(positions))

    @staticmethod
    def cloud(turns, width, height, x, y):
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

    @staticmethod
    def fixed_start():
        return 'ドロップ操作開始位置をランダムで固定される'

    @staticmethod
    def turn_change(turn_counter, threshold=None):
        if threshold:
            return '{}%HP以下で行動ターンが{}に変わる'.format(threshold, turn_counter)
        else:
            return '行動ターンが{}に変わる'.format(turn_counter)

    @staticmethod
    def attribute_block(turns, attributes):
        return '{}ターンの間、{}ドロップを消せなくなる'.format(turns, attributes_to_str(attributes))

    @staticmethod
    def spinners(turns, speed, random_num=None):
        if random_num is None:
            return '{:.1f}ターンの間、特定の位置のマスが{}秒毎に変化する' \
                   .format(turns, speed / 100)
        else:
            return '{}ターンの間、ランダムで{}箇所のマスがが{}秒毎に変化する' \
                   .format(turns, random_num, speed / 100)

    @staticmethod
    def max_hp_change(turns, max_hp, percent):
        if percent:
            return '{}ターンの間、最大HPを{}%で固定される'.format(turns, max_hp)
        else:
            return '{}ターンの間、最大HPを{}で固定される'.format(turns, max_hp)

    @staticmethod
    def fixed_target(turns):
        return '{}ターンの間、攻撃ターゲットを自身に固定する'.format(turns)

    @staticmethod
    def death_cry(message):
        if message is None:
            return '死亡効果を表示'
        else:
            return '{}を表示'.format(message)

    @staticmethod
    def attribute_exists(atts):
        return '盤面に{}ドロップをある場合に使用'.format(attributes_to_str(atts))

    @staticmethod
    def countdown(counter):
        return '\'{}\'を表示してターンをスキップ'.format(counter)

    @staticmethod
    def gacha_fever(attribute, orb_req):
        return 'フィーバーモード: {}ドロップが{}個消す'.format(ATTRIBUTE_MAP[attribute],orb_req)

    @staticmethod
    def lead_alter(turns, target):
        return '{}ターンの間、リーダーが[{}]になる'.format(turns, target)

    @staticmethod
    def force_7x6(turns):
        return '{}ターンの間、盤面が7ｘ6になる'.format(turns)

    @staticmethod
    def no_skyfall(turns):
        return '{}ターンの間、落ちコンしなくなる'.format(turns)

    @staticmethod
    def branch(condition, compare, value, rnd):
        return 'Branch on {} {} {}, target rnd {}'.format(condition, compare, value, rnd)

    @staticmethod
    def join_skill_descs(descs):
        return '＋'.join(descs)


__all__ = ['JpESTextConverter']
