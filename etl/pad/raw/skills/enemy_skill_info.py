import copy
import logging
from abc import ABC
from collections import OrderedDict
from typing import List, Optional

from pad.common.pad_util import Printable
from pad.raw import EnemySkill
from pad.raw.card import ESRef, Card
from pad.raw.skills.en.enemy_skill_text import *
from pad.raw.skills.en.skill_common import *

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
        row = [(bits_arr[i] >> j) & 1 for j in range(6)]
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

        # Only executes if these attributes are cleared
        self.attributes_erased = None

        # Only executs if this much damage is done
        self.damage_done = None

        # Only executes if these attributes attacked
        self.attributes_attacked = None

        # Only executes if the number of skills are used
        self.skills_used = None

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

    def description(self, converter):
        desc = converter.condition(max(self._ai, self._rnd), self.hp_threshold,
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
                desc += " & " + converter.attribute_exists(self.condition_attributes)
            else:
                desc = converter.attribute_exists(self.condition_attributes).capitalize()

        if self.attributes_erased:
            if desc:
                desc += " & " + converter.attributes_to_str(self.attributes_erased) + " are erased"
            else:
                desc = converter.attributes_to_str(self.attributes_erased) + " are erased"

        if self.damage_done:
            if desc:
                desc += " & damage done in previous turn is >= {}".format(self.damage_done)
            else:
                desc = "damage done in previous turn is >= {}".format(self.damage_done)

        if self.attributes_attacked:
            if desc:
                desc += " & when " + converter.attributes_to_str(self.attributes_attacked) + " are used to attack"
            else:
                desc = converter.attributes_to_str(self.attributes_attacked) + " are used to attack"

        if self.skills_used:
            if desc:
                desc += " & " + "# of skills used >= {}".format(self.skills_used)
            else:
                desc = "# of skills used >= {}".format(self.skills_used)

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

    def description(self, converter):
        return converter.attack(self.atk_multiplier, self.min_hits, self.max_hits)


class ESBehavior(Printable):
    skill_types = []
    """Base class for any kind of enemy behavior, including logic, passives, and actions"""

    def __init__(self, skill: EnemySkill):
        self.enemy_skill_id = skill.enemy_skill_id
        self._name = skill.name
        self.type = skill.type
        self.params = skill.params

        # The default value for this skill conditional. This value can be
        # overridden or the is_conditional function can be adjusted.
        self.conditional = False

    @property
    def name(self):
        return self._name

    def ends_battle(self):
        return False

    def description(self, converter):
        return converter.not_set()

    def full_description(self, converter):
        return self.description(converter)

    def is_conditional(self):
        return self.conditional

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

    def full_description(self, converter):
        if isinstance(self, ESBehaviorAttack):
            return self.description(converter)
        elif self.attack:
            return '{}, {:s}'.format(self.description(converter), self.attack.description(converter))
        else:
            return self.description(converter)


class ESBehaviorAttack(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self, converter):
        return converter.attack(self.attack.atk_multiplier, self.attack.min_hits, self.attack.max_hits)


class ESInactivity(ESAction):
    def description(self, converter):
        return converter.skip()


class ESInactivity16(ESInactivity):
    skill_types = [16]


class ESInactivity66(ESInactivity):
    skill_types = [66]


class ESDeathCry(ESDeathAction, ESAction):
    skill_types = [69]

    def __init__(self, skill):
        super().__init__(skill)
        self.message = self.params[0]

    def description(self, converter):
        return converter.death_cry(self.message)


class ESAttackSinglehit(ESBehaviorAttack):
    skill_types = [82]

    def __init__(self, skill):
        super().__init__(skill)
        self.attack = ESAttack.new_instance(100)


# 'Fake' Behavior - Stand-In For Default Attack
class ESDefaultAttack(ESAttackSinglehit):
    def __init__(self):
        raw = ['-2', 'Default Attack', '-2', '0']
        dummy_skill = EnemySkill(raw)
        super().__init__(dummy_skill)


class ESAttackMultihit(ESBehaviorAttack):
    skill_types = [15]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attack = ESAttack.new_instance(self.params[3], self.params[1], self.params[2])


class ESAttackPreemptive(ESBehaviorAttack):
    skill_types = [47]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attack = ESAttack.new_instance(self.params[2])


class ESBind(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.min_turns = self.params[2] or 0
        self.max_turns = self.params[3]
        self.target_count = None
        self.targets = [TargetType.unset]

    def description(self, converter):
        return converter.bind(self.min_turns, self.max_turns,
                              self.target_count, self.targets)


class ESBindAttack(ESBind):
    skill_types = [63]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.targets = bind_bitmap(self.params[4])
        if 'leader' not in ''.join(map(str, self.targets)):
            self.target_count = self.params[5]
        self.attack = ESAttack.new_instance(self.params[1])


class ESBindRandom(ESBind):
    skill_types = [1]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.target_count = self.params[1]
        self.targets = TargetType.random


class ESBindTarget(ESBind):
    skill_types = [54]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.targets = bind_bitmap(self.params[1])
        self.target_count = None


class ESBindRandomSub(ESBindRandom):
    skill_types = [65]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.targets = TargetType.subs


class ESBindAttribute(ESBind):
    skill_types = [2]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.target_attribute = self.params[1]
        self.targets = [TargetType.attrs]

        self.conditional = True

    def description(self, converter):
        return converter.bind(self.min_turns, self.max_turns,
                              target_types=self.target_attribute, source=Source.attrs)


class ESBindTyping(ESBind):
    skill_types = [3]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.target_typing = self.params[1]
        self.targets = [TargetType.types]

        self.conditional = True

    def description(self, converter):
        return converter.bind(self.min_turns, self.max_turns,
                              target_types=self.target_typing, source=Source.types)


class ESBindSkill(ESAction):
    skill_types = [14]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.min_turns = self.params[1] or 0
        self.max_turns = self.params[2]

    def description(self, converter):
        return converter.bind(self.min_turns, self.max_turns, target_types=TargetType.actives)


class ESBindAwoken(ESAction):
    skill_types = [88]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]

        self.conditional = self.turns > 1

    def description(self, converter):
        return converter.bind(self.turns, None, None, target_types=TargetType.awokens)


class ESOrbChange(ESAction):
    def __init__(self, skill: EnemySkill, orb_from, orb_to):
        super().__init__(skill)
        self.orb_from = orb_from
        self.orb_to = orb_to
        self.random_count = None
        self.random_type_count = None
        self.exclude_hearts = None

        self.conditional = self.orb_from != -1

    def description(self, converter):
        return converter.orb_change(self.orb_from,
                                    self.orb_to,
                                    random_count=self.random_count,
                                    random_type_count=self.random_type_count,
                                    exclude_hearts=self.exclude_hearts)


# Prototype
class ESOrbChangeConditional(ABC, ESOrbChange):
    def __init__(self, skill: EnemySkill, orb_from, orb_to):
        super().__init__(skill, orb_from, orb_to)
        self.conditional = True


class ESOrbChangeSingle(ESOrbChangeConditional):
    skill_types = [4]

    def __init__(self, skill: EnemySkill):
        from_attr = skill.params[1]
        to_attr = skill.params[2]
        super().__init__(skill, from_attr, to_attr)


class ESOrbChangeAttackBits(ESOrbChangeConditional):
    skill_types = [108]

    def __init__(self, skill: EnemySkill):
        super().__init__(
            skill,
            orb_from=attribute_bitmap(skill.params[2]),
            orb_to=attribute_bitmap(skill.params[3]))
        self.attack = ESAttack.new_instance(self.params[1])


class ESJammerChangeSingle(ESOrbChangeConditional):
    skill_types = [12]

    def __init__(self, skill: EnemySkill):
        from_attr = skill.params[1]
        to_attr = 6
        super().__init__(skill, from_attr, to_attr)


class ESJammerChangeRandom(ESOrbChange):
    skill_types = [13]

    def __init__(self, skill: EnemySkill):
        from_attr = -1
        to_attr = 6
        super().__init__(skill, from_attr, to_attr)
        self.random_type_count = int(skill.params[1])


class ESPoisonChangeSingle(ESOrbChangeConditional):
    skill_types = [56]

    def __init__(self, skill: EnemySkill):
        from_attr = skill.params[1]
        to_attr = 7
        super().__init__(skill, from_attr, to_attr)


class ESPoisonChangeRandom(ESOrbChange):
    skill_types = [57]

    def __init__(self, skill: EnemySkill):
        from_attr = -1
        to_attr = 7
        super().__init__(skill, from_attr, to_attr)
        self.exclude_hearts = self.params[2] == 1


class ESPoisonChangeRandomCount(ESOrbChange):
    skill_types = [60]

    def __init__(self, skill: EnemySkill):
        from_attr = -1
        to_attr = 7
        super().__init__(skill, from_attr, to_attr)
        self.random_count = int(skill.params[1])
        self.exclude_hearts = self.params[2] == 1


class ESMortalPoisonChangeRandom(ESOrbChange):
    skill_types = [61]

    def __init__(self, skill: EnemySkill):
        from_attr = -1
        to_attr = 8
        super().__init__(skill, from_attr, to_attr)
        self.random_count = int(skill.params[1])


class ESOrbChangeAttack(ESOrbChange):
    skill_types = [48]

    def __init__(self, skill: EnemySkill, orb_from=None, orb_to=None):
        from_attr = orb_from or skill.params[2]
        to_attr = orb_to or skill.params[3]
        super().__init__(skill, orb_from=from_attr, orb_to=to_attr)
        self.attack = ESAttack.new_instance(self.params[1])


class ESPoisonChangeRandomAttack(ESOrbChangeAttack):
    skill_types = [64]

    def __init__(self, skill: EnemySkill):
        from_attr = -1
        to_attr = 7
        super().__init__(skill, orb_from=from_attr, orb_to=to_attr)
        self.random_count = int(skill.params[2])
        self.conditional = False


class ESBlind(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attack = ESAttack.new_instance(self.params[1])

    def description(self, converter):
        return converter.blind()


class ESBlind5(ESBlind):
    skill_types = [5]


class ESBlind62(ESBlind):
    skill_types = [62]


class ESBlindStickyRandom(ESAction):
    skill_types = [97]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.min_count = self.params[2]
        self.max_count = self.params[3]

    def description(self, converter):
        return converter.blind_sticky_random(self.turns, self.min_count, self.max_count)


class ESBlindStickyFixed(ESAction):
    skill_types = [98]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.position_map, self.position_rows, self.position_cols \
            = positions_2d_bitmap(self.params[2:7])

    def description(self, converter):
        return converter.blind_sticky_fixed(self.turns)


class ESBlindStickySkyfall(ESAction):
    skill_types = [128]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.chance = self.params[2]
        self.b_turns = self.params[13]  # For some reason?? (why?)

    def description(self, converter):
        return converter.blind_sticky_skyfall(self.turns, self.chance, self.b_turns)


class ESDispel(ESAction):
    skill_types = [6]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self, converter):
        return converter.dispel_buffs()


class ESStatusShield(ESAction):
    skill_types = [20]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]

    def description(self, converter):
        return converter.status_shield(self.turns)


