import copy
import logging
from abc import ABC
from builtins import issubclass
from collections import OrderedDict
from typing import List, Optional

from pad.common.pad_util import Printable
from pad.raw import EnemySkill
from pad.raw.card import ESRef, Card
from pad.raw.enemy_skills.enemy_skill_text import *

human_fix_logger = logging.getLogger('human_fix')


def attribute_bitmap(bits, inverse=False, bit_len=9):
    if bits is None:
        return []
    if bits == -1:
        return [-1]
    offset = 0
    atts = []
    while offset < bit_len:
        if inverse:
            if (bits >> offset) & 1 == 0:
                atts.append(offset)
        else:
            if (bits >> offset) & 1 == 1:
                atts.append(offset)
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
            types.append(offset)
        offset += 1
    return types


def bind_bitmap(bits) -> List[TargetType]:
    if bits is None:
        return [TargetType.random]
    targets = []
    if (bits >> 0) & 1 == 1:
        targets.append(TargetType.self_leader)
    if (bits >> 1) & 1 == 1:
        if len(targets) > 0:
            targets = [TargetType.both_leader]
        else:
            targets.append(TargetType.friend_leader)
    if (bits >> 2) & 1 == 1:
        targets.append(TargetType.subs)
    return targets


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


# Condition subclass

class ESCondition(object):
    def __init__(self, ai, rnd, params_arr):
        # If the monster has a hp_threshold value, the % chance is AI+RND under the threshold.
        self._ai = ai
        # The base % chance is rnd.
        self._rnd = rnd
        self.hp_threshold = params_arr[11]
        self.one_time = params_arr[13]
        self.forced_one_time = None

        # Force ignore hp threshold on skill if the monster has no AI.
        if self.hp_threshold and self._ai == 0:
            self.hp_threshold = None

        # If set, this only executes when a specified number of enemies remain.
        self.enemies_remaining = None

        # If set, this only executes when the enemy is defeated.
        self.on_death = None

        # Only executes if these attributes are present
        self.condition_attributes = []  # type List[int]

        # Only executes if certain cards are on the team
        self.cards_on_team = []  # type List[int]

        # Only executes if a certain combo count was met
        self.combos_made = None

    def use_chance(self, hp: int = 100):
        """Returns the likelihood that this condition will be used.

        If 100, it means it will always activate. If a HP threshold is present, RND should
        be interpreted as the 'base chance' and the 'under threshold' chance is AI + RND.
        """
        max_chance = min(int(self._ai + (100 - self._ai) * self._rnd / 100), 100)
        min_chance = min(self._rnd, 100)
        if self.hp_threshold:
            if hp < self.hp_threshold:
                return max_chance
            elif self._ai >= 100:
                # This case literally only affects Avowed Thief, Ishikawa Goemon
                # This is probably wrong but still fixes him.
                return 0
            else:
                return min_chance
        return max_chance

    def description(self):
        desc = Describe.condition(max(self._ai, self._rnd), self.hp_threshold,
                                  self.one_time is not None or self.forced_one_time is not None)
        # TODO: figure out if this is still needed
        if self.enemies_remaining:
            desc = desc + ', ' if desc else ''
            enemies = 1 if self.enemies_remaining > 10 else self.enemies_remaining
            desc += 'when <= {} enemies remain'.format(enemies)
        if self.on_death:
            desc = desc + ', ' if desc else ''
            desc += 'on death'
            desc = desc.capitalize()

        if self.condition_attributes:
            if desc:
                desc += " & " + Describe.attribute_exists(self.condition_attributes)
            else:
                desc = Describe.attribute_exists(self.condition_attributes).capitalize()

            # TODO: tieout
            # desc = desc.capitalize()

        return desc


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

    def describe(self):
        return Describe.attack(self.atk_multiplier, self.min_hits, self.max_hits)


class ESBehavior(Printable):
    """Base class for any kind of enemy behavior, including logic, passives, and actions"""

    def __init__(self, skill: EnemySkill):
        self.enemy_skill_id = skill.enemy_skill_id
        self._name = skill.name
        self.type = skill.type
        self.params = skill.params

    @property
    def name(self):
        return self._name

    def ends_battle(self):
        return False

    def is_conditional(self):
        return False

    def description(self):
        return Describe.not_set()

    def full_description(self):
        return self.description()

    def __str__(self):
        return '{}({} - {}: {})'.format(self.__class__.__name__,
                                        self.enemy_skill_id, self.type, self.name)

    def __eq__(self, other):
        return other and self.enemy_skill_id == other.enemy_skill_id


