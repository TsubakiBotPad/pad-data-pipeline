from pad.raw.skills.kr.skill_common import *
from pad.raw.skills.en.enemy_skill_text import EnESTextConverter as BaseESTextConverter

from enum import Enum

import logging

human_fix_logger = logging.getLogger('human_fix')

TARGET_NAMES = {
    TargetType.unset: '<targets unset>',

    # Specific Subs
    TargetType.random: 'random card',
    TargetType.self_leader: 'player leader',
    TargetType.both_leader: 'both leaders',
    TargetType.friend_leader: 'friend leader',
    TargetType.subs: 'random sub',
    TargetType.attrs: '속성',
    TargetType.types: '타입',
    TargetType.card: 'card',

    # Specific Players/Enemies (For Recovery)
    TargetType.player: '플레이어',
    TargetType.enemy: '적',
    TargetType.enemy_ally: '적 아군',

    # Full Team Aspect
    TargetType.awokens: 'awoken skills',
    TargetType.actives: 'active skills',

}


def targets_to_str(targets):
    return targets if isinstance(targets, str) \
        else '、'.join([TARGET_NAMES[x] for x in targets])


ORB_SHAPES = {
    OrbShape.l_shape: 'L shape',
    OrbShape.cross: 'cross',
    OrbShape.column: '열',
    OrbShape.row: '행',
}


def orbshape_to_str(shapes):
    return KrBaseTextConverter.concat_list_and([ORB_SHAPES[x] for x in shapes])


STATUSES = {
    Status.movetime: 'movetime',
    Status.atk: 'ATK',
    Status.hp: 'HP',
    Status.rcv: 'RCV',
}

UNITS = {
    Unit.unknown: '?',
    Unit.seconds: 's',
    Unit.percent: '%',
    Unit.none: '',
}

SOURCE_FUNCS = {
    Source.all_sources: lambda x: 'all sources',
    Source.types: KrBaseTextConverter.typing_to_str,
    Source.attrs: KrBaseTextConverter.attributes_to_str,
}


