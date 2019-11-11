from collections import OrderedDict
import json
from math import ceil, log
from typing import List

from pad.raw import EnemySkill
from pad.raw.card import ESRef, Card

ATTRIBUTE_MAP = {
    -1: 'Random',
    None: 'Fire',
    0: 'Fire',
    1: 'Water',
    2: 'Wood',
    3: 'Light',
    4: 'Dark',
    5: 'Heal',
    6: 'Jammer',
    7: 'Poison',
    8: 'Mortal Poison',
    9: 'Bomb',
}

TYPING_MAP = {
    1: 'Balanced',
    2: 'Physical',
    3: 'Healer',
    4: 'Dragon',
    5: 'God',
    6: 'Attacker',
    7: 'Devil',
    8: 'Machine',
}


class DictWithAttributeAccess(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value


# TODO: this needs fixing, can't have a global map like this
enemy_skill_map = None


def es_id(skill: ESRef):
    return skill.enemy_skill_id


def name(skill: ESRef):
    return enemy_skill_map[skill.enemy_skill_id].name


def params(skill: ESRef):
    return enemy_skill_map[skill.enemy_skill_id].params


def ai(skill: ESRef):
    return skill.enemy_ai


def rnd(skill: ESRef):
    return skill.enemy_rnd


def es_type(skill: ESRef):
    return enemy_skill_map[skill.enemy_skill_id].type


def attribute_bitmap(bits, inverse=False, bit_len=9):
    if bits is None:
        return None
    if bits == -1:
        return ['random']
    offset = 0
    atts = []
    while offset < bit_len:
        if inverse:
            if (bits >> offset) & 1 == 0:
                atts.append(ATTRIBUTE_MAP[offset])
        else:
            if (bits >> offset) & 1 == 1:
                atts.append(ATTRIBUTE_MAP[offset])
        offset += 1
    return atts


def typing_bitmap(bits):
    if bits is None:
        return None
    if bits == -1:
        return []
    offset = 0
    types = []
    while offset < bits.bit_length():
        if (bits >> offset) & 1 == 1:
            types.append(TYPING_MAP[offset])
        offset += 1
    return types


def bind_bitmap(bits):
    if bits is None:
        return ['random']
    targets = []
    if (bits >> 0) & 1 == 1:
        targets.append('own leader')
    if (bits >> 1) & 1 == 1:
        if len(targets) > 0:
            targets = ['both leaders']
        else:
            targets.append('friend leader')
    if (bits >> 2) & 1 == 1:
        targets.append('subs')
    return targets


def ordinal(n): return "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


def position_bitmap(bits):
    offset = 0
    positions = []
    while offset < bits.bit_length():
        if (bits >> offset) & 1 == 1:
            positions.append(offset + 1)
        offset += 1
    return positions


def positions_2d_bitmap(bits_arr):
    # row check
    rows = []
    for i in range(5):
        if bits_arr[i] is None:
            bits_arr[i] = 0
        is_row = True
        not_row = True
        for j in range(6):
            is_row = is_row and (bits_arr[i] >> j) & 1 == 1
            not_row = not_row and (bits_arr[i] >> j) & 1 != 1
        if is_row:
            rows.append(i + 1)
    if len(rows) == 5:
        return 'all', None, None
    if len(rows) == 0:
        rows = None
    # column check
    cols = []
    for j in range(6):
        is_col = True
        for i in range(5):
            is_col = is_col and (bits_arr[i] >> j) & 1 == 1
        if is_col:
            cols.append(j + 1)
    if len(cols) == 0:
        cols = None
    positions = []
    for i in range(5):
        row = ''
        for j in range(6):
            if (bits_arr[i] >> j) & 1 == 1:
                row += 'O'
            else:
                row += 'X'
        positions.append(row)
    return positions, rows, cols


# description


class Describe:
    @staticmethod
    def condition(chance, hp=None, one_time=False):
        output = []
        if 0 < chance < 100 and not one_time:
            output.append('{:d}% chance'.format(chance))
        if hp:
            output.append('when < {:d}% HP'.format(hp))
        if one_time:
            if len(output) > 0:
                output.append(', one-time use')
            else:
                output.append('one-time use')
        return ' '.join(output).capitalize() if len(output) > 0 else None

    @staticmethod
    def attack(mult, min_hit=1, max_hit=1):
        if mult is None:
            return None
        output = ''
        if min_hit == max_hit:
            output += 'Deal {:d}% damage'.format(int(min_hit) * int(mult))
            if int(min_hit) > 1:
                output += ' ({:d} hits, {:d}% each)'.format(min_hit, mult)
        else:
            output += 'Deal {:d}%~{:d}% damage ({:d}~{:d} hits, {:d}% each)'. \
                format(int(min_hit) * int(mult), int(max_hit) * int(mult), min_hit, max_hit, mult)
        return output

    @staticmethod
    def skip():
        return 'Do nothing'

    @staticmethod
    def bind(min_turns, max_turns, target_count=None, target_type='cards'):
        output = []
        if target_count:
            output.append('Bind {:d} {:s}'.format(target_count, target_type))
        else:
            output.append('Bind {:s}'.format(target_type))
        if max_turns is not None and min_turns != max_turns:
            output.append('{:d}~{:d} turns'.format(min_turns, max_turns))
        else:
            output.append('{:d} turns'.format(min_turns))
        return ' for '.join(output)

    @staticmethod
    def orb_change(orb_from, orb_to):
        output = 'Change '
        if type(orb_from) == list:
            output += ', '.join(orb_from)
        else:
            output += orb_from
        output += ' to '
        if type(orb_to) == list:
            output += ', '.join(orb_to)
        else:
            output += orb_to
        return output

    @staticmethod
    def blind():
        return 'Blind all orbs on the board'

    @staticmethod
    def blind_sticky_random(turns, min_count, max_count):
        if min_count == 42:
            return 'Blind all orbs for {:d} turns'.format(turns)
        if min_count == max_count:
            return 'Blind random {:d} orbs for {:d} turns'.format(min_count, turns)
        else:
            return 'Blind random {:d}~{:d} orbs for {:d} turns'.format(min_count, max_count, turns)

    @staticmethod
    def blind_sticky_fixed(turns):
        return 'Blind orbs in specific positions for {:d} turns'.format(turns)

    @staticmethod
    def recover(min_amount, max_amount, target='enemy'):
        if min_amount == max_amount or max_amount is None:
            return '{:s} recover {:d}% HP'.format(target, min_amount).capitalize()
        else:
            return '{:s} recover {:d}%~{:d}% HP'.format(target, min_amount, max_amount).capitalize()

    @staticmethod
    def enrage(mult, turns):
        output = ['Increase damage to {:d}%'.format(mult)]
        if turns == 0:
            output.append('attack')
        else:
            output.append('{:d} turns'.format(turns))
        return ' for the next '.join(output)

    @staticmethod
    def status_shield(turns):
        return 'Voids status ailments for {:d} turns'.format(turns)

    @staticmethod
    def debuff(d_type, amount, unit, turns):
        return '{:s} {:.0f}{:s} for {:d} turns'.format(d_type, amount, unit, turns).capitalize()

    @staticmethod
    def end_battle():
        return 'Reduce self HP to 0'

    @staticmethod
    def change_attribute(attributes):
        if len(attributes) == 1:
            return 'Change own attribute to ' + attributes[0]
        else:
            return 'Change own attribute to random one of ' + ', '.join(attributes)

    @staticmethod
    def gravity(percent):
        return 'Player -{:d}% HP'.format(percent)

    @staticmethod
    def absorb(source, min_turns, max_turns=None):
        if max_turns is None or min_turns == max_turns:
            return 'Absorb {:s} damage for {:d} turns'.format(source, min_turns)
        else:
            return 'Absorb {:s} damage for {:d}~{:d} turns'.format(source, min_turns, max_turns)

    @staticmethod
    def skyfall(orbs, chance, min_turns, max_turns=None, locked=False):
        lock = 'Locked ' if locked else ''
        if max_turns is None or min_turns == max_turns:
            return '{:s}{:s} skyfall +{:d}% for {:d} turns'.format(lock, ', '.join(orbs), chance, min_turns)
        else:
            return '{:s}{:s} skyfall +{:d}% for {:d}~{:d} turns' \
                .format(lock, ', '.join(orbs), chance, min_turns, max_turns)

    @staticmethod
    def void(threshold, turns):
        return 'Void damage >= {:d} for {:d} turns'.format(threshold, turns)

    @staticmethod
    def damage_reduction(source, percent=None, turns=None):
        if percent is None:
            return 'Immune to damage from {:s} for {:d} turns'.format(source, turns)
        else:
            if turns:
                return 'Reduce damage from {:s} by {:d}% for {:d} turns'.format(source, percent, turns)
            else:
                return 'Reduce damage from {:s} by {:d}%'.format(source, percent)

    @staticmethod
    def resolve(percent):
        return 'Survive attacks with 1 HP when HP > {:d}%'.format(percent)

    @staticmethod
    def leadswap(turns):
        return 'Leader changes to random sub for {:d} turns'.format(turns)

    @staticmethod
    def row_col_spawn(position_type, positions, attributes):
        return 'Change {:s} {:s} to {:s} orbs'.format(
            ', '.join([ordinal(x) for x in positions]), position_type, ', '.join(attributes))

    @staticmethod
    def board_change(attributes):
        return 'Change all orbs to {:s}'.format(', '.join(attributes))

    @staticmethod
    def random_orb_spawn(count, attributes):
        if count == 42:
            return Describe.board_change(attributes)
        else:
            return 'Spawn random {:d} {:s} orbs'.format(count, ', '.join(attributes))

    @staticmethod
    def fixed_orb_spawn(attributes):
        return 'Spawn {:s} orbs in the specified positions'.format(', '.join(attributes))

    @staticmethod
    def skill_delay(min_turns, max_turns):
        if min_turns is None:
            return 'Delay active skills by {:d} turns'.format(max_turns)
        elif max_turns is None or min_turns == max_turns:
            return 'Delay active skills by {:d} turns'.format(min_turns)
        else:
            return 'Delay active skills by {:d}~{:d} turns'.format(min_turns, max_turns)

    @staticmethod
    def orb_lock(count, attributes):
        if count == 42:
            return 'Lock all {:s} orbs'.format(', '.join(attributes))
        else:
            return 'Lock {:d} random {:s} orbs'.format(count, ', '.join(attributes))

    @staticmethod
    def orb_seal(turns, position_type, positions):
        return 'Seal {:s} {:s} for {:d} turns'.format(', '.join([ordinal(x) for x in positions]), position_type, turns)

    @staticmethod
    def cloud(turns, width, height, x, y):
        if width == 6 and height == 1:
            shape = 'Row of'
        elif width == 1 and height == 5:
            shape = 'Column of'
        else:
            shape = '{:d}x{:d}'.format(width, height)
        pos = []
        if x is not None and shape != 'Row of':
            pos.append('{:s} row'.format(ordinal(x)))
        if y is not None and shape != 'Column of':
            pos.append('{:s} column'.format(ordinal(y)))
        if len(pos) == 0:
            pos.append('random location')
        return '{:s} cloud appear for {:d} turns at {:s}'.format(shape, turns, ', '.join(pos))

    @staticmethod
    def turn_change(turn_counter, threshold=None):
        if threshold:
            return 'Enemy turn counter change to {:d} when HP <= {:d}%'.format(turn_counter, threshold)
        else:
            return 'Enemy turn counter change to {:d}'.format(turn_counter)

    @staticmethod
    def attribute_block(turns, attributes):
        return 'Unable to match {:s} orbs for {:d} turns'.format(', '.join(attributes), turns)

    @staticmethod
    def spinners(turns, speed, position_description):
        return '{:s} orbs change every {:.1f}s for {:d} turns'.format(position_description, speed / 100, turns)

    @staticmethod
    def max_hp_change(turns, max_hp, change_type):
        if change_type == 'flat':
            return 'Change player HP to {:d} for {:d} turns'.format(max_hp, turns)
        else:
            return 'Change player HP to {:d}% for {:d} turns'.format(max_hp, turns)

    @staticmethod
    def death_cry(message):
        if message is None:
            return 'Show death effect'
        else:
            return 'Show message: {:s}'.format(message)

    @staticmethod
    def attribute_exists(atts):
        return 'when {:s} orbs are on the board'.format(', '.join(atts))

    @staticmethod
    def countdown(counter):
        return 'Display \'{:d}\' and skip turn'.format(counter)

    @staticmethod
    def gacha_fever(attribute, orb_req):
        return 'Fever Mode: clear {} {} orbs'.format(orb_req, attribute)

    @staticmethod
    def lead_alter(turns, target):
        return 'Change leader to [{}] for {} turns'.format(target, turns)

    @staticmethod
    def no_skyfall(turns):
        return 'No skyfall for {} turns'.format(turns)


# Condition subclass

class ESCondition(object):
    def __init__(self, ai, rnd, params_arr, description=None):
        # If the monster has a hp_threshold value, the % chance is AI+RND under the threshold.
        self._ai = ai
        # The base % chance is rnd.
        self._rnd = rnd
        self.hp_threshold = None if params_arr[11] is None else params_arr[11]
        self.one_time = params_arr[13]
        self.forced_one_time = None
        self.description = description if description else \
            Describe.condition(max(ai, rnd), self.hp_threshold,
                               self.one_time is not None or self.forced_one_time is not None)

        # Force ignore hp threshold on skill if the monster has no AI.
        if self.hp_threshold and self._ai == 0:
            self.hp_threshold = None

        # If set, this only executes when a specified number of enemies remain.
        self.enemies_remaining = None

    def use_chance(self):
        """Returns the likelyhood that this condition will be used.

        If 100, it means it will always activate.
        Note that this implementation is incorrect; it should take a 'current HP' parameter and
        validate that against the hp_threshold. If under, the result should be ai+rnd.
        """
        return max(self._ai, self._rnd)


class ESAttack(object):
    def __init__(self, atk_multiplier, min_hits=1, max_hits=1):
        self.atk_multiplier = atk_multiplier
        self.min_hits = min_hits
        self.max_hits = max_hits

    @staticmethod
    def new_instance(atk_multiplier, min_hits=1, max_hits=1):
        if atk_multiplier is None:
            return None
        else:
            return ESAttack(atk_multiplier, min_hits, max_hits)

    def max_damage_pct(self) -> int:
        return self.atk_multiplier * self.max_hits

    def min_damage_pct(self) -> int:
        return self.atk_multiplier * self.min_hits


class ESBehavior(object):
    """Base class for any kind of enemy behavior, including logic, passives, and actions"""

    def __init__(self, skill: EnemySkill):
        self.enemy_skill_id = es_id(skill)
        self.name = name(skill)
        self.type = es_type(skill)
        self.description = None
        # This might be filled in during the processing step
        self.extra_description = None

        # Shitty hack to avoid passing CrossServerEsBehavior around
        self.jp_name = None


# Action
class ESAction(ESBehavior):
    def full_description(self):
        output = self.description
        if self.description == 'Enemy action':
            output = self.attack.description
        elif self.attack:
            output += ', {:s}'.format(self.attack.description)

        if self.extra_description:
            output += ', {:s}'.format(self.extra_description)

        return output

    def __eq__(self, other):
        return other and self.enemy_skill_id == other.enemy_skill_id

    def __init__(self, skill: EnemySkill, effect='enemy_skill', description='Enemy action', attack=None):
        super().__init__(skill)
        self.CATEGORY = 'ACTION'
        self.effect = effect
        self.description = description
        self.condition = None if ai(skill) is None or rnd(skill) is None \
            else ESCondition(ai(skill), rnd(skill), params(skill))
        self.attack = attack if attack is not None else ESAttack.new_instance(params(skill)[14])
        # param 15 controls displaying sprites on screen, used by Gintama

    def ends_battle(self):
        return False

    def is_conditional(self):
        return False


class ESInactivity(ESAction):
    def __init__(self, skill):
        super().__init__(
            skill,
            effect='skip_turn',
            description=Describe.skip()
        )


class ESDeathCry(ESAction):
    def __init__(self, skill):
        self.message = params(skill)[0]
        super().__init__(
            skill,
            effect='death_action',
            description=Describe.death_cry(self.message)
        )
        if self.condition:
            self.condition.description = 'On death'


class ESAttackSinglehit(ESAction):
    def __init__(self, skill, atk_multiplier=100):
        super().__init__(
            skill,
            effect='attack_single',
            attack=ESAttack.new_instance(atk_multiplier)
        )


class ESDefaultAttack(ESAttackSinglehit):
    """Not a real behavior, used in place of a behavior when none is detected.

    Implies that a monster uses its normal attack.
    """

    def __init__(self):
        super().__init__(ESRef(1, 100, 0))
        self.name = 'Default Attack'


class ESAttackMultihit(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            effect='attack_multi',
            attack=ESAttack.new_instance(params(skill)[3], params(skill)[1], params(skill)[2])
        )


class ESAttackPreemptive(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            effect='attack_preemptive',
            attack=ESAttack.new_instance(params(skill)[2])
        )


class ESBind(ESAction):
    def __init__(self, skill: EnemySkill, target_count=None, target_type_description='cards', attack=None):
        self.min_turns = params(skill)[2]
        self.max_turns = params(skill)[3]
        if target_count:
            self.target_count = target_count
        super().__init__(
            skill,
            effect='bind',
            description=Describe.bind(self.min_turns, self.max_turns,
                                      target_count, target_type_description),
            attack=attack
        )


class ESBindAttack(ESBind):
    def __init__(self, skill: EnemySkill):
        self.targets = bind_bitmap(params(skill)[4])
        super().__init__(
            skill,
            target_count=params(skill)[5],
            target_type_description=', '.join(self.targets),
            attack=ESAttack.new_instance(params(skill)[1]))


class ESBindRandom(ESBind):
    def __init__(self, skill: EnemySkill, target_type_description='random cards'):
        super().__init__(
            skill,
            target_count=params(skill)[1],
            target_type_description=target_type_description)


class ESBindTarget(ESBind):
    def __init__(self, skill: EnemySkill):
        targets = bind_bitmap(params(skill)[1])
        super().__init__(
            skill,
            target_count=len(targets),
            target_type_description=', '.join(targets)
        )


class ESBindRandomSub(ESBindRandom):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, target_type_description='random subs')