class ESRecover(ESAction):
    def __init__(self, skill, target):
        super().__init__(skill)
        self.target = target

    def description(self, converter):
        return converter.recover(self.min_amount, self.max_amount, self.target)


class ESRecoverEnemy(ESRecover):
    def __init__(self, skill):
        super().__init__(skill, target=TargetType.enemy)
        self.min_amount = self.params[1]
        self.max_amount = self.params[2]


class ESRecoverEnemy7(ESRecoverEnemy):
    skill_types = [7]


class ESRecoverEnemy86(ESRecoverEnemy):
    skill_types = [86]


class ESRecoverEnemyAlly(ESRecover):
    skill_types = [52]

    def __init__(self, skill):
        super().__init__(skill, target=TargetType.enemy_ally)
        self.enemy_count = 1
        self.min_amount = self.params[1]
        self.max_amount = self.params[1]


class ESRecoverPlayer(ESRecover):
    skill_types = [55]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill, target=TargetType.player)
        self.min_amount = self.params[1]
        self.max_amount = self.params[1]
        self.hp_threshold = self.params[2]

    def description(self, converter):
        return converter.recover(self.min_amount, self.max_amount, self.target, player_threshold=self.hp_threshold)


class ESEnrage(ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.multiplier = 1
        self.turns = 0

    def description(self, converter):
        return converter.enrage(self.multiplier, self.turns)


class ESStorePower(ESEnrage):
    skill_types = [8]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.multiplier = 100 + self.params[1]
        self.turns = 0


class ESEnrageAttackUp(ABC, ESEnrage):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)