class ESDeathAction(object):
    """This is just a marker class for death actions."""

    def has_action(self) -> bool:
        return False


# Action
class ESAction(ESBehavior):
    def __init__(self, skill: EnemySkill, attack=None):
        super().__init__(skill)
        self._attack = attack if attack is not None else ESAttack.new_instance(self.params[14])
        # param 15 controls displaying sprites on screen, used by Gintama

    @property
    def attack(self):
        return self._attack

    @attack.setter
    def attack(self, value):
        self._attack = value

    def full_description(self):
        if isinstance(self, ESBehaviorAttack):
            return self.description()
        elif self.attack:
            return '{}, {:s}'.format(self.description(), self.attack.describe())
        else:
            return self.description()


class ESBehaviorAttack(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self):
        return Describe.attack(self.attack.atk_multiplier, self.attack.min_hits, self.attack.max_hits)


class ESInactivity(ESAction):
    def __init__(self, skill):
        super().__init__(skill)

    def description(self):
        return Describe.skip()


class ESDeathCry(ESDeathAction, ESAction):
    def __init__(self, skill):
        super().__init__(skill)
        self.message = self.params[0]

    def description(self):
        return Describe.death_cry(self.message)


class ESAttackSinglehit(ESBehaviorAttack):
    def __init__(self, skill):
        super().__init__(skill)
        self.attack = ESAttack.new_instance(100)


class ESDefaultAttack(ESAttackSinglehit):
    """Not a real behavior, used in place of a behavior when none is detected.

    Implies that a monster uses its normal attack.
    """

    def __init__(self):
        raw = ['-2', Describe.default_attack(), '-2', '0']
        dummy_skill = EnemySkill(raw)
        super().__init__(dummy_skill)


class ESAttackMultihit(ESBehaviorAttack):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attack = ESAttack.new_instance(self.params[3], self.params[1], self.params[2])


class ESAttackPreemptive(ESBehaviorAttack):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attack = ESAttack.new_instance(self.params[2])