class ESBindAttribute(ESBind):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            target_count=None,
            target_type_description='{:s} cards'.format(ATTRIBUTE_MAP[params(skill)[1]]))
        self.target_attribute = ATTRIBUTE_MAP[params(skill)[1]]

    def is_conditional(self):
        return True


class ESBindTyping(ESBind):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            target_count=None,
            target_type_description='{:s} cards'.format(TYPING_MAP[params(skill)[1]]))
        self.target_typing = TYPING_MAP[params(skill)[1]]

    def is_conditional(self):
        return True


class ESBindSkill(ESAction):
    def __init__(self, skill: EnemySkill):
        self.min_turns = params(skill)[1]
        self.max_turns = params(skill)[2]
        super().__init__(
            skill,
            effect='skill_bind',
            description=Describe.bind(self.min_turns, self.max_turns, target_type='active skills')
        )

    def is_conditional(self):
        return True


class ESBindAwoken(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[1]
        super().__init__(
            skill,
            effect='awoken_bind',
            description=Describe.bind(self.turns, None, None, 'awoken skills')
        )

    def is_conditional(self):
        return True


class ESOrbChange(ESAction):
    def __init__(self, skill: EnemySkill, orb_from, orb_to):
        self.orb_from = orb_from
        self.orb_to = orb_to
        super().__init__(
            skill,
            effect='orb_change',
            description=Describe.orb_change(self.orb_from, self.orb_to)
        )

    def is_conditional(self):
        return self.orb_from.lower() != 'random'


class ESOrbChangeConditional(ESOrbChange):
    """Parent class for orb changes that may not execute."""

    def __init__(self, skill: EnemySkill, orb_from, orb_to):
        super().__init__(skill, orb_from, orb_to)

    def is_conditional(self):
        return True


class ESOrbChangeSingle(ESOrbChangeConditional):
    def __init__(self, skill: EnemySkill):
        from_attr = ATTRIBUTE_MAP[params(skill)[1]]
        to_attr = ATTRIBUTE_MAP[params(skill)[2]]
        super().__init__(skill, from_attr, to_attr)


class ESOrbChangeAttackBits(ESOrbChangeConditional):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            orb_from=attribute_bitmap(params(skill)[2]),
            orb_to=attribute_bitmap(params(skill)[3])
        )
        self.attack = ESAttack.new_instance(params(skill)[1])