class ESAttackUPRemainingEnemies(ESEnrageAttackUp):
    skill_types = [17]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.enemy_count = self.params[1]
        self.multiplier = self.params[3]
        self.turns = self.params[2]


class ESAttackUpStatus(ESEnrageAttackUp):
    skill_types = [18]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.multiplier = self.params[2]
        self.turns = self.params[1]

    def debug_description(self, converter):
        return super().description(converter) + ' after being affected by a status effect'


class ESAttackUPCooldown(ESEnrageAttackUp):
    skill_types = [19]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        # enrage cannot trigger until this many turns have passed
        cooldown_value = self.params[1] or 0
        self.turn_cooldown = cooldown_value if cooldown_value > 1 else None
        self.multiplier = self.params[3]
        self.turns = self.params[2]

    def debug_description(self, converter):
        desc = super().description(converter)
        if self.turn_cooldown:
            desc += ' after {} turns'.format(self.turn_cooldown)
        return desc


class ESDebuff(ABC, ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]


class ESDebuffMovetime(ESDebuff):
    skill_types = [39]

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

    def description(self, converter):
        return converter.debuff(self.debuff_type, self.amount, self.unit, self.turns)


class ESDebuffRCV(ESDebuff):
    skill_types = [105]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.debuff_type = Status.rcv
        self.amount = self.params[2]
        self.unit = Unit.percent

    def description(self, converter):
        return converter.debuff(self.debuff_type, self.amount, self.unit, self.turns)