class KrESTextConverter(KrBaseTextConverter, BaseESTextConverter):
    def not_set(self):
        return 'No description set'

    def default_attack(self):
        return 'Default Attack'

    def condition(self, chance, hp=None, one_time=False):
        output = ['']
        if hp:
            output[0] += 'HP가 {}% 이하일때'.format(hp)
        if 0 < chance < 100 and not one_time:
            output[0] += '{}% 확률'.format(chance)
        if not output[0]:
            output = []
        if one_time:
            output.append('반드시 1회 사용')
        return capitalize_first('、'.join(output)) if len(output) > 0 else None

    def attack(self, mult, min_hit=1, max_hit=1):
        if mult is None:
            return None
        output = '{}%데미지'. \
            format(minmax(int(min_hit) * int(mult), int(max_hit) * int(mult)))
        if min_hit and max_hit != 1:
            output += ' ({}회, 각 {}%)'. \
                format(minmax(min_hit, max_hit), mult)
        return output

    def skip(self):
        return '아무것도 하지않는다'

    def bind(self, min_turns, max_turns, target_count=None, target_types=TargetType.card, source: Source = None):
        if isinstance(target_types, TargetType):
            target_types = [target_types]
        elif source is not None:
            target_types = SOURCE_FUNCS[source]([target_types]) + ' cards'
        targets = targets_to_str(target_types)
        output = 'Bind {:s} '.format(pluralize2(targets, target_count))
        output += 'for ' + pluralize2('turn', minmax(min_turns, max_turns))
        return output

    def orb_change(self, orb_from, orb_to, random_count=None, random_type_count=None, exclude_hearts=False):
        if not isinstance(orb_from, list):
            orb_from = [orb_from]
        orb_from = self.attributes_to_str(orb_from)

        if not isinstance(orb_to, list):
            orb_to = [orb_to]
        orb_to = self.attributes_to_str(orb_to)

        output = 'Change '
        if random_count is not None:
            if orb_from == 'Random':
                output += '{} random {:s}'.format(random_count, pluralize('orb', random_count))
            else:
                output += '{} random {} {}'.format(random_count, orbs_from, pluralize('orb', random_count))
            if exclude_hearts:
                output += ' (excluding hearts)'
        else:
            if 'Random' in orb_from:
                output += 'a random attribute'
            else:
                output += 'all {} orbs'.format(orb_from)
        output += ' to '
        if 'Random' in orb_to:
            output += 'a random attribute'
        else:
            output += '{} {}'.format(orb_to, 'orbs')
        return output

    def blind(self):
        return '모든 드롭을 암흑으로 가림'

    def blind_sticky_random(self, turns, min_count, max_count):
        if min_count == 42:
            return '{}턴동안 모든 드롭을 초암흑으로 가림'.format(turns)
        else:
            return '{}턴동안 무작위 {}개의 드롭을 초암흑으로 가림' \
                .format(turns, minmax(min_count, max_count))

    def blind_sticky_fixed(self, turns):
        return 'Blind orbs in specific positions for {:s}'.format(pluralize2('turn', turns))

    def dispel_buffs(self):
        return '플레이어의 강화 효과를 모두 제거'

    def recover(self, min_amount, max_amount, target_type):
        target = targets_to_str([target_type])
        return capitalize_first('{:s} HP {}% 회복'.format(target, minmax(min_amount, max_amount, True)))

    def enrage(self, mult, turns):
        output = '{}턴동안 공격력 {}%로 상승' if turns else '다음 {}번 공격 {}% 데미지'
        return output.format(mult)

    def status_shield(self, turns):
        return '{}턴 동안 상태이상 무효화 '.format(turns)

    def debuff(self, d_type, amount, unit, turns):
        amount = amount or 0
        d_type = STATUSES[d_type] or ''
        unit = UNITS[unit]
        turns = turns or 0
        return '{:s} {:+.0f}{:s} for {:s}' \
            .format(capitalize_first(d_type), amount, unit, pluralize2('turn', turns))

    def end_battle(self):
        return 'Reduce self HP to 0'

    def change_attribute(self, attributes):
        if len(attributes) == 1:
            return '적의 속성이 {} 속성으로 변환'.format(ATTRIBUTE_MAP[attributes[0]])
        else:
            return '무작위로 적의 속성이 {}중 한속성으로 변환'.format(self.attributes_to_str(attributes))

    def gravity(self, percent):
        return '플레이어 - {}%HP'.format(percent)

    def absorb(self, abs_type: Absorb, condition, min_turns, max_turns=None):
        if abs_type == Absorb.attr:
            source = self.attributes_to_str(condition)
            return '{}턴동안 {} 속성의 공격을 흡수' \
                .format(minmax(min_turns, max_turns), source)
        elif abs_type == Absorb.combo:
            source = ' {}콤보 이하의'.format(condition)
        elif abs_type == Absorb.damage:
            source = ' {} 이상'.format(self.bignumber(condition))
        else:
            source = 'ㅇㅇ'
        return '{}턴동안 공격을 흡수'.format(minmax(min_turns, max_turns), source)

    def skyfall(self, attributes, chance, min_turns, max_turns=None, locked=False):
        lock = 'Locked ' if locked else ''
        orbs = self.attributes_to_str(attributes)
        if orbs != 'Random':
            orbs += '드롭이 '
        return '{}턴동안 {}%확률로 {}잠금 상태로 출현' \
            .format(minmax(min_turns, max_turns), chance, orbs)

    def void(self, threshold, turns):
        return 'Void damage >= {:d} for {:s}'.format(threshold, pluralize2('turn', turns))

    def damage_reduction(self, source_type: Source, source=None, percent=None, turns=None):
        source = (SOURCE_FUNCS[source_type])(source)
        if source_type != Source.all_sources:
            source += TARGET_NAMES[TargetType(source.value)] + '에게 받는'
        else:
            source = '모든'
        if percent is None:
            return source + ' 피해 {}턴동안 무효화'.format(turns)
        else:
            if turns:
                return 'Reduce damage from {:s} by {:d}% for {:s}' \
                    .format(source, percent, pluralize2('turn', turns))
            else:
                return 'Reduce damage from {:s} by {:d}%' \
                    .format(source, percent)

    def invuln_off(self):
        return '피해를 입힐 수 있는 상태가 된다'

    def resolve(self, percent):
        return 'HP {}% 이상일 때 현재 HP 이상의 데미지를 받아도 HP 1이 남고 생존'.format(percent)

    def leadswap(self, turns):
        return 'Leader changes to random sub for {:s}'.format(pluralize2('turn', turns))

    def row_col_spawn(self, position_type, positions, attributes):
        return '{}을 {}드롭으로 변환'.format(
            self.concat_list_and(map(lambda x: x + ORB_SHAPES[position_type])),
            self.attributes_to_str(attributes))

    def row_col_multi(self, desc_arr):
        return self.concat_list_semicolons(desc_arr)

    def board_change(self, attributes):
        return '모든 드롭을 {}드롭으로 변환'.format(self.attributes_to_str(attributes))

    def random_orb_spawn(self, count, attributes):
        if count == 42:
            return KrESTextConverter.board_change(attributes)
        else:
            return '무작위 {}개 드롭을 {}드롭으로 변환' \
                .format(count, self.attributes_to_str(attributes))

    def fixed_orb_spawn(self, attributes):
        return '특정 위치에 {}드롭 생성'.format(self.attributes_to_str(attributes))

    def skill_delay(self, min_turns, max_turns):
        return '아군의 액티브 스킬 대기 턴 {}턴 증가'.format(minmax(min_turns, max_turns))

    def orb_lock(self, count, attributes):
        if count == 42 and attributes == EnESTextConverter.ATTRS_EXCEPT_BOMBS:
            return '모든 드롭을 잠금'
        elif count == 42:
            return '모든 {}속성 드롭을 잠금'.format(self.attributes_to_str(attributes))
        elif attributes == EnESTextConverter.ATTRS_EXCEPT_BOMBS:
            return '무작위로 {}개의 드롭을 잠금'.format(count)
        else:
            return '무작위로 {}개의 {}속성 드롭을 잠금'.format(count, self.attributes_to_str(attributes))

    def orb_seal(self, turns, position_type, positions):
        return '{}턴동안 {}{}의 드롭을 움직일 수 없음' \
            .format(turns,
                    self.concat_list_and([ordinal(x) for x in positions]),
                    ORB_SHAPES[position_type])

    def cloud(self, turns, width, height, x, y):
        if width == 6 and height == 1:
            shape = 'row'
        elif width == 1 and height == 5:
            shape = 'column'
        else:
            shape = '{:d}×{:d}'.format(width, height)
            shape += ' square' if width == height else ' rectangle'
        pos = []
        if x is not None and shape != 'Row of':
            pos.append('{:s} row'.format(ordinal(x)))
        if y is not None and shape != 'Column of':
            pos.append('{:s} column'.format(ordinal(y)))
        if len(pos) == 0:
            pos.append('a random location')
        return 'A {:s} of clouds appears for {:s} at {:s}' \
            .format(shape, pluralize2('turn', turns), ', '.join(pos))

    def fixed_start(self):
        return '무작위로 조작할 드롭을 강제로 지정'

    def turn_change(self, turn_counter, threshold=None):
        if threshold:
            return '적 HP {}% 이하일때 행동 턴 {}턴으로 변경'.format(threshold, turn_counter)
        else:
            return '적 행동 턴 {}턴으로 변경'.format(turn_counter)

    def attribute_block(self, turns, attributes):
        return '{}턴 동안 {attrs}드롭을 연결해도 지울 수 없음'.format(turns, self.attributes_to_str(attributes))

    def spinners(self, turns, speed, random_num=None):
        if random_num is None:
            return 'Specific orbs change every {:.1f}s for {:s}' \
                .format(speed / 100, pluralize2('turn', turns))
        else:
            return '{}턴동안 무작위 드롭 {}개를 {:.1f}초마다 변환' \
                .format(turns, random_num, speed / 100)

    def max_hp_change(self, turns, max_hp, percent):
        if percent:
            return '{}턴 동안 플레이어의 HP를 {}%로 변경'.format(turns, max_hp)
        else:
            return '{}턴 동안 플레이어의 최대 HP를 {}로 고정'.format(turns, max_hp)

    def fixed_target(self, turns):
        return '{}턴동안 공격을 이 적에게 고정'.format(turns)

    def death_cry(self, message):
        if message is None:
            return 'Show death effect'
        else:
            return '메시지를 출력: 「{}」'.format(message)

    def attribute_exists(self, atts):
        return 'when {:s} orbs are on the board'.format(self.attributes_to_str(atts, 'or'))

    def countdown(self, counter):
        return '「{}」를 출력하고 턴을 건너뛴다'.format(counter)

    def gacha_fever(self, attribute, orb_req):
        return '피버 모드: {}드롭 {}개를 지우면 클리어'.format(ATTRIBUTE_MAP[attribute], orb_req)

    def lead_alter(self, turns, target):
        return '{}턴 동안 리더를 [{}]로 변경'.format(target, turns)

    def force_7x6(self, turns):
        return '{}턴 동안 드롭판을 7x6으로 변경'.format(turns)

    def no_skyfall(self, turns):
        return '{}턴 동안 낙차 콤보 없음'.format(turns)

    def branch(self, condition, compare, value, rnd):
        return 'Branch on {} {} {}, target rnd {}'.format(condition, compare, value, rnd)

    def join_skill_descs(self, descs):
        return ' + '.join(descs)


__all__ = ['KrESTextConverter']