class ESJammerChangeSingle(ESOrbChangeConditional):
    def __init__(self, skill: EnemySkill):
        from_attr = ATTRIBUTE_MAP[params(skill)[1]]
        to_attr = ATTRIBUTE_MAP[6]
        super().__init__(skill, from_attr, to_attr)

    def is_conditional(self):
        return True


class ESJammerChangeRandom(ESOrbChange):
    def __init__(self, skill: EnemySkill):
        self.random_count = int(params(skill)[1])
        from_attr = 'Random {:d}'.format(self.random_count)
        to_attr = ATTRIBUTE_MAP[6]
        super().__init__(skill, from_attr, to_attr)


class ESPoisonChangeSingle(ESOrbChangeConditional):
    def __init__(self, skill: EnemySkill):
        from_attr = ATTRIBUTE_MAP[params(skill)[1]]
        to_attr = ATTRIBUTE_MAP[7]
        super().__init__(skill, from_attr, to_attr)


class ESPoisonChangeRandom(ESOrbChange):
    def __init__(self, skill: EnemySkill):
        self.random_count = int(params(skill)[1])
        from_attr = 'Random {:d}'.format(self.random_count)
        to_attr = ATTRIBUTE_MAP[7]
        # TODO: This skill (and possibly others) seem to have an 'excludes hearts'
        # clause; either it's innate to this skill, or it's in params[2] (many monsters have
        # a 1 in that slot, not all though).
        super().__init__(skill, from_attr, to_attr)