class ESDebuffATK(ESAction):
    skill_types = [130]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.amount = self.params[2]

    def description(self, converter):
        return converter.debuff_atk(self.turns, self.amount)


class ESEndBattle(ESAction):
    skill_types = [40]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self, converter):
        return converter.end_battle()

    def ends_battle(self):
        return True


class ESChangeAttribute(ESAction):
    skill_types = [46]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = list(OrderedDict.fromkeys(self.params[1:6]))
        # self.attributes = list(filter(None, self.params[1:6]))

    def description(self, converter):
        return converter.change_attribute(self.attributes)


class ESGravity(ESAction):
    skill_types = [50]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.percent = self.params[1]

    def description(self, converter):
        return converter.gravity(self.percent)


class ESAbsorb(ABC, ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.min_turns = self.params[1] or 0
        self.max_turns = self.params[2]
        self.absorb_type = Absorb.unknown
        self.absorb_threshold = -1

    def description(self, converter):
        return converter.absorb(self.absorb_type, self.absorb_threshold, self.min_turns, self.max_turns)


class ESAbsorbAttribute(ESAbsorb):
    skill_types = [53]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = attribute_bitmap(self.params[3])
        self.absorb_type = Absorb.attr

    def description(self, converter):
        return converter.absorb(Absorb.attr, self.attributes, self.min_turns, self.max_turns)


class ESAbsorbCombo(ESAbsorb):
    skill_types = [67]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.absorb_threshold = self.params[3]
        self.absorb_type = Absorb.combo


class ESAbsorbThreshold(ESAbsorb):
    skill_types = [87]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.absorb_threshold = self.params[2]
        self.absorb_type = Absorb.damage

    def description(self, converter):
        return converter.absorb(self.absorb_type, self.absorb_threshold, self.turns)


class ESVoidShield(ESAction):
    skill_types = [71]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        # mysterious params[2], always 1055 except for no.2485 Hakumen no Mono who has 31
        self.void_threshold = self.params[3]

    def description(self, converter):
        return converter.void(self.void_threshold, self.turns)


class ESDamageShield(ESAction):
    skill_types = [74]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.shield_percent = self.params[2]

    def description(self, converter):
        return converter.damage_reduction(
            Source.all_sources, None, self.shield_percent, self.turns)


class ESInvulnerableOn(ESAction):
    skill_types = [119]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]

    def description(self, converter):
        return converter.damage_reduction(Source.all_sources, turns=self.turns)


class ESInvulnerableOnHexazeon(ESInvulnerableOn):
    skill_types = [123]


class ESInvulnerableOff(ESAction):
    skill_types = [121]

    def description(self, converter):
        return converter.invuln_off()


class ESSkyfall(ESAction):
    skill_types = [68]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.min_turns = self.params[2] or 0
        self.max_turns = self.params[3]
        self.attributes = attribute_bitmap(self.params[1])
        self.chance = self.params[4]

    def description(self, converter):
        return converter.skyfall(self.attributes, self.chance,
                                 self.min_turns, self.max_turns)


class ESSkyfallLocked(ESSkyfall):
    skill_types = [96]

    def description(self, converter):
        return converter.skyfall(self.attributes, self.chance,
                                 self.min_turns, self.max_turns, True)


class ESLeaderSwap(ESAction):
    skill_types = [75]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.turns = self.params[1]

    def description(self, converter):
        return converter.leadswap(self.turns)


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

    def description(self, converter):
        return converter.row_col_spawn(
            self.position_type,
            position_bitmap(self.params[1]),
            attribute_bitmap(self.params[2]))


class ESRowColSpawnMulti(ESFixedOrbSpawn):
    RANGE_MAP = {
        76: [1, 3],
        77: [1, 3, 5],
        78: [1, 3],
        79: [1, 3, 5]
    }

    def __init__(self, skill: EnemySkill, position_type):
        self.pos_nested = []
        self.att_nested = []
        for i in self.RANGE_MAP[skill.type]:
            if skill.params[i] and skill.params[i + 1]:
                self.pos_nested.append(position_bitmap(skill.params[i]))
                self.att_nested.append(attribute_bitmap(skill.params[i + 1]))

        super().__init__(
            skill,
            position_type=position_type,
            positions=sum(self.pos_nested, []),
            attributes=sum(self.att_nested, []))
        self.attack = ESAttack.new_instance(self.params[7]) if skill.type in [77, 79] else None

    def description(self, converter):
        desc_arr = [converter.row_col_spawn(self.position_type, self.pos_nested[i], self.att_nested[i])
                    for i in range(len(self.pos_nested))]
        return converter.row_col_multi(desc_arr)


class ESColumnSpawn(ESRowColSpawn):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, position_type=OrbShape.column)


class ESColumnSpawnMulti(ESRowColSpawnMulti):
    skill_types = [76, 77]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill, position_type=OrbShape.column)