class ESBind(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.min_turns = self.params[2]
        self.max_turns = self.params[3]
        self.target_count = None
        self.targets = [TargetType.unset]

    def description(self):
        return Describe.bind(self.min_turns, self.max_turns,
                             self.target_count, self.targets)


class ESBindAttack(ESBind):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.targets = bind_bitmap(self.params[4])
        self.target_count = self.params[5]
        self.attack = ESAttack.new_instance(self.params[1])


class ESBindRandom(ESBind):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.target_count = self.params[1]
        self.targets = TargetType.random


class ESBindTarget(ESBind):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.targets = bind_bitmap(self.params[1])
        self.target_count = len(self.targets)


class ESBindRandomSub(ESBindRandom):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.targets = TargetType.subs


class ESBindAttribute(ESBind):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.target_attribute = self.params[1]
        self.targets = [TargetType.attributes]

    def is_conditional(self):
        return True

    def description(self):
        target_type = attributes_to_str([self.target_attribute])
        return Describe.bind(self.min_turns, self.max_turns, target_types=target_type)


class ESBindTyping(ESBind):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.target_typing = self.params[1]
        self.targets = [TargetType.types]

    def is_conditional(self):
        return True

    def description(self):
        target_type = typing_to_str([self.target_typing])
        return Describe.bind(self.min_turns, self.max_turns, target_types=target_type)


class ESBindSkill(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.min_turns = self.params[1]
        self.max_turns = self.params[2]

    def is_conditional(self):
        return True

    def description(self):
        return Describe.bind(self.min_turns, self.max_turns, target_types=TargetType.actives)


class ESBindAwoken(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]

    def is_conditional(self):
        return True

    def description(self):
        return Describe.bind(self.turns, None, None, target_types=TargetType.awokens)


class ESOrbChange(ESAction):
    def __init__(self, skill: EnemySkill, orb_from, orb_to):
        super().__init__(skill)
        self.orb_from = orb_from
        self.orb_to = orb_to
        self.random_count = None
        self.exclude_hearts = None

    def is_conditional(self):
        return self.orb_from != -1

    def description(self):
        return Describe.orb_change(self.orb_from, self.orb_to,
                                   random_count=self.random_count, exclude_hearts=self.exclude_hearts)


# Prototype
class ESOrbChangeConditional(ABC, ESOrbChange):
    def __init__(self, skill: EnemySkill, orb_from, orb_to):
        super().__init__(skill, orb_from, orb_to)

    def is_conditional(self):
        return True


class ESOrbChangeSingle(ESOrbChangeConditional):
    def __init__(self, skill: EnemySkill):
        from_attr = skill.params[1]
        to_attr = skill.params[2]
        super().__init__(skill, from_attr, to_attr)


class ESOrbChangeAttackBits(ESOrbChangeConditional):
    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            orb_from=attribute_bitmap(skill.params[2]),
            orb_to=attribute_bitmap(skill.params[3]))
        self.attack = ESAttack.new_instance(self.params[1])


class ESJammerChangeSingle(ESOrbChangeConditional):
    def __init__(self, skill: EnemySkill):
        from_attr = skill.params[1]
        to_attr = 6
        super().__init__(skill, from_attr, to_attr)

    def is_conditional(self):
        return True


class ESJammerChangeRandom(ESOrbChange):
    def __init__(self, skill: EnemySkill):
        from_attr = -1
        to_attr = 6
        super().__init__(skill, from_attr, to_attr)
        self.random_count = int(skill.params[1])


class ESPoisonChangeSingle(ESOrbChangeConditional):
    def __init__(self, skill: EnemySkill):
        from_attr = skill.params[1]
        to_attr = 7
        super().__init__(skill, from_attr, to_attr)


class ESPoisonChangeRandom(ESOrbChange):
    def __init__(self, skill: EnemySkill):
        from_attr = -1
        to_attr = 7
        super().__init__(skill, from_attr, to_attr)
        self.exclude_hearts = self.params[2] == 1


class ESPoisonChangeRandomCount(ESOrbChange):
    def __init__(self, skill: EnemySkill):
        from_attr = -1
        to_attr = 7
        super().__init__(skill, from_attr, to_attr)
        self.random_count = int(skill.params[1])
        self.exclude_hearts = self.params[2] == 1


class ESMortalPoisonChangeRandom(ESOrbChange):
    def __init__(self, skill: EnemySkill):
        from_attr = -1
        to_attr = 8
        super().__init__(skill, from_attr, to_attr)
        self.random_count = int(skill.params[1])


class ESOrbChangeAttack(ESOrbChange):
    def __init__(self, skill: EnemySkill, orb_from=None, orb_to=None):
        from_attr = orb_from or skill.params[2]
        to_attr = orb_to or skill.params[3]
        super().__init__(skill, orb_from=from_attr, orb_to=to_attr)
        self.attack = ESAttack.new_instance(self.params[1])


class ESPoisonChangeRandomAttack(ESOrbChangeAttack):
    def __init__(self, skill: EnemySkill):
        from_attr = -1
        to_attr = 7
        super().__init__(skill, orb_from=from_attr, orb_to=to_attr)
        self.random_count = int(skill.params[2])

    def is_conditional(self):
        return False


class ESBlind(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attack = ESAttack.new_instance(self.params[1])

    def description(self):
        return Describe.blind()


class ESBlindStickyRandom(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.min_count = self.params[2]
        self.max_count = self.params[3]

    def description(self):
        return Describe.blind_sticky_random(self.turns, self.min_count, self.max_count)


class ESBlindStickyFixed(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.position_str, self.position_rows, self.position_cols \
            = positions_2d_bitmap(self.params[2:7])

    def description(self):
        return Describe.blind_sticky_fixed(self.turns)


class ESDispel(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self):
        return Describe.dispel_buffs()


class ESStatusShield(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]

    def description(self):
        return Describe.status_shield(self.turns)


class ESRecover(ESAction):
    def __init__(self, skill, target):
        super().__init__(skill)
        self.min_amount = self.params[1]
        self.max_amount = self.params[2]
        self.target = target

    def description(self):
        return Describe.recover(self.min_amount, self.max_amount, self.target)


class ESRecoverEnemy(ESRecover):
    def __init__(self, skill):
        super().__init__(skill, target=TargetType.enemy)


class ESRecoverEnemyAlly(ESRecover):
    def __init__(self, skill):
        super().__init__(skill, target=TargetType.enemy_ally)
        self.enemy_count = 1

    def conditions(self):
        return 'When enemy ally is killed'


class ESRecoverPlayer(ESRecover):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, target=TargetType.player)


class ESEnrage(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.multiplier = 1
        self.turns = 0

    def description(self):
        return Describe.enrage(self.multiplier, self.turns)


class ESStorePower(ESEnrage):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.multiplier = 100 + self.params[1]
        self.turns = 0


class ESEnrageAttackUp(ABC, ESEnrage):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)


class ESAttackUPRemainingEnemies(ESEnrageAttackUp):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.enemy_count = self.params[1]
        self.multiplier = self.params[3]
        self.turns = self.params[2]

    def description(self):
        return super().description()


class ESAttackUpStatus(ESEnrageAttackUp):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.multiplier = self.params[2]
        self.turns = self.params[1]

    def description(self):
        # return super().description() + ' after being affected by a status effect'
        return super().description()


class ESAttackUPCooldown(ESEnrageAttackUp):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        # enrage cannot trigger until this many turns have passed
        cooldown_value = self.params[1] or 0
        self.turn_cooldown = cooldown_value if cooldown_value > 1 else None
        self.multiplier = self.params[3]
        self.turns = self.params[2]

    def description(self):
        desc = super().description()
        # if self.turn_cooldown:
        #     desc += ' after {} turns'.format(self.turn_cooldown)
        return desc


class ESDebuff(ABC, ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]


class ESDebuffMovetime(ESDebuff):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.debuff_type = Status.movetime
        self.amount = 0
        self.unit = Unit.none

        if self.params[2] is not None:
            self.amount = -self.params[2] / 10
            self.unit = Unit.seconds
        elif self.params[3] is not None:
            self.amount = self.params[3]
            self.unit = Unit.percent
        else:
            human_fix_logger.warning('unexpected debuff movetime skill: {} ({})'.format(self.name, self.enemy_skill_id))

    def description(self):
        return Describe.debuff(self.debuff_type, self.amount, self.unit, self.turns)


class ESDebuffRCV(ESDebuff):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.debuff_type = Status.rcv
        self.amount = self.params[2]
        self.unit = Unit.percent

    def description(self):
        return Describe.debuff(self.debuff_type, self.amount, self.unit, self.turns)


class ESEndBattle(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self):
        return Describe.end_battle()

    def ends_battle(self):
        return True


class ESChangeAttribute(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = list(OrderedDict.fromkeys(self.params[1:6]))
        # self.attributes = list(filter(None, self.params[1:6]))

    def description(self):
        return Describe.change_attribute(self.attributes)


class ESGravity(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.percent = self.params[1]

    def description(self):
        return Describe.gravity(self.percent)


class ESAbsorb(ABC, ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.min_turns = self.params[1]
        self.max_turns = self.params[2]
        self.absorb_type = Absorb.unknown
        self.absorb_threshold = -1

    def description(self):
        return Describe.absorb(self.absorb_type, self.absorb_threshold, self.min_turns, self.max_turns)


class ESAbsorbAttribute(ESAbsorb):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = attribute_bitmap(self.params[3])
        self.absorb_type = Absorb.attr

    def description(self):
        return Describe.absorb(Absorb.attr, self.attributes, self.min_turns, self.max_turns)


class ESAbsorbCombo(ESAbsorb):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.absorb_threshold = self.params[3]
        self.absorb_type = Absorb.combo


class ESAbsorbThreshold(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.absorb_threshold = self.params[2]
        self.absorb_type = Absorb.damage

    def description(self):
        return Describe.absorb(self.absorb_type, self.absorb_threshold, self.turns)


class ESVoidShield(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        # mysterious params[2], always 1055 except for no.2485 Hakumen no Mono who has 31
        self.void_threshold = self.params[3]

    def description(self):
        return Describe.void(self.void_threshold, self.turns)


class ESDamageShield(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.shield_percent = self.params[2]

    def description(self):
        return Describe.damage_reduction('all sources', self.shield_percent, self.turns)


class ESInvulnerableOn(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]

    def description(self):
        return Describe.damage_reduction('all sources', turns=self.turns)


class ESInvulnerableOff(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self):
        return Describe.invuln_off()


class ESSkyfall(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.min_turns = self.params[2]
        self.max_turns = self.params[3]
        self.attributes = attribute_bitmap(self.params[1])
        self.chance = self.params[4]

    def description(self):
        if self.type == 68:
            return Describe.skyfall(self.attributes, self.chance,
                                    self.min_turns, self.max_turns)
        elif self.type == 96:
            return Describe.skyfall(self.attributes, self.chance,
                                    self.min_turns, self.max_turns, True)


class ESLeaderSwap(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.turns = self.params[1]

    def description(self):
        return Describe.leadswap(self.turns)


class ESFixedOrbSpawn(ABC, ESAction):
    def __init__(self, skill: EnemySkill, position_type, positions, attributes):
        super().__init__(skill)
        self.position_type = position_type
        self.positions = positions
        self.attributes = attributes


class ESRowColSpawn(ESFixedOrbSpawn):
    def __init__(self, skill: EnemySkill, position_type):
        self.position_type = position_type
        super().__init__(
            skill,
            position_type=position_type,
            positions=position_bitmap(self.params[1]),
            attributes=attribute_bitmap(self.params[2]))

    def description(self):
        return Describe.row_col_spawn(
            self.position_type,
            position_bitmap(self.params[1]),
            attribute_bitmap(self.params[2]))


class ESRowColSpawnMulti(ESFixedOrbSpawn):
    RANGE_MAP = {
        76: range(1, 4, 2),
        77: range(1, 6, 2),
        78: range(1, 4, 2),
        79: range(1, 6, 2)
    }

    def __init__(self, skill: EnemySkill, position_type):
        self.desc_arr = []
        pos = []
        att = []
        for i in self.RANGE_MAP[skill.type]:
            if skill.params[i] and skill.params[i + 1]:
                p = position_bitmap(skill.params[i])
                a = attribute_bitmap(skill.params[i + 1])
                self.desc_arr.append(Describe.row_col_spawn(position_type, p, a)[7:])
                pos += p
                att += a
        super().__init__(
            skill,
            position_type=position_type,
            positions=pos,
            attributes=att)
        self.attack = ESAttack.new_instance(self.params[7]) if skill.type in [77, 79] else None

    def description(self):
        return Describe.row_col_multi(self.desc_arr)


class ESColumnSpawn(ESRowColSpawn):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, position_type=OrbShape.column)


class ESColumnSpawnMulti(ESRowColSpawnMulti):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, position_type=OrbShape.column)


class ESRowSpawn(ESRowColSpawn):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, position_type=OrbShape.row)


class ESRowSpawnMulti(ESRowColSpawnMulti):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, position_type=OrbShape.row)


class ESRandomSpawn(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.count = self.params[1]
        self.attributes = attribute_bitmap(self.params[2])
        self.condition_attributes = []
        condition_attributes = attribute_bitmap(self.params[3], inverse=True)
        if len(condition_attributes) < 6:
            self.condition_attributes = condition_attributes

    def description(self):
        return Describe.random_orb_spawn(self.count, self.attributes)

    def is_conditional(self):
        return self.condition_attributes

    def conditions(self):
        return Describe.attribute_exists(self.condition_attributes)


class ESBombRandomSpawn(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.count = self.params[2]
        self.locked = self.params[8] == 1

    def description(self):
        spawn_type = [-9] if self.locked else [9]
        return Describe.random_orb_spawn(self.count, spawn_type)


class ESBombFixedSpawn(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.count = self.params[2]
        self.position_str, self.position_rows, self.position_cols = positions_2d_bitmap(self.params[2:7])
        self.locked = self.params[8] == 1
        all_rows = len(self.position_rows or []) == 6
        all_cols = len(self.position_cols or []) == 5
        self.whole_board = all_rows and all_cols

    def description(self):
        spawn_type = [-9] if self.locked else [9]
        if self.whole_board:
            return Describe.board_change(spawn_type)
        else:
            return Describe.fixed_orb_spawn(spawn_type)


class ESBaseBoardChange(ABC, ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = []

    def description(self):
        return Describe.board_change(self.attributes)


class ESBoardChange(ESBaseBoardChange):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = attribute_bitmap(self.params[1])


class ESBoardChangeAttackFlat(ESBaseBoardChange):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = self.params[2:self.params.index(-1)]
        self.attack = ESAttack.new_instance(self.params[1])


class ESBoardChangeAttackBits(ESBaseBoardChange):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = attribute_bitmap(self.params[2])
        self.attack = ESAttack.new_instance(self.params[1])


class ESSkillSet(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.skill_ids = list(filter(None, self.params[1:11]))  # type: List[int]
        self.skills = []  # type: List[ESAction]

    @property
    def attack(self):
        # TODO: This is so wrong. Need to stop relying on the parent
        #       skill attack and get all the attacks from the children.
        #       Also need to figure out if there are skillsets with
        #       attacks attached in addition to having children with attacks.
        if self._attack:
            return self._attack
        for s in self.skills:
            if s.attack:
                return s.attack
        return None

    @property
    def name(self):
        return Describe.join_skill_descs(map(lambda s: s.name, self.skills))

    def description(self):
        # TODO: This is weird because of the attack property above.
        # Realistically I think we should not store the attack info at all in the
        # skill description, and just rely on the min/max attacks for the UI. We can
        # Keep a version with the attacks for dumping to plain text though.
        return Describe.join_skill_descs(map(lambda s: s.description(), self.skills))

    def ends_battle(self):
        return any([s.ends_battle() for s in self.skills])


class ESSkillSetOnDeath(ESDeathAction, ESSkillSet):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def has_action(self) -> bool:
        """Helper that determines if the skillset does stuff other than emote."""
        for x in self.skills:
            if isinstance(x, ESSkillSet):
                if any([not isinstance(y, ESInactivity) for y in x.skills]):
                    return True
            elif type(x) != ESInactivity:
                return True
        return False


class ESSkillDelay(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.min_turns = self.params[1]
        self.max_turns = self.params[2]

    def description(self):
        return Describe.skill_delay(self.min_turns, self.max_turns)


class ESOrbLock(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = attribute_bitmap(self.params[1])
        self.count = self.params[2]

    def description(self):
        return Describe.orb_lock(self.count, self.attributes)

    def is_conditional(self):
        return self.attributes != [-1] and len(self.attributes) != 9


class ESOrbSeal(ABC, ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[2]
        self.position_type = None
        self.positions = position_bitmap(self.params[1])

    def description(self):
        return Describe.orb_seal(self.turns, self.position_type, self.positions)


class ESOrbSealColumn(ESOrbSeal):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.position_type = OrbShape.column


class ESOrbSealRow(ESOrbSeal):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.position_type = OrbShape.row


class ESCloud(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.cloud_width = self.params[2]
        self.cloud_height = self.params[3]
        self.origin_y = self.params[4]
        self.origin_x = self.params[5]

    def description(self):
        return Describe.cloud(
            self.turns, self.cloud_width, self.cloud_height, self.origin_x, self.origin_y)


class ESFixedStart(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self):
        return Describe.fixed_start()


class ESAttributeBlock(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.attributes = attribute_bitmap(self.params[2])

    def description(self):
        return Describe.attribute_block(self.turns, self.attributes)


class ESSpinners(ABC, ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.speed = self.params[2]


class ESSpinnersRandom(ESSpinners):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.count = self.params[3]

    def description(self):
        return Describe.spinners(self.turns, self.speed, self.count)


class ESSpinnersFixed(ESSpinners):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.position_str, self.position_rows, self.position_cols = positions_2d_bitmap(self.params[3:8])

    def description(self):
        return Describe.spinners(self.turns, self.speed)


class ESMaxHPChange(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[3]
        if self.params[1] is not None:
            self.max_hp = self.params[1]
            self.percent = True
        elif self.params[2] is not None:
            self.max_hp = self.params[2]
            self.percent = False

    def description(self):
        return Describe.max_hp_change(self.turns, self.max_hp, self.percent)


class ESFixedTarget(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turn_count = self.params[1]

    def description(self):
        return Describe.fixed_target(self.turn_count)


class ESGachaFever(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attribute = self.params[1]
        self.orb_req = self.params[2]

    def description(self):
        return Describe.gacha_fever(self.attribute, self.orb_req)


class ESLeaderAlter(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.target_card = self.params[2]

    def description(self):
        return Describe.lead_alter(self.turns, self.target_card)


class ES7x6Change(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.unknown = self.params[2]  # So far, only a single example with 1, converts to 7x6

    def description(self):
        return Describe.force_7x6(self.turns)


class ESNoSkyfall(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[2]

    def description(self):
        return Describe.no_skyfall(self.turns)


# Passive
class ESPassive(ESBehavior):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self):
        return 'Unset passive'


class ESAttributeResist(ESPassive):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = attribute_bitmap(self.params[1])
        self.shield_percent = self.params[2]

    def description(self):
        return Describe.damage_reduction(
            attributes_to_str(self.attributes), percent=self.shield_percent)


class ESResolve(ESPassive):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.hp_threshold = self.params[1]

    def description(self):
        return Describe.resolve(self.hp_threshold)


class ESTurnChangeRemainingEnemies(ESPassive):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turn_counter = self.params[2]
        self.enemy_count = self.params[1]

    def description(self):
        return Describe.turn_change(self.turn_counter)


class ESTurnChangePassive(ESPassive):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.hp_threshold = self.params[1]
        self.turn_counter = self.params[2]

    def description(self):
        return Describe.turn_change(self.turn_counter, self.hp_threshold)


class ESTypeResist(ESPassive):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.types = typing_bitmap(self.params[1])
        self.shield_percent = self.params[2]

    def description(self):
        return Describe.damage_reduction(
            typing_to_str(self.types), percent=self.shield_percent)


# Logic
class ESLogic(ESBehavior):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    @property
    def name(self):
        return type(self).__name__

    def description(self):
        return 'Unset logic'


class ESNone(ESLogic):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self):
        # return 'No action'
        return 'nothing'


class ESFlagOperation(ESLogic):
    FLAG_OPERATION_MAP = {
        22: 'SET',
        24: 'UNSET',
        44: 'OR',
        45: 'XOR'
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.flag = None
        self.flag_bin = None
        self.operation = self.FLAG_OPERATION_MAP[skill.type]

    def description(self):
        return 'flag {} {}'.format(self.operation, self.flag_bin)


class ESSetCounter(ESLogic):
    COUNTER_SET_MAP = {
        25: '=',
        26: '+',
        27: '-'
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.counter = None
        self.set = self.COUNTER_SET_MAP[skill.type]

    def description(self):
        return 'counter {} {}'.format(self.set, self.counter)


class ESSetCounterIf(ESLogic):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.counter_is = None
        self.counter = None

    def description(self):
        return 'set counter = {} if counter == {}'.format(self.counter, self.counter_is)


class ESBranch(ESLogic):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.branch_condition = None
        self.compare = '='
        self.branch_value = None
        self.target_round = None
        self.target_round_offset = 0

    def description(self):
        return Describe.branch(self.branch_condition, self.compare, self.branch_value, self.target_round)


class ESBranchFlag0(ESBranch):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.branch_condition = 'flag'
        self.compare = '&'
        # For legacy reasons we treat all branches as 0 offset and manually offset by 1.
        # This +1 fixes it for this rarely used branch type.
        self.target_round_offset = 1


class ESBranchFlag(ESBranch):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.branch_condition = 'flag'
        self.compare = '&'


class ESBranchHP(ESBranch):
    HP_COMPARE_MAP = {
        28: '<',
        29: '>'
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.branch_condition = 'hp'
        self.compare = self.HP_COMPARE_MAP[skill.type]


class ESBranchCounter(ESBranch):
    COUNTER_COMPARE_MAP = {
        30: '<',
        31: '=',
        32: '>'
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.branch_condition = 'counter'
        self.compare = self.COUNTER_COMPARE_MAP[skill.type]


class ESBranchLevel(ESBranch):
    LEVEL_COMPARE_MAP = {
        33: '<=',
        34: '=',
        35: '>'
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.branch_condition = 'level'
        self.compare = self.LEVEL_COMPARE_MAP[skill.type]


class ESEndPath(ESLogic):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self):
        return 'end_turn'


class ESCountdown(ESLogic):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self):
        # return 'countdown and end turn'
        # TODO: fix for tieout
        return 'countdown'


class ESCountdownMessage(ESBehavior):
    """Dummy action class to represent displaying countdown numbers"""

    def __init__(self, current_counter=0):
        raw = ['-1', 'Countdown Message', '-1', '0']
        dummy_skill = EnemySkill(raw)
        super().__init__(dummy_skill)
        self.current_counter = current_counter

    def description(self):
        return Describe.countdown(self.current_counter)


class ESPreemptive(ESLogic):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.level = self.params[1]

    def description(self):
        return 'Enable preempt if level {}'.format(self.level)


class ESBranchCard(ESBranch):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.branch_condition = 'player_cards'
        self.compare = 'HAS'
        self.branch_list_value = list(filter(None, self.params))
        self.branch_value = self.branch_list_value

    def description(self):
        return Describe.branch(self.branch_condition, self.compare, self.branch_list_value, self.target_round)


class ESBranchCombo(ESBranch):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.branch_condition = 'combo'
        self.compare = '>='


class ESBranchRemainingEnemies(ESBranch):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.branch_condition = 'remaining enemies'
        self.compare = '<='


class EnemySkillUnknown(ESBehavior):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)


class ESInstance(Printable):
    def __init__(self, behavior: ESBehavior, ref: ESRef, monster_card: Card):
        self.enemy_skill_id = behavior.enemy_skill_id
        self.behavior = copy.deepcopy(behavior)
        self.condition = None  # type: Optional[ESCondition]

        # self.ai = ref.enemy_ai
        # self.rnd = ref.enemy_rnd

        self.use_new_ai = monster_card.use_new_ai
        self.max_counter = monster_card.enemy_skill_max_counter
        self.increment = monster_card.enemy_skill_counter_increment

        if not issubclass(self.btype, ESLogic):
            if ref.enemy_ai > 0 or ref.enemy_rnd > 0:
                self.condition = ESCondition(ref.enemy_ai, ref.enemy_rnd, self.behavior.params)

        # This seems bad but I'm not sure how to improve
        # Start terrible badness
        if isinstance(self.behavior, ESFlagOperation):
            self.behavior.flag = ref.enemy_ai
            self.behavior.flag_bin = bin(ref.enemy_ai)

        if isinstance(self.behavior, ESSetCounter):
            self.behavior.counter = ref.enemy_ai if self.behavior.type == 25 else 1

        if isinstance(self.behavior, ESSetCounterIf):
            self.behavior.counter_is = ref.enemy_ai
            self.behavior.counter = ref.enemy_rnd

        if isinstance(self.behavior, ESBranch):
            self.behavior.branch_value = ref.enemy_ai
            self.behavior.target_round = ref.enemy_rnd + self.behavior.target_round_offset

        if self.btype in [ESRecoverEnemyAlly, ESAttackUPRemainingEnemies, ESTurnChangeRemainingEnemies]:
            self._ensure_condition(ref)
            self.condition.enemies_remaining = self.behavior.enemy_count

        if self.btype in [ESSkillSetOnDeath, ESDeathCry]:
            self._ensure_condition(ref)
            self.condition.on_death = True

        if self.btype in [ESRandomSpawn]:
            self._ensure_condition(ref)
            self.condition.condition_attributes = self.behavior.condition_attributes
        # End terrible badness

    def _ensure_condition(self, ref: ESRef):
        if not self.condition:
            self.condition = ESCondition(ref.enemy_ai, ref.enemy_rnd, self.behavior.params)

    @property
    def btype(self):
        return type(self.behavior)

    @property
    def name(self):
        return self.behavior.name

    def description(self):
        msg = self.condition.description() if self.condition else ''
        msg = msg or ''
        msg += self.behavior.description()
        return msg.strip()

    def __str__(self):
        return 'ESInstance - {} | {}'.format(self.behavior, self.ref)

    def __eq__(self, other):
        return other and self.enemy_skill_id == other.enemy_skill_id


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
    9: EnemySkillUnknown,  # This skill is unused
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
    57: ESPoisonChangeRandom,
    60: ESPoisonChangeRandomCount,
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
    123: ESInvulnerableOn,  # hexa's invulnerable gets special type because reasons
    124: ESGachaFever,  # defines number & type of orbs needed in fever mode
    125: ESLeaderAlter,
    126: ES7x6Change,
    127: ESNoSkyfall,

    # LOGIC
    0: ESNone,
    21: EnemySkillUnknown,  # This logic is unused
    22: ESFlagOperation,
    23: ESBranchFlag0,
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
    122: ESTurnChangeRemainingEnemies,
    118: ESTypeResist,
}