class ESMortalPoisonChangeRandom(ESOrbChange):
    def __init__(self, skill: EnemySkill):
        self.random_count = int(params(skill)[1])
        from_attr = 'Random {:d}'.format(self.random_count)
        to_attr = ATTRIBUTE_MAP[8]
        super().__init__(skill, from_attr, to_attr)


class ESOrbChangeAttack(ESOrbChange):
    def __init__(self, skill: EnemySkill, orb_from=None, orb_to=None):
        from_attr = ATTRIBUTE_MAP[params(skill)[2]] if orb_from is None else orb_from
        to_attr = ATTRIBUTE_MAP[params(skill)[3]] if orb_to is None else orb_to
        super().__init__(skill, orb_from=from_attr, orb_to=to_attr)
        self.attack = ESAttack.new_instance(params(skill)[1])
        self.effect = 'orb_change_attack'


class ESPoisonChangeRandomAttack(ESOrbChangeAttack):
    def __init__(self, skill: EnemySkill):
        self.random_count = int(params(skill)[2])
        from_attr = 'Random {:d}'.format(self.random_count)
        to_attr = ATTRIBUTE_MAP[7]
        super().__init__(skill, orb_from=from_attr, orb_to=to_attr)

    def is_conditional(self):
        return False


class ESBlind(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            effect='blind',
            description=Describe.blind(),
            attack=ESAttack.new_instance(params(skill)[1])
        )


class ESBlindStickyRandom(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[1]
        self.min_count = params(skill)[2]
        self.max_count = params(skill)[3]
        super().__init__(
            skill,
            effect='blind_sticky_random',
            description=Describe.blind_sticky_random(self.turns, self.min_count, self.max_count)
        )


class ESBlindStickyFixed(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[1]
        self.position_str, self.position_rows, self.position_cols \
            = positions_2d_bitmap(params(skill)[2:7])
        super().__init__(
            skill,
            effect='blind_sticky_fixed',
            description=Describe.blind_sticky_fixed(self.turns)
        )


class ESDispel(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            effect='dispel',
            description='Voids player buff effects'
        )


class ESStatusShield(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[1]
        super().__init__(
            skill,
            effect='status_shield',
            description=Describe.status_shield(self.turns)
        )


class ESRecover(ESAction):
    def __init__(self, skill, target):
        self.min_amount = params(skill)[1]
        self.max_amount = params(skill)[2]
        self.target = target
        super().__init__(
            skill,
            effect='recover',
            description=Describe.recover(self.min_amount, self.max_amount, self.target)
        )


class ESRecoverEnemy(ESRecover):
    def __init__(self, skill):
        super().__init__(skill, target='enemy')


class ESRecoverEnemyAlly(ESRecover):
    def __init__(self, skill):
        super().__init__(skill, target='enemy ally')
        if self.condition:
            self.condition.description = 'When enemy ally is killed'
            self.condition.enemies_remaining = 1


class ESRecoverPlayer(ESRecover):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, target='player')


class ESEnrage(ESAction):
    def __init__(self, skill: EnemySkill, multiplier, turns):
        self.multiplier = multiplier
        self.turns = turns
        super().__init__(
            skill,
            effect='enrage',
            description=Describe.enrage(self.multiplier, self.turns)
        )


class ESStorePower(ESEnrage):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            multiplier=100 + params(skill)[1],
            turns=0
        )


class ESAttackUp(ESEnrage):
    def __init__(self, skill: EnemySkill, multiplier, turns):
        super().__init__(
            skill,
            multiplier=multiplier,
            turns=turns
        )


class ESAttackUPRemainingEnemies(ESAttackUp):
    def __init__(self, skill: EnemySkill):
        self.enemy_count = params(skill)[1]
        super().__init__(
            skill,
            multiplier=params(skill)[3],
            turns=params(skill)[2]
        )
        if self.condition and self.enemy_count:
            if self.condition.description:
                self.condition.description += ', when <= {} enemies remain'.format(self.enemy_count)
            else:
                self.condition.description = 'when <= {} enemies remain'.format(self.enemy_count)


class ESAttackUpStatus(ESAttackUp):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            multiplier=params(skill)[2],
            turns=params(skill)[1]
        )
        if self.condition:
            if self.condition.description:
                self.condition.description += ', after being affected by a status effect'
            else:
                self.condition.description = 'after being affected by a status effect'