class ESRowSpawn(ESRowColSpawn):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill, position_type=OrbShape.row)


class ESRowSpawnMulti(ESRowColSpawnMulti):
    skill_types = [78, 79]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill, position_type=OrbShape.row)


class ESRandomSpawn(ESAction):
    skill_types = [92]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.count = self.params[1]
        self.attributes = attribute_bitmap(self.params[2])
        self.condition_attributes = []
        condition_attributes = attribute_bitmap(self.params[3], inverse=True)
        if len(condition_attributes) < 6:
            self.condition_attributes = condition_attributes
        self.conditional = bool(self.condition_attributes)

    def description(self, converter):
        if self.count == 42 and self.condition_attributes:
            return converter.orb_change(self.condition_attributes, self.attributes)
        else:
            return converter.random_orb_spawn(self.count, self.attributes)


class ESBombRandomSpawn(ESAction):
    skill_types = [102]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.count = self.params[2]
        self.locked = self.params[8] == 1

    def description(self, converter):
        spawn_type = [-9] if self.locked else [9]
        return converter.random_orb_spawn(self.count, spawn_type)


class ESBombFixedSpawn(ESAction):
    skill_types = [103]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.count = self.params[2]
        self.position_map, self.position_rows, self.position_cols = positions_2d_bitmap(self.params[2:7])
        self.locked = self.params[8] == 1
        all_rows = len(self.position_rows or []) == 6
        all_cols = len(self.position_cols or []) == 5
        self.whole_board = all_rows and all_cols

    def description(self, converter):
        spawn_type = [-9] if self.locked else [9]
        if self.whole_board:
            return converter.board_change(spawn_type)
        else:
            return converter.fixed_orb_spawn(spawn_type)


class ESBaseBoardChange(ABC, ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = []

    def description(self, converter):
        return converter.board_change(self.attributes)


class ESBoardChange(ESBaseBoardChange):
    skill_types = [84]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = attribute_bitmap(self.params[1])


class ESBoardChangeAttackFlat(ESBaseBoardChange):
    skill_types = [81]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = self.params[2:self.params.index(-1)]
        self.attack = ESAttack.new_instance(self.params[1])


class ESBoardChangeAttackBits(ESBaseBoardChange):
    skill_types = [85]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = attribute_bitmap(self.params[2])
        self.attack = ESAttack.new_instance(self.params[1])


class ESSkillSet(ESAction):
    skill_types = [83]

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
        # TODO: Find out if this makes sense in Korean.  It does work in English and Japanese.
        return ' + '.join(map(lambda s: s.name, self.skills))

    def description(self, converter):
        # TODO: This is weird because of the attack property above.
        # Realistically I think we should not store the attack info at all in the
        # skill description, and just rely on the min/max attacks for the UI. We can
        # Keep a version with the attacks for dumping to plain text though.
        return converter.join_skill_descs(map(lambda s: s.description(converter), self.skills))

    def ends_battle(self):
        return any([s.ends_battle() for s in self.skills])


class ESSkillSetOnDeath(ESDeathAction, ESSkillSet):
    skill_types = [95]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def has_action(self) -> bool:
        """Helper that determines if the skillset does stuff other than emote."""
        for skill in self.skills:
            if isinstance(skill, ESSkillSet):
                if any([not isinstance(y, ESInactivity) for y in skill.skills]):
                    return True
            elif not isinstance(skill, ESInactivity):
                return True
        return False


class ESSkillDelay(ESAction):
    skill_types = [89]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.min_turns = self.params[1] or 0
        self.max_turns = self.params[2]

    def description(self, converter):
        return converter.skill_delay(self.min_turns, self.max_turns)


class ESOrbLock(ESAction):
    skill_types = [94]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = attribute_bitmap(self.params[1])
        self.count = self.params[2]

        self.conditional = self.attributes != [-1] and len(self.attributes) < 4

    def description(self, converter):
        return converter.orb_lock(self.count, self.attributes)


class ESOrbSeal(ABC, ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[2]
        self.position_type = None
        self.positions = position_bitmap(self.params[1])

    def description(self, converter):
        return converter.orb_seal(self.turns, self.position_type, self.positions)


class ESOrbSealColumn(ESOrbSeal):
    skill_types = [99]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.position_type = OrbShape.column


class ESOrbSealRow(ESOrbSeal):
    skill_types = [100]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.position_type = OrbShape.row


class ESCloud(ESAction):
    skill_types = [104]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.cloud_width = self.params[2]
        self.cloud_height = self.params[3]
        self.origin_y = self.params[4]
        self.origin_x = self.params[5]

    def description(self, converter):
        return converter.cloud(
            self.turns, self.cloud_width, self.cloud_height, self.origin_x, self.origin_y)


class ESFixedStart(ESAction):
    skill_types = [101]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self, converter):
        return converter.fixed_start()


class ESAttributeBlock(ESAction):
    skill_types = [107]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.attributes = attribute_bitmap(self.params[2])

    def description(self, converter):
        return converter.attribute_block(self.turns, self.attributes)


class ESSpinners(ABC, ESAction):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.speed = self.params[2]


class ESSpinnersRandom(ESSpinners):
    skill_types = [109]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.count = self.params[3]

    def description(self, converter):
        return converter.spinners(self.turns, self.speed, self.count)


class ESSpinnersFixed(ESSpinners):
    skill_types = [110]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.position_map, self.position_rows, self.position_cols = positions_2d_bitmap(self.params[3:8])

    def description(self, converter):
        return converter.spinners(self.turns, self.speed)


class ESMaxHPChange(ESAction):
    skill_types = [111]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[3]
        if self.params[1] is not None:
            self.max_hp = self.params[1]
            self.percent = True
        elif self.params[2] is not None:
            self.max_hp = self.params[2]
            self.percent = False

    def description(self, converter):
        return converter.max_hp_change(self.turns, self.max_hp, self.percent)


class ESFixedTarget(ESAction):
    skill_types = [112]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turn_count = self.params[1]

    def description(self, converter):
        return converter.fixed_target(self.turn_count)


class ESGachaFever(ESAction):
    skill_types = [124]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attribute = self.params[1]
        self.orb_req = self.params[2]

    def description(self, converter):
        return converter.gacha_fever(self.attribute, self.orb_req)


class ESLeaderAlter(ESAction):
    skill_types = [125]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.target_card = self.params[2]

    def description(self, converter):
        return converter.lead_alter(self.turns, self.target_card)


class ESBoardSizeChange(ESAction):
    skill_types = [126]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[1]
        self.board_size_param = self.params[2]
        self.conditional = True

    def description(self, converter):
        return converter.force_board_size(self.turns, self.board_size_param)


class ESNoSkyfall(ESAction):
    skill_types = [127]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[2]

    def description(self, converter):
        return converter.no_skyfall(self.turns)


class ESComboSkyfall(ESAction):
    skill_types = [131]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turns = self.params[2]
        self.chance = self.params[3]

    def description(self, converter):
        return converter.combo_skyfall(self.turns, self.chance)


# Passive
class ESPassive(ESBehavior):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self, converter):
        return 'Unset passive'


class ESAttributeResist(ESPassive):
    skill_types = [72]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.attributes = attribute_bitmap(self.params[1])
        self.shield_percent = self.params[2]

    def description(self, converter):
        return converter.damage_reduction(
            Source.attrs, self.attributes, percent=self.shield_percent)


class ESResolve(ESPassive):
    skill_types = [73]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.hp_threshold = self.params[1]

    def description(self, converter):
        return converter.resolve(self.hp_threshold)


class ESSuperResolve(ESPassive):
    skill_types = [129]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.hp_threshold = self.params[1]
        self.hp_remaining = self.params[2]

    def description(self, converter):
        return converter.superresolve(self.hp_threshold, self.hp_remaining)


class ESTurnChangeRemainingEnemies(ESPassive):
    skill_types = [122]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.turn_counter = self.params[2]
        self.enemy_count = self.params[1]

    def description(self, converter):
        return converter.turn_change(self.turn_counter)


class ESTurnChangePassive(ESPassive):
    skill_types = [106]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.hp_threshold = self.params[1]
        self.turn_counter = self.params[2]

    def description(self, converter):
        return converter.turn_change(self.turn_counter, self.hp_threshold)


class ESTypeResist(ESPassive):
    skill_types = [118]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.types = typing_bitmap(self.params[1])
        self.shield_percent = self.params[2]

    def description(self, converter):
        return converter.damage_reduction(
            Source.types, self.types, percent=self.shield_percent)


# Logic
class ESLogic(ESBehavior):
    @property
    def name(self):
        return type(self).__name__

    def description(self, converter):
        return 'Unset logic'


class ESNone(ESLogic):
    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self, converter):
        # return 'No action'
        return 'nothing'


class ESFlagOperation(ESLogic):
    skill_types = [22, 24, 44, 45]
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

    def description(self, converter):
        return 'flag {} {}'.format(self.operation, self.flag_bin)