class ESAttackUPCooldown(ESAttackUp):
    def __init__(self, skill: EnemySkill):
        # enrage cannot trigger until this many turns have passed
        cooldown_value = params(skill)[1] or 0
        self.turn_cooldown = cooldown_value if cooldown_value > 1 else None
        super().__init__(
            skill,
            multiplier=params(skill)[3],
            turns=params(skill)[2]
        )
        if self.condition and self.turn_cooldown:
            if self.condition.description:
                self.condition.description += ', after {} turns'.format(self.turn_cooldown)
            else:
                self.condition.description = 'after {} turns'.format(self.turn_cooldown)


class ESDebuff(ESAction):
    def __init__(self, skill: EnemySkill, debuff_type, amount, unit):
        self.turns = params(skill)[1]
        self.type = debuff_type
        self.amount = amount or 0
        self.unit = unit
        super().__init__(
            skill,
            effect='debuff',
            description=Describe.debuff(self.type, self.amount, self.unit, self.turns)
        )


class ESDebuffMovetime(ESDebuff):
    def __init__(self, skill: EnemySkill):
        if params(skill)[2] is not None:
            super().__init__(
                skill,
                debuff_type='movetime',
                amount=-params(skill)[2] / 10,
                unit='s'
            )
        elif params(skill)[3] is not None:
            super().__init__(
                skill,
                debuff_type='movetime',
                amount=params(skill)[3],
                unit='%'
            )


class ESDebuffRCV(ESDebuff):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            debuff_type='RCV',
            amount=params(skill)[2],
            unit='%'
        )


class ESEndBattle(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            effect='end_battle',
            description=Describe.end_battle()
        )
        if self.condition:
            self.condition.chance = 100

    def ends_battle(self):
        return True


class ESChangeAttribute(ESAction):
    def __init__(self, skill: EnemySkill):
        self.attributes = list(OrderedDict.fromkeys([ATTRIBUTE_MAP[x] for x in params(skill)[1:6]]))
        super().__init__(
            skill,
            effect='change_attribute',
            description=Describe.change_attribute(self.attributes)
        )


class ESGravity(ESAction):
    def __init__(self, skill: EnemySkill):
        self.percent = params(skill)[1]
        super().__init__(
            skill,
            effect='gravity',
            description=Describe.gravity(self.percent)
        )


class ESAbsorb(ESAction):
    def __init__(self, skill: EnemySkill, source, effect='absorb'):
        self.min_turns = params(skill)[1]
        self.max_turns = params(skill)[2]
        super().__init__(
            skill,
            effect=effect,
            description=Describe.absorb(source, self.min_turns, self.max_turns)
        )


class ESAbsorbAttribute(ESAbsorb):
    def __init__(self, skill: EnemySkill):
        self.attributes = attribute_bitmap(params(skill)[3])
        super().__init__(
            skill,
            ', '.join(self.attributes),
            effect='absorb_attribute'
        )


class ESAbsorbCombo(ESAbsorb):
    def __init__(self, skill: EnemySkill):
        self.combo_threshold = params(skill)[3]
        super().__init__(
            skill,
            'combo <= {:,d}'.format(self.combo_threshold),
            effect='absorb_combo'
        )


class ESAbsorbThreshold(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[1]
        self.absorb_threshold = params(skill)[2]
        super().__init__(
            skill,
            effect='absorb_damage',
            description=Describe.absorb('damage >= {}'.format(self.absorb_threshold), self.turns)
        )


class ESVoidShield(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[1]
        # mysterious params[2], always 1055 except for no.2485 Hakumen no Mono who has 31
        self.void_threshold = params(skill)[3]
        super().__init__(
            skill,
            effect='void_damage',
            description=Describe.void(self.void_threshold, self.turns)
        )


class ESDamageShield(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[1]
        self.shield_percent = params(skill)[2]
        super().__init__(
            skill,
            effect='reduce_damage',
            description=Describe.damage_reduction('all sources', self.shield_percent, self.turns)
        )


class ESInvulnerableOn(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[1]
        super().__init__(
            skill,
            effect='invulnerability_on',
            description=Describe.damage_reduction('all sources', turns=self.turns)
        )


class ESInvulnerableOff(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            effect='invulnerability_off',
            description='Remove damage immunity effect'
        )


class ESSkyfall(ESAction):
    def __init__(self, skill: EnemySkill):
        self.min_turns = params(skill)[2]
        self.max_turns = params(skill)[3]
        self.attributes = attribute_bitmap(params(skill)[1])
        self.chance = params(skill)[4]
        if es_type(skill) == 68:
            super().__init__(
                skill,
                effect='skyfall_increase',
                description=Describe.skyfall(self.attributes, self.chance,
                                             self.min_turns, self.max_turns)
            )
        elif es_type(skill) == 96:
            super().__init__(
                skill,
                effect='skyfall_lock',
                description=Describe.skyfall(self.attributes, self.chance,
                                             self.min_turns, self.max_turns, True)
            )


class ESLeaderSwap(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = self.turns = params(skill)[1]
        super().__init__(
            skill,
            effect='swap_leader',
            description=Describe.leadswap(self.turns)
        )


class ESFixedOrbSpawn(ESAction):
    def __init__(self, skill: EnemySkill, position_type, positions, attributes, description, attack=None):
        self.position_type = position_type
        self.positions = positions
        self.attributes = attributes
        super().__init__(
            skill,
            effect='row_col_spawn',
            description=description,
            attack=attack
        )


class ESRowColSpawn(ESFixedOrbSpawn):
    def __init__(self, skill: EnemySkill, position_type):
        super().__init__(
            skill,
            position_type=position_type,
            positions=position_bitmap(params(skill)[1]),
            attributes=attribute_bitmap(params(skill)[2]),
            description=Describe.row_col_spawn(
                position_type,
                position_bitmap(params(skill)[1]),
                attribute_bitmap(params(skill)[2])
            )
        )


class ESRowColSpawnMulti(ESFixedOrbSpawn):
    RANGE_MAP = {
        76: range(1, 4, 2),
        77: range(1, 6, 2),
        78: range(1, 4, 2),
        79: range(1, 6, 2)
    }

    def __init__(self, skill: EnemySkill, position_type):
        desc_arr = []
        pos = []
        att = []
        for i in self.RANGE_MAP[es_type(skill)]:
            if params(skill)[i] and params(skill)[i + 1]:
                p = position_bitmap(params(skill)[i])
                a = attribute_bitmap(params(skill)[i + 1])
                desc_arr.append(Describe.row_col_spawn(position_type, p, a)[7:])
                pos += p
                att += a
        super().__init__(
            skill,
            position_type=position_type,
            positions=pos,
            attributes=att,
            description='Change ' + ', '.join(desc_arr),
            attack=ESAttack.new_instance(params(skill)[7]) if es_type(skill) in [77, 79] else None
        )


class ESColumnSpawn(ESRowColSpawn):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            position_type='column'
        )


class ESColumnSpawnMulti(ESRowColSpawnMulti):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            position_type='column'
        )


class ESRowSpawn(ESRowColSpawn):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            position_type='row'
        )


class ESRowSpawnMulti(ESRowColSpawnMulti):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            position_type='row'
        )


class ESRandomSpawn(ESAction):
    def __init__(self, skill: EnemySkill):
        self.count = params(skill)[1]
        self.attributes = attribute_bitmap(params(skill)[2])
        self.condition_attributes = attribute_bitmap(params(skill)[3], inverse=True)

        super().__init__(
            skill,
            effect='random_orb_spawn',
            description=Describe.random_orb_spawn(self.count, self.attributes)
        )
        if self.condition and self.condition_attributes:
            if self.condition.description:
                self.condition.description += " & " + \
                                              Describe.attribute_exists(self.condition_attributes)
            else:
                self.condition.description = Describe.attribute_exists(
                    self.condition_attributes).capitalize()

    def is_conditional(self):
        return len(self.condition_attributes or []) < 6


class ESBombRandomSpawn(ESAction):
    def __init__(self, skill: EnemySkill):
        self.count = params(skill)[2]
        self.locked = params(skill)[8] == 1
        super().__init__(
            skill,
            effect='random_bomb_spawn',
            description=Describe.random_orb_spawn(
                self.count, ['locked Bomb'] if self.locked else ['Bomb'])
        )


class ESBombFixedSpawn(ESAction):
    def __init__(self, skill: EnemySkill):
        self.count = params(skill)[2]
        self.position_str, self.position_rows, self.position_cols = positions_2d_bitmap(params(skill)[2:7])
        self.locked = params(skill)[8] == 1
        super().__init__(
            skill,
            effect='fixed_bomb_spawn',
            description=Describe.board_change(['locked Bomb'] if self.locked else ['Bomb'])
            if self.position_rows is not None and len(self.position_rows) == 6
               and self.position_cols is not None and len(self.position_cols) == 5
            else Describe.fixed_orb_spawn(['locked Bomb'] if self.locked else ['Bomb'])
        )


class ESBoardChange(ESAction):
    def __init__(self, skill: EnemySkill, attributes=None, attack=None):
        if attributes:
            self.attributes = attributes
        else:
            self.attributes = attribute_bitmap(params(skill)[1])
        super().__init__(
            skill,
            effect='board_change',
            description=Describe.board_change(self.attributes),
            attack=attack
        )


class ESBoardChangeAttackFlat(ESBoardChange):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            [ATTRIBUTE_MAP[x] for x in params(skill)[2:params(skill).index(-1)]],
            ESAttack.new_instance(params(skill)[1])
        )


class ESBoardChangeAttackBits(ESBoardChange):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            attribute_bitmap(params(skill)[2]),
            ESAttack.new_instance(params(skill)[1])
        )


class SubSkill(object):
    def __init__(self, enemy_skill_id):
        self.enemy_skill_id = enemy_skill_id
        self.enemy_skill_info = enemy_skill_map[enemy_skill_id]
        self.enemy_ai = None
        self.enemy_rnd = None


class ESSkillSet(ESAction):
    def __init__(self, skill: EnemySkill):
        self.skill_list = []  # List[ESAction]
        i = 0
        for s in params(skill)[1:11]:
            if s is not None:
                sub_skill = ESRef(s, 0, 0)
                if es_type(sub_skill) in BEHAVIOR_MAP:
                    behavior = BEHAVIOR_MAP[es_type(sub_skill)](sub_skill)
                    self.skill_list.append(behavior)
                else:
                    self.skill_list.append(EnemySkillUnknown(sub_skill))
            i += 1
        super().__init__(
            skill,
            effect='skill_set',
            description='Perform multiple skills'
        )

        self.name = ' + '.join(map(lambda s: s.name, self.skill_list))

    def full_description(self):
        output = ' + '.join(map(lambda s: s.full_description(), self.skill_list))
        if self.extra_description:
            output += ', {:s}'.format(self.extra_description)
        return output

    def ends_battle(self):
        return any([s.ends_battle() for s in self.skill_list])


class ESSkillSetOnDeath(ESSkillSet):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        if self.condition:
            self.condition.description = 'On death'

    def has_action(self) -> bool:
        """Helper that determines if the skillset does stuff other than emote."""
        for x in self.skill_list:
            if type(x) == ESSkillSet:
                if any([type(y) != ESInactivity for y in x.skill_list]):
                    return True
            elif type(x) != ESInactivity:
                return True
        return False


class ESSkillDelay(ESAction):
    def __init__(self, skill: EnemySkill):
        self.min_turns = params(skill)[1]
        self.max_turns = params(skill)[2]
        super().__init__(
            skill,
            effect='skill_delay',
            description=Describe.skill_delay(self.min_turns, self.max_turns)
        )


class ESOrbLock(ESAction):
    def __init__(self, skill: EnemySkill):
        self.count = params(skill)[2]
        self.attributes = attribute_bitmap(params(skill)[1])
        super().__init__(
            skill,
            effect='orb_lock',
            description=Describe.orb_lock(self.count, self.attributes)
        )

    def is_conditional(self):
        return self.attributes != ['random'] and len(self.attributes) != 9


class ESOrbSeal(ESAction):
    def __init__(self, skill: EnemySkill, position_type, positions):
        self.turns = params(skill)[2]
        self.position_type = position_type
        self.positions = positions
        super().__init__(
            skill,
            effect='orb_seal',
            description=Describe.orb_seal(self.turns, self.position_type, self.positions)
        )


class ESOrbSealColumn(ESOrbSeal):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            position_type='column',
            positions=position_bitmap(params(skill)[1])
        )


class ESOrbSealRow(ESOrbSeal):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            position_type='row',
            positions=position_bitmap(params(skill)[1])
        )