class ESSetCounter(ESLogic):
    skill_types = [25, 26, 27]
    COUNTER_SET_MAP = {
        25: '=',
        26: '+',
        27: '-'
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.counter = None
        self.operation = self.COUNTER_SET_MAP[skill.type]

    def description(self, converter):
        return 'counter {} {}'.format(self.operation, self.counter)


class ESSetCounterIf(ESLogic):
    skill_types = [38]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.counter_is = None
        self.counter = None

    def description(self, converter):
        return 'set counter = {} if counter == {}'.format(self.counter, self.counter_is)


class ESBranch(ESLogic):
    branch_condition = None

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.operation = '='
        self.branch_value = None
        self.target_round = None
        self.target_round_offset = 0

    def description(self, converter):
        return converter.branch(self.branch_condition, self.operation, self.branch_value, self.target_round)


class ESBranchFlag(ESBranch):
    skill_types = [43]
    branch_condition = 'flag'

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.operation = '&'


class ESBranchFlag0(ESBranchFlag):
    skill_types = [23]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        # For legacy reasons we treat all branches as 0 offset and manually offset by 1.
        # This +1 fixes it for this rarely used branch type.
        self.target_round_offset = 1


class ESBranchHP(ESBranch):
    skill_types = [28, 29]
    branch_condition = 'hp'
    HP_COMPARE_MAP = {
        28: '<',
        29: '>'
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.operation = self.HP_COMPARE_MAP[skill.type]


class ESBranchCounter(ESBranch):
    skill_types = [30, 31, 32]
    branch_condition = 'counter'
    COUNTER_COMPARE_MAP = {
        30: '<=',
        31: '=',
        32: '>='
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.operation = self.COUNTER_COMPARE_MAP[skill.type]


class ESBranchLevel(ESBranch):
    skill_types = [33, 34, 35]
    branch_condition = 'level'
    LEVEL_COMPARE_MAP = {
        33: '<=',
        34: '=',
        35: '>='
    }

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.operation = self.LEVEL_COMPARE_MAP[skill.type]


class ESBranchCard(ESBranch):
    skill_types = [90]
    branch_condition = 'player_cards'

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.operation = 'HAS'
        self.branch_cards = list(filter(None, self.params))
        self.branch_value = self.branch_cards

    def description(self, converter):
        return converter.branch(self.branch_condition, self.operation, self.branch_cards, self.target_round)


class ESBranchCombo(ESBranch):
    skill_types = [113]
    branch_condition = 'combo'

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.operation = '>='


class ESBranchDamageAttribute(ESBranch):
    skill_types = [114]
    branch_condition = 'color attacked with'

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.operation = '=='
        self.attributes = skill.params[1]


class ESBranchSkillUse(ESBranch):
    skill_types = [115]
    branch_condition = 'uses of skills'

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.operation = '>='


class ESBranchDamage(ESBranch):
    skill_types = [116]
    branch_condition = 'damage last turn'

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.branch_damage = skill.params[1]
        self.operation = '>='


class ESBranchEraseAttr(ESBranch):
    skill_types = [117]
    branch_condition = 'color erased'

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.operation = '=='
        self.branch_attrs_erased = skill.params[1]


class ESBranchRemainingEnemies(ESBranch):
    skill_types = [120]
    branch_condition = 'remaining enemies'

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.operation = '<='


class ESPreemptive(ESLogic):
    skill_types = [49]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)
        self.level = self.params[1]

    def description(self, converter):
        return 'Enable preempt if level {}'.format(self.level)


class ESEndPath(ESLogic):
    skill_types = [36]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self, converter):
        return 'end_turn'


class ESCountdown(ESLogic):
    skill_types = [37]

    def __init__(self, skill: EnemySkill):
        super().__init__(skill)

    def description(self, converter):
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

    def description(self, converter):
        return converter.countdown(self.current_counter)


class ESUseSkillset(ESBehavior):
    """Dummy action class to represent using a skillset"""

    def __init__(self, skillset_id=1):
        # ID is 1-indexed
        es_id = -9 - skillset_id
        raw = [str(es_id), 'Use Skill Set', '-3', '0']
        dummy_skill = EnemySkill(raw)
        super().__init__(dummy_skill)
        self.skillset_id = skillset_id

    def description(self, converter):
        return converter.use_skillset(self.skillset_id)


class ESUnknown(ESAction):  # Pretend to work so we can extract data
    """Unknown ES (Unknown skill type)"""


class ESInstance(Printable):
    def __init__(self, behavior: ESBehavior, ref: ESRef, monster_card: Card):
        self.enemy_skill_id = behavior.enemy_skill_id
        self.behavior = copy.deepcopy(behavior)
        self.condition = None  # type: Optional[ESCondition]
        self.ref = ref

        # self.ai = ref.enemy_ai
        # self.rnd = ref.enemy_rnd

        self.use_new_ai = monster_card.use_new_ai
        self.max_counter = monster_card.enemy_skill_max_counter
        self.increment = monster_card.enemy_skill_counter_increment

        if not isinstance(self.behavior, ESLogic):
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

        if isinstance(self.behavior, (ESRecoverEnemyAlly, ESAttackUPRemainingEnemies, ESTurnChangeRemainingEnemies)):
            self._ensure_condition(ref)
            self.condition.enemies_remaining = self.behavior.enemy_count

        if isinstance(self.behavior, (ESSkillSetOnDeath, ESDeathCry)):
            self._ensure_condition(ref)
            self.condition.on_death = True

        if isinstance(self.behavior, ESRandomSpawn):
            self._ensure_condition(ref)
            self.condition.condition_attributes = self.behavior.condition_attributes
        # End terrible badness

    def _ensure_condition(self, ref: ESRef):
        if not self.condition:
            self.condition = ESCondition(ref.enemy_ai, ref.enemy_rnd, self.behavior.params)

    @property
    def name(self):
        return self.behavior.name

    def description(self, converter):
        msg = self.condition.description(converter) if self.condition else ''
        msg = msg or ''
        msg += self.behavior.description(converter)
        return msg.strip()

    def __str__(self):
        return 'ESInstance - {} | {}'.format(self.behavior, self.ref)

    def __eq__(self, other):
        if isinstance(other, ESInstance):
            return self.enemy_skill_id == other.enemy_skill_id
        else:
            return False


ENEMY_SKILLS = [
    ESBindRandom,
    ESBindAttribute,
    ESBindTyping,
    ESOrbChangeSingle,
    ESBlind5,
    ESBlind62,
    ESDispel,
    ESRecoverEnemy7,
    ESRecoverEnemy86,
    ESStorePower,
    ESJammerChangeSingle,
    ESJammerChangeRandom,
    ESBindSkill,
    ESAttackMultihit,
    ESInactivity16,
    ESInactivity66,
    ESAttackUPRemainingEnemies,
    ESAttackUpStatus,
    ESAttackUPCooldown,
    ESStatusShield,
    ESDebuffMovetime,
    ESEndBattle,
    ESChangeAttribute,
    ESAttackPreemptive,
    ESOrbChangeAttack,
    ESGravity,
    ESRecoverEnemyAlly,
    ESAbsorbAttribute,
    ESBindTarget,
    ESRecoverPlayer,
    ESPoisonChangeSingle,
    ESPoisonChangeRandom,
    ESPoisonChangeRandomCount,
    ESMortalPoisonChangeRandom,
    ESBindAttack,
    ESPoisonChangeRandomAttack,
    ESBindRandomSub,
    ESAbsorbCombo,
    ESSkyfall,
    ESSkyfallLocked,
    ESDeathCry,
    ESVoidShield,
    ESDamageShield,
    ESLeaderSwap,
    ESColumnSpawnMulti,
    ESRowSpawnMulti,
    ESBoardChangeAttackFlat,
    ESAttackSinglehit,
    ESSkillSet,
    ESBoardChange,
    ESBoardChangeAttackBits,
    ESAbsorbThreshold,
    ESBindAwoken,
    ESSkillDelay,
    ESRandomSpawn,
    ESNone,
    ESOrbLock,
    ESSkillSetOnDeath,
    ESBlindStickyRandom,
    ESBlindStickyFixed,
    ESOrbSealColumn,
    ESOrbSealRow,
    ESFixedStart,
    ESBombRandomSpawn,
    ESBombFixedSpawn,
    ESCloud,
    ESDebuffRCV,
    ESAttributeBlock,
    ESOrbChangeAttackBits,
    ESSpinnersRandom,
    ESSpinnersFixed,
    ESMaxHPChange,
    ESFixedTarget,
    ESInvulnerableOn,
    ESInvulnerableOnHexazeon,
    ESInvulnerableOff,
    ESGachaFever,
    ESLeaderAlter,
    ESBoardSizeChange,
    ESNoSkyfall,
    ESComboSkyfall,
    ESFlagOperation,
    ESBranchFlag0,
    ESSetCounter,
    ESBranchHP,
    ESBranchCounter,
    ESBranchLevel,
    ESBranchDamageAttribute,
    ESBranchSkillUse,
    ESBranchDamage,
    ESBranchEraseAttr,
    ESEndPath,
    ESCountdown,
    ESSetCounterIf,
    ESBranchFlag,
    ESPreemptive,
    ESBranchCard,
    ESBranchCombo,
    ESBranchRemainingEnemies,
    ESAttributeResist,
    ESResolve,
    ESTurnChangePassive,
    ESTurnChangeRemainingEnemies,
    ESTypeResist,
    ESDebuffATK,
    ESSuperResolve,
    ESBlindStickySkyfall,
]

BEHAVIOR_MAP = {t: s for s in ENEMY_SKILLS for t in s.skill_types}
BEHAVIOR_MAP[0] = ESNone
BEHAVIOR_MAP[9] = ESUnknown
BEHAVIOR_MAP[21] = ESUnknown
BEHAVIOR_MAP[93] = ESNone  # FF Animation
BEHAVIOR_MAP[136] = ESNone  # Shikigami Animation