class ESCloud(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[1]
        self.cloud_width = params(skill)[2]
        self.cloud_height = params(skill)[3]
        self.origin_y = params(skill)[4]
        self.origin_x = params(skill)[5]
        super().__init__(
            skill,
            effect='cloud',
            description=Describe.cloud(
                self.turns, self.cloud_width, self.cloud_height, self.origin_x, self.origin_y)
        )


class ESFixedStart(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            effect='fixed_start',
            description='Fix orb movement starting point to random position on the board'
        )


class ESAttributeBlock(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[1]
        self.attributes = attribute_bitmap(params(skill)[2])
        super().__init__(
            skill,
            effect='attribute_block',
            description=Describe.attribute_block(self.turns, self.attributes)
        )


class ESSpinners(ESAction):
    def __init__(self, skill: EnemySkill, position_type, position_description):
        self.turns = params(skill)[1]
        self.speed = params(skill)[2]
        self.position_type = position_type
        super().__init__(
            skill,
            effect='orb_spinners',
            description=Describe.spinners(self.turns, self.speed, position_description)
        )


class ESSpinnersRandom(ESSpinners):
    def __init__(self, skill: EnemySkill):
        self.count = params(skill)[3]
        super().__init__(
            skill,
            position_type='random',
            position_description='Random {:d}'.format(self.count)
        )


class ESSpinnersFixed(ESSpinners):
    def __init__(self, skill: EnemySkill):
        self.position_str, self.position_rows, self.position_cols = positions_2d_bitmap(params(skill)[3:8])
        super().__init__(
            skill,
            position_type='fixed',
            position_description='Specific'
        )


class ESMaxHPChange(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[3]
        if params(skill)[1] is not None:
            self.max_hp = params(skill)[1]
            self.hp_change_type = 'percent'
        elif params(skill)[2] is not None:
            self.max_hp = params(skill)[2]
            self.hp_change_type = 'flat'
        super().__init__(
            skill,
            effect='max_hp_change',
            description=Describe.max_hp_change(self.turns, self.max_hp, self.hp_change_type)
        )


class ESFixedTarget(ESAction):
    def __init__(self, skill: EnemySkill):
        self.target = params(skill)[1]
        super().__init__(
            skill,
            effect='fixed_target',
            description='Forces attacks to hit this enemy'
        )


class ESTurnChangeActive(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turn_counter = params(skill)[2]
        self.enemy_seq = params(skill)[1]
        super().__init__(
            skill,
            effect='turn_change_active',
            description=Describe.turn_change(self.turn_counter)
        )


class ESGachaFever(ESAction):
    def __init__(self, skill: EnemySkill):
        self.attribute = ATTRIBUTE_MAP[params(skill)[1]]
        self.orb_req = params(skill)[2]
        super().__init__(
            skill,
            description=Describe.gacha_fever(self.attribute, self.orb_req)
        )


class ESLeaderAlter(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[1]
        self.target_card = params(skill)[2]
        super().__init__(
            skill,
            description=Describe.lead_alter(self.turns, self.target_card)
        )


class ESNoSkyfall(ESAction):
    def __init__(self, skill: EnemySkill):
        self.turns = params(skill)[2]
        super().__init__(
            skill,
            description=Describe.no_skyfall(self.turns)
        )


# Passive
class ESPassive(ESBehavior):
    def full_description(self):
        return self.description

    def __init__(self, skill: EnemySkill, effect, description):
        super().__init__(skill)
        self.CATEGORY = 'PASSIVE'
        self.effect = effect
        self.description = description


class ESAttributeResist(ESPassive):
    def __init__(self, skill: EnemySkill):
        self.attributes = attribute_bitmap(params(skill)[1])
        self.shield_percent = params(skill)[2]
        super().__init__(
            skill,
            effect='resist_attribute',
            description=Describe.damage_reduction(
                ', '.join(self.attributes), percent=self.shield_percent)
        )


class ESResolve(ESPassive):
    def __init__(self, skill: EnemySkill):
        self.hp_threshold = params(skill)[1]
        super().__init__(
            skill,
            effect='resolve',
            description=Describe.resolve(self.hp_threshold)
        )


class ESTurnChangePassive(ESPassive):
    def __init__(self, skill: EnemySkill):
        self.hp_threshold = params(skill)[1]
        self.turn_counter = params(skill)[2]
        super().__init__(
            skill,
            effect='turn_change_passive',
            description=Describe.turn_change(self.turn_counter, self.hp_threshold)
        )


class ESTypeResist(ESPassive):
    def __init__(self, skill: EnemySkill):
        self.types = typing_bitmap(params(skill)[1])
        self.shield_percent = params(skill)[2]
        super().__init__(
            skill,
            effect='resist_type',
            description=Describe.damage_reduction(
                ', '.join(self.types), percent=self.shield_percent)
        )


# Logic
class ESLogic(ESBehavior):
    def __init__(self, skill: EnemySkill, effect=None):
        self.CATEGORY = 'LOGIC'
        self.enemy_skill_id = es_id(skill)
        self.effect = effect
        self.type = es_type(skill)

    @property
    def name(self):
        return type(self).__name__

    @property
    def description(self):
        return self.effect

    def full_description(self):
        return self.effect


class ESNone(ESLogic):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, 'nothing')


class ESFlagOperation(ESLogic):
    FLAG_OPERATION_MAP = {
        22: 'SET',
        24: 'UNSET',
        44: 'OR',
        45: 'XOR'
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(skill, effect='flag_operation')
        self.flag = ai(skill)
        self.flag_bin = bin(self.flag)
        self.operation = self.FLAG_OPERATION_MAP[es_type(skill)]

    @property
    def description(self):
        return 'flag {} {}'.format(self.operation, self.flag_bin)


class ESSetCounter(ESLogic):
    COUNTER_SET_MAP = {
        25: '=',
        26: '+',
        27: '-'
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(skill, effect='set_counter')
        self.counter = ai(skill) if es_type(skill) == 25 else 1
        self.set = self.COUNTER_SET_MAP[es_type(skill)]

    @property
    def description(self):
        return 'counter {} {}'.format(self.set, self.counter)


class ESSetCounterIf(ESLogic):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, effect='set_counter_if')
        self.effect = 'set_counter_if'
        self.counter_is = ai(skill)
        self.counter = rnd(skill)

    @property
    def description(self):
        return 'set counter = {} if counter == {}'.format(self.counter, self.counter_is)


class ESBranch(ESLogic):
    def __init__(self, skill: EnemySkill, branch_condition, compare='='):
        self.branch_condition = branch_condition
        self.branch_value = ai(skill)
        self.target_round = rnd(skill)
        self.compare = compare
        super().__init__(skill, effect='branch')

    @property
    def description(self):
        return 'Branch on {} {} {}, target rnd {}'.format(
            self.branch_condition, self.compare, str(self.branch_value), self.target_round)


class ESBranchFlag(ESBranch):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            branch_condition='flag',
            compare='&'
        )


class ESBranchHP(ESBranch):
    HP_COMPARE_MAP = {
        28: '<',
        29: '>'
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            branch_condition='hp',
            compare=self.HP_COMPARE_MAP[es_type(skill)]
        )


class ESBranchCounter(ESBranch):
    COUNTER_COMPARE_MAP = {
        30: '<',
        31: '=',
        32: '>'
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            branch_condition='counter',
            compare=self.COUNTER_COMPARE_MAP[es_type(skill)]
        )


class ESBranchLevel(ESBranch):
    LEVEL_COMPARE_MAP = {
        33: '<',
        34: '=',
        35: '>'
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            branch_condition='level',
            compare=self.LEVEL_COMPARE_MAP[es_type(skill)]
        )


class ESEndPath(ESLogic):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, effect='end_turn')


class ESCountdown(ESLogic):
    def __init__(self, skill: EnemySkill):
        # decrement counter and end path
        super().__init__(skill, effect='countdown')


class ESCountdownMessage(ESAction):
    """Dummy action class to represent displaying countdown numbers"""

    def __init__(self, enemy_skill_id, current_counter=0):
        super(ESCountdownMessage, self).__init__(ESRef(enemy_skill_id, 0, 0))
        self.enemy_skill_id += 1000 * current_counter
        self.current_counter = current_counter
        self.name = 'Countdown Message'
        self.description = Describe.countdown(self.current_counter)


class ESPreemptive(ESLogic):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, effect='preemptive')
        self.level = params(skill)[1]

    @property
    def description(self):
        return 'Enable preempt if level {}'.format(self.level)


class ESBranchCard(ESBranch):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, branch_condition='player_cards', compare='HAS')
        self.branch_value = [x for x in params(skill) if x is not None]


class ESBranchCombo(ESBranch):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, branch_condition='combo', compare='>=')


class ESBranchRemainingEnemies(ESBranch):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, branch_condition='remaining enemies', compare='<=')


# Unknown
class EnemySkillUnknown(ESBehavior):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.description = 'unknown'

    def full_description(self):
        return self.description

    def ends_battle(self):
        return False


BEHAVIOR_MAP = {
    # SKILLS
    1: ESBindRandom,
    2: ESBindAttribute,
    3: ESBindTyping,
    4: ESOrbChangeSingle,
    5: ESBlind,
    6: ESDispel,
    7: ESRecoverEnemy,
    8: ESStorePower,
    # type 9 skills are unused, but there's 3 and they seem to buff defense
    12: ESJammerChangeSingle,
    13: ESJammerChangeRandom,
    14: ESBindSkill,
    15: ESAttackMultihit,
    16: ESInactivity,
    17: ESAttackUPRemainingEnemies,
    18: ESAttackUpStatus,
    19: ESAttackUPCooldown,
    20: ESStatusShield,
    39: ESDebuffMovetime,
    40: ESEndBattle,
    46: ESChangeAttribute,
    47: ESAttackPreemptive,
    48: ESOrbChangeAttack,
    50: ESGravity,
    52: ESRecoverEnemyAlly,
    53: ESAbsorbAttribute,
    54: ESBindTarget,
    55: ESRecoverPlayer,
    56: ESPoisonChangeSingle,
    60: ESPoisonChangeRandom,
    61: ESMortalPoisonChangeRandom,
    62: ESBlind,
    63: ESBindAttack,
    64: ESPoisonChangeRandomAttack,
    65: ESBindRandomSub,
    66: ESInactivity,
    67: ESAbsorbCombo,
    68: ESSkyfall,
    69: ESDeathCry,
    71: ESVoidShield,
    74: ESDamageShield,
    75: ESLeaderSwap,
    76: ESColumnSpawnMulti,
    77: ESColumnSpawnMulti,
    78: ESRowSpawnMulti,
    79: ESRowSpawnMulti,
    81: ESBoardChangeAttackFlat,
    82: ESAttackSinglehit,  # called "Disable Skill" in EN but "Normal Attack" in JP
    83: ESSkillSet,
    84: ESBoardChange,
    85: ESBoardChangeAttackBits,
    86: ESRecoverEnemy,
    87: ESAbsorbThreshold,
    88: ESBindAwoken,
    89: ESSkillDelay,
    92: ESRandomSpawn,
    93: ESNone,  # FF animation (???)
    94: ESOrbLock,
    95: ESSkillSetOnDeath,
    96: ESSkyfall,
    97: ESBlindStickyRandom,
    98: ESBlindStickyFixed,
    99: ESOrbSealColumn,
    100: ESOrbSealRow,
    101: ESFixedStart,
    102: ESBombRandomSpawn,
    103: ESBombFixedSpawn,
    104: ESCloud,
    105: ESDebuffRCV,
    107: ESAttributeBlock,
    108: ESOrbChangeAttackBits,
    109: ESSpinnersRandom,
    110: ESSpinnersFixed,
    111: ESMaxHPChange,
    112: ESFixedTarget,
    119: ESInvulnerableOn,
    121: ESInvulnerableOff,
    122: ESTurnChangeActive,
    123: ESInvulnerableOn,  # hexa's invulnerable gets special type because reasons
    124: ESGachaFever,  # defines number & type of orbs needed in fever mode
    125: ESLeaderAlter,
    127: ESNoSkyfall,

    # LOGIC
    0: ESNone,
    22: ESFlagOperation,
    23: ESBranchFlag,
    24: ESFlagOperation,
    25: ESSetCounter,
    26: ESSetCounter,
    27: ESSetCounter,
    28: ESBranchHP,
    29: ESBranchHP,
    30: ESBranchCounter,
    31: ESBranchCounter,
    32: ESBranchCounter,
    33: ESBranchLevel,
    34: ESBranchLevel,
    35: ESBranchLevel,
    36: ESEndPath,
    37: ESCountdown,
    38: ESSetCounterIf,
    43: ESBranchFlag,
    44: ESFlagOperation,
    45: ESFlagOperation,
    49: ESPreemptive,
    90: ESBranchCard,
    113: ESBranchCombo,
    120: ESBranchRemainingEnemies,

    # PASSIVES
    72: ESAttributeResist,
    73: ESResolve,
    106: ESTurnChangePassive,
    118: ESTypeResist,
}


def inject_implicit_onetime(card: Card, behavior: List[ESAction]):
    """Injects one_time values into specific categories of skills.

    Currently only ESBindRandom but other early skills may need this.
    This seems to fix things like Hera-Is and others, but breaks some like Metatron Tama.

    TODO: Investigate if this has an ai/rnd interaction, like the hp_threshold issue.
    There may be some interaction with slots 52/53/54 to take into account but unclear.
    """
    if card.enemy_skill_counter_increment != 0:
        # This seems unlikely to be correct.
        return
    max_flag = max([0] + [x.condition.one_time for x in behavior if hasattr(x, 'condition') and x.condition.one_time])
    next_flag = pow(2, ceil(log(max_flag + 1) / log(2)))
    for b in behavior:
        if type(b) in [ESBindRandom, ESBindAttribute] and not b.condition.one_time and b.condition.use_chance() == 100:
            b.condition.forced_one_time = next_flag
            next_flag = next_flag << 1
