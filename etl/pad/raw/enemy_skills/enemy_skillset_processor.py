"""
Contains code to convert a list of enemy behavior logic into a flattened structure
called a ProcessedSkillset.
"""
import collections
import copy
from typing import Set, Tuple, List, Optional

from pad.raw.card import Card, ESRef
from pad.raw.skills.enemy_skill_info import ESBranchAttrOnBoard, ESInstance, ESBehavior, ESEnrageAttackUp, \
    ESAttackUPRemainingEnemies, \
    ESAttackUPCooldown, ESDamageShield, ESStatusShield, ESAbsorbCombo, ESAbsorbAttribute, ESAbsorbThreshold, \
    ESDebuffMovetime, ESSkyfall, ESNoSkyfall, ESVoidShield, ESComboSkyfall, ESDebuffATK, ESDebuffRCV, ESCondition, \
    ESCountdownMessage, ESDefaultAttack, attribute_bitmap, ESNone, ESPreemptive, ESAttackPreemptive, ESAttackUpStatus, \
    ESUnknown, ESAction, ESDispel, ESBranchFlag, ESEndPath, ESFlagOperation, ESBranchHP, ESBranchLevel, ESSetCounter, \
    ESSetCounterIf, ESCountdown, ESBranchCounter, ESBranchCard, ESBranchCombo, ESBranchRemainingEnemies, \
    ESBranchEraseAttr, ESBranchDamage, ESBranchDamageAttribute, ESBranchSkillUse, ESPassive, ESDeathCry, \
    ESSkillSetOnDeath, ESRecoverEnemyAlly


class StandardSkillGroup(object):
    """Base class storing a list of skills."""

    def __init__(self, skills: List[ESInstance], hp_threshold):
        # List of skills which execute.
        self.skills = skills
        # The hp threshold that this group executes on, always present, even if 100.
        self.hp = hp_threshold

        self.hp_range = None  # type: Optional[int]

    def __eq__(self, other):
        return self.skills == other.skills


class TimedSkillGroup(StandardSkillGroup):
    """Set of skills which execute on a specific turn, possibly with a HP threshold."""

    def __init__(self, turn: int, hp_threshold: int, skills: List[ESInstance]):
        super().__init__(skills, hp_threshold)
        # The turn that this group executes on.
        self.turn = turn
        # If set, this group executes over a range of turns
        self.end_turn = None  # type: Optional[int]
        self.execute_above_hp = None


class RepeatSkillGroup(TimedSkillGroup):
    """Set of skills which execute on a specific turn, possibly with a HP threshold."""

    def __init__(self, turn: int, interval: int, hp_threshold: int, skills: List[ESInstance]):
        super().__init__(turn, hp_threshold, skills)
        # The number of turns between repeats, aka loop size
        self.interval = interval


class HpActions():
    def __init__(self, hp: int, timed: List[TimedSkillGroup], repeating: List[RepeatSkillGroup]):
        self.hp = hp
        self.timed = timed
        self.repeating = repeating


class Moveset(object):
    def __init__(self):
        # Action which triggers when a status is applied.
        self.status_action = None  # type: Optional[ESInstance]
        # Action which triggers when player has a buff.
        self.dispel_action = None  # type: Optional[ESInstance]
        # Timed and repeating actions which execute at various HP checkpoints.
        self.hp_actions = []  # type: List[HpActions]

    def has_actions(self):
        return any([self.status_action, self.dispel_action, self.hp_actions])


class EnemyRemainingMoveset(Moveset):
    def __init__(self, count: int):
        super().__init__()
        # Number of enemies required to trigger this set of actions.
        self.count = count


class ProcessedSkillset(object):
    """Flattened set of enemy skills.

    Skills are broken into chunks which are intended to be output independently,
    roughly in the order in which they're declared here.
    """

    def __init__(self, level: int, card: Card):
        # The monster level this skillset applies to.
        self.level = level
        # Things like color/type resists, resolve, etc.
        self.base_abilities = []  # type: List[ESInstance]
        # These automatically trigger when the monster dies
        self.death_actions = []  # type: List[ESInstance]
        # Preemptive attacks, shields, combo guards.
        self.preemptives = []  # type: List[ESInstance]

        # Default enemy actions.
        self.moveset = Moveset()

        # Alternate movesets which execute when a specific number of enemies remain.
        self.enemy_remaining_movesets = []  # type: List[EnemyRemainingMoveset]

        # Hint that we shouldn't accept enemy remaining conditions.
        self.enemy_remaining_enabled = card.unknown_009 != 5

    def has_actions(self):
        return any([self.base_abilities,
                    self.death_actions,
                    self.preemptives,
                    self.enemy_remaining_movesets,
                    self.moveset.has_actions()])


class Context(object):
    """Represents the game state when running through the simulator."""

    def __init__(self, level: int, max_skill_counter: int, skill_counter_increment: int, long_loop: bool):
        self.turn = 1
        # Whether the current turn triggered a preempt flag.
        self.is_preemptive = False
        # A bitmask for flag values which can be updated.
        self.flags = 0
        # A bitmask for flag values which can only be unset.
        self.skill_use = 0
        # Special flag that is modified by the 'counter' operations.
        self.counter = 0
        # Current HP value.
        self.hp = 100
        # Monster level, toggles some behaviors.
        self.level = level
        # Number of enemies on the screen.
        self.enemies = 999
        # Cards on the team.
        self.cards = set()
        # Combos made in previous round.
        self.combos = 0
        # Attributes erased in the previous round
        self.attributes_erased = 0
        # Damage done in the previous round
        self.attributes_on_board = 0
        # Damage done in the previous round
        self.damage_done = 0
        # attributes attacked with in previous round
        self.attributes_attacked = 0
        # number of skills used
        self.skills_used = 0
        # Turns of enrage, initial:None -> (enrage cooldown period:int<0 ->) enrage:int>0 -> expire:int=0
        self.enraged = None
        # Turns of damage shield, initial:int=0 -> shield up:int>0 -> expire:int=0
        self.damage_shield = 0
        # Turns of status shield, initial:int=0 -> shield up:int>0 -> expire:int=0
        self.status_shield = 0
        # Turns of combo shield, initial:int=0 -> shield up:int>0 -> expire:int=0
        self.combo_shield = 0
        # Turns of attribute absorb shield, initial:int=0 -> shield up:int>0 -> expire:int=0
        self.attribute_shield = 0
        # Turns of damage absorb shield, initial:int=0 -> shield up:int>0 -> expire:int=0
        self.absorb_shield = 0
        # Turns of damage void shield, initial:int=0 -> shield up:int>0 -> expire:int=0
        self.void_shield = 0
        # Turns of time debuff, initial:int=0 -> shield up:int>0 -> expire:int=0
        self.time_debuff = 0
        # Turns of skyfall, initial:int=0 -> skyfall up:int>0 -> expire:int=0
        self.skyfall = 0
        # Turns of no skyfall, initial:int=0 -> skyfall off:int>0 -> expire:int=0
        self.no_skyfall = 0
        # Turns of combo skyfall, initial:int=0 -> skyfall combo:int>0 -> expire:int=0
        self.combo_skyfall = 0
        # Turns of attack down, initial:int=0 -> attack down:int>0 -> expire:int=0
        self.attack_down = 0
        # Turns of rcv down, initial:int=0 -> rcv down:int>0 -> expire:int=0
        self.rcv_down = 0

        # The current skill counter value, initialized to max.
        self.skill_counter = max_skill_counter
        # The max value for the skill counter.
        self.max_skill_counter = max_skill_counter
        # the amount to increment the skill counter by each turn.
        self.skill_counter_increment = skill_counter_increment

        # The flag values for one-time skills.
        self.flag_skill_use = 0

        # Determines how many times we should loop looking for repeats
        self.long_loop = long_loop

    def reset(self):
        self.is_preemptive = False

    def clone(self):
        return copy.deepcopy(self)

    def turn_event(self, enraged_this_turn: bool):
        self.turn += 1
        if self.enraged is not None and not enraged_this_turn:
            if self.enraged > 0:
                # count down enraged turns
                self.enraged -= 1
            elif self.enraged < 0:
                # count up enraged cooldown turns
                self.enraged += 1

        # count down shield turns
        if self.damage_shield > 0:
            self.damage_shield -= 1
        if self.status_shield > 0:
            self.status_shield -= 1
        if self.combo_shield > 0:
            self.combo_shield -= 1
        if self.attribute_shield > 0:
            self.attribute_shield -= 1
        if self.absorb_shield > 0:
            self.absorb_shield -= 1
        if self.void_shield > 0:
            self.void_shield -= 1
        if self.time_debuff > 0:
            self.time_debuff -= 1
        if self.skyfall > 0:
            self.skyfall -= 1
        if self.no_skyfall > 0:
            self.no_skyfall -= 1
        if self.combo_skyfall > 0:
            self.combo_skyfall -= 1
        if self.attack_down > 0:
            self.attack_down -= 1
        if self.rcv_down > 0:
            self.rcv_down -= 1

    def apply_skill_effects(self, b: ESBehavior) -> bool:
        """Check context to see if a skill is allowed to be used, and update flag accordingly"""
        if isinstance(b, ESEnrageAttackUp):
            if isinstance(b, ESAttackUPRemainingEnemies) \
                    and b.enemy_count is not None \
                    and self.enemies > b.enemy_count:
                return False
            if self.enraged is None:
                if isinstance(b, ESAttackUPCooldown) and b.turn_cooldown is not None:
                    self.enraged = -b.turn_cooldown + 1
                    return False
                else:
                    self.enraged = b.turns
                    return True
            else:
                if self.enraged == 0:
                    self.enraged = b.turns
                    return True
                else:
                    return False
        elif isinstance(b, ESDamageShield):
            if self.damage_shield == 0:
                self.damage_shield = b.turns
                return True
            else:
                return False
        elif isinstance(b, ESStatusShield):
            if self.status_shield == 0:
                self.status_shield = b.turns
                return True
            else:
                return False
        elif isinstance(b, ESAbsorbCombo):
            if self.combo_shield == 0:
                self.combo_shield = b.max_turns
                return True
            else:
                return False
        elif isinstance(b, ESAbsorbAttribute):
            if self.attribute_shield == 0:
                self.attribute_shield = b.max_turns
                return True
            else:
                return False
        elif isinstance(b, ESAbsorbThreshold):
            if self.absorb_shield == 0:
                self.absorb_shield = b.turns
                return True
            else:
                return False
        elif isinstance(b, ESVoidShield):
            if self.void_shield == 0:
                self.void_shield = b.turns
                return True
            else:
                return False
        elif isinstance(b, ESDebuffMovetime):
            if self.time_debuff == 0:
                self.time_debuff = b.turns + 1  # This ticks down after enemy movement, so add 1
                return True
            else:
                return False
        elif isinstance(b, ESSkyfall):
            if self.skyfall == 0:
                self.skyfall = b.max_turns
                return True
            else:
                return False
        elif isinstance(b, ESNoSkyfall):
            if self.no_skyfall == 0:
                self.no_skyfall = b.turns
                return True
            else:
                return False
        elif isinstance(b, ESComboSkyfall):
            if self.combo_skyfall == 0:
                self.combo_skyfall = b.turns
                return True
            else:
                return False
        elif isinstance(b, ESDebuffATK):
            if self.attack_down == 0:
                self.attack_down = b.turns
                return True
            else:
                return False
        elif isinstance(b, ESDebuffRCV):
            if self.rcv_down == 0:
                self.rcv_down = b.turns
                return True
            else:
                return False

        return True

    def check_no_apply_skill_effects(self, b: ESBehavior) -> bool:
        """Check context to see if a skill is allowed to be used"""
        if isinstance(b, ESEnrageAttackUp):
            if isinstance(b, ESAttackUPRemainingEnemies) \
                    and b.enemy_count is not None \
                    and self.enemies > b.enemy_count:
                return False
            if self.enraged is None:
                if isinstance(b, ESAttackUPCooldown) and b.turn_cooldown is not None:
                    return False
                else:
                    return True
            else:
                return self.enraged == 0
        elif isinstance(b, ESDamageShield):
            return self.damage_shield == 0
        elif isinstance(b, ESStatusShield):
            return self.status_shield == 0
        elif isinstance(b, ESAbsorbCombo):
            return self.combo_shield == 0
        elif isinstance(b, ESAbsorbAttribute):
            return self.attribute_shield == 0
        elif isinstance(b, ESAbsorbThreshold):
            return self.absorb_shield == 0
        elif isinstance(b, ESVoidShield):
            return self.void_shield == 0
        elif isinstance(b, ESDebuffMovetime):
            return self.time_debuff == 0
        elif isinstance(b, ESSkyfall):
            return self.skyfall == 0
        elif isinstance(b, ESNoSkyfall):
            return self.no_skyfall == 0
        elif isinstance(b, ESComboSkyfall):
            return self.combo_skyfall == 0
        elif isinstance(b, ESDebuffATK):
            return self.attack_down == 0
        elif isinstance(b, ESDebuffRCV):
            return self.rcv_down == 0

        return True

    def check_skill_use(self, cond: ESCondition):
        result = True
        if cond.one_time:
            result = result and self.skill_counter >= cond.one_time
        if cond.forced_one_time:
            result = result and self.flag_skill_use and cond.forced_one_time == 0
        if cond.enemies_remaining:
            result = result and self.enemies <= cond.enemies_remaining
        return result

    def update_skill_use(self, cond: ESCondition):
        if cond.one_time:
            self.skill_counter -= cond.one_time
        elif cond.forced_one_time:
            self.flag_skill_use |= cond.forced_one_time

    def increment_skill_counter(self):
        self.skill_counter = min(self.skill_counter + self.skill_counter_increment, self.max_skill_counter)

    def is_enraged(self):
        return (self.enraged or 0) > 0


def wrap_with_instance(behavior):
    FakeCard = collections.namedtuple('Card', 'use_new_ai enemy_skill_max_counter enemy_skill_counter_increment')
    fake_card = FakeCard(use_new_ai=False, enemy_skill_max_counter=0, enemy_skill_counter_increment=0)
    fake_ref = ESRef(behavior.enemy_skill_id, 100, 0)
    return ESInstance(behavior, fake_ref, fake_card)  # noqa


def countdown_message():
    return wrap_with_instance(ESCountdownMessage())


def default_attack():
    """Indicates that the monster uses its standard attack."""
    return wrap_with_instance(ESDefaultAttack())


def loop_through(ctx, behaviors: List[Optional[ESInstance]]) -> List[ESInstance]:
    original_ctx = ctx.clone()
    results, card_branches, combo_branches, erase_attribute_branches, on_board_attribute_branches, damage_branches, \
    attributes_attacked_branches, skill_use_branches = loop_through_inner(ctx, behaviors)
    # Handle extracting alternate actions based on card values
    card_extra_actions = []
    for card_ids in sorted(card_branches):
        card_ctx = original_ctx.clone()
        card_ctx.cards.update(card_ids)
        card_loop, *_ = loop_through_inner(card_ctx, behaviors)
        new_behaviors = [x for x in card_loop if x not in results]

        # Update the description to distinguish
        for nb in new_behaviors:
            nb.condition.cards_on_team = list(card_ids)

        # Some branches set flags to prevent them from triggering again
        ctx.flags |= card_ctx.flags
        card_extra_actions.extend(new_behaviors)

    # Add any alternate preempts
    for nb in card_extra_actions:
        results.insert(0, nb)

    # Handle extracting alternate actions based on combo values
    combo_extra_actions = []
    for combo_count in sorted(combo_branches):
        combo_ctx = original_ctx.clone()
        combo_ctx.combos = combo_count
        combo_loop, *_ = loop_through_inner(combo_ctx, behaviors)
        new_behaviors = [x for x in combo_loop if x not in results]

        # Update the description to distinguish
        for nb in new_behaviors:
            nb.condition.combos_made = combo_count

        combo_extra_actions.extend(new_behaviors)

    # Add any alternate preempts
    for nb in combo_extra_actions:
        results.insert(0, nb)

    # Handle extracting alternate actions based on erased attributes
    erased_attribute_extra_actions = []
    for erase_attribute in erase_attribute_branches:
        erased_attribute_ctx = original_ctx.clone()
        erased_attribute_ctx.attributes_erased = erase_attribute
        erased_loop, *_ = loop_through_inner(erased_attribute_ctx, behaviors)
        new_behaviors = [x for x in erased_loop if x not in results]

        # Update the description to distinguish
        for nb in new_behaviors:
            nb.condition.attributes_erased = attribute_bitmap(erase_attribute)

        erased_attribute_extra_actions.extend(new_behaviors)

    # Add any alternate preempts
    for nb in erased_attribute_extra_actions:
        results.insert(0, nb)

    # Handle extracting alternate actions based on attributes existing on board
    on_board_attribute_extra_actions = []
    for on_board_attribute in on_board_attribute_branches:
        on_board_attribute_ctx = original_ctx.clone()
        on_board_attribute_ctx.attributes_on_board = on_board_attribute
        on_board_loop, *_ = loop_through_inner(on_board_attribute_ctx, behaviors)
        new_behaviors = [x for x in on_board_loop if x not in results]

        # Update the description to distinguish
        for nb in new_behaviors:
            nb.condition.attributes_on_board = attribute_bitmap(on_board_attribute)

        on_board_attribute_extra_actions.extend(new_behaviors)

    # Add any alternate preempts
    for nb in on_board_attribute_extra_actions:
        results.insert(0, nb)

    # Handle extracting alternate actions based on damage done
    damage_extra_actions = []
    for damage in damage_branches:
        damage_ctx = original_ctx.clone()
        damage_ctx.damage_done = damage
        damage_loop, *_ = loop_through_inner(damage_ctx, behaviors)
        new_behaviors = [x for x in damage_loop if x not in results]

        # Update the description to distinguish
        for nb in new_behaviors:
            nb.condition.damage_done = damage

        damage_extra_actions.extend(new_behaviors)

    # Add any alternate preempts
    for nb in damage_extra_actions:
        results.insert(0, nb)

    # Handle extracting alternate actions based on erased attributes
    attributes_attacked_extra_actions = []
    for attribute_attacked in attributes_attacked_branches:
        attribute_attacked_ctx = original_ctx.clone()
        attribute_attacked_ctx.attributes_attacked = attribute_attacked
        attacked_loop, *_ = loop_through_inner(attribute_attacked_ctx, behaviors)
        new_behaviors = [x for x in attacked_loop if x not in results]

        # Update the description to distinguish
        for nb in new_behaviors:
            nb.condition.attributes_attacked = attribute_bitmap(attribute_attacked)

        attributes_attacked_extra_actions.extend(new_behaviors)

    # Add any alternate preempts
    for nb in attributes_attacked_extra_actions:
        results.insert(0, nb)

    # Handle extracting alternate actions based on erased attributes
    skill_use_extra_actions = []
    for skill_use in skill_use_branches:
        skill_use_ctx = original_ctx.clone()
        skill_use_ctx.skills_used = skill_use
        skill_use_loop, *_ = loop_through_inner(skill_use_ctx, behaviors)
        new_behaviors = [x for x in skill_use_loop if x not in results]

        # Update the description to distinguish
        for nb in new_behaviors:
            nb.condition.skills_used = skill_use

        skill_use_extra_actions.extend(new_behaviors)

    # Add any alternate preempts
    for nb in skill_use_extra_actions:
        results.insert(0, nb)

    ctx.increment_skill_counter()
    for r in results:
        cond = r.condition
        if cond and cond.use_chance(hp=ctx.hp) == 100 and (cond.one_time or cond.forced_one_time):
            # Handle single counter / fixed cost items
            ctx.update_skill_use(r.condition)
            break

    return results


def loop_through_inner(ctx: Context, behaviors: List[Optional[ESInstance]]) -> \
        Tuple[List[ESInstance], List[List[int]], List[int], List[int], List[int], List[int], List[int], List[int]]:
    """Executes a single turn through the simulator.

    This is called multiple times with varying Context values to probe the action set
    of the monster.
    """
    ctx.reset()
    # The list of behaviors identified for this loop.
    results = []
    # A list of behaviors which have been iterated over.
    traversed = []

    # If any BranchCard instructions were spotted
    card_branches = []  # type: List[List[int]]
    # If any BranchCombo instructions were spotted
    combo_branches = []  # type: List[int]
    # If any BranchEraseAttribute instructions were spotted
    erase_attribute_branches = []  # type: List[int]
    # If any BranchAttrOnBoard instructions were spotted
    on_board_attribute_branches = []  # type: List[int]
    # If any BranchDamage instructions were spotted
    damage_branches = []  # type: List[int]
    # If any BranchDamageAttribute instructions were spotted
    attributes_attacked_branches = []  # type: List[int]
    # If any BranchSkillUse instructions were spotted
    skills_used_branches = []  # type: List[int]

    # The current spot in the behavior array.
    idx = 0
    # Number of iterations we've done.
    iter_count = 0
    while iter_count < 1000:
        # Safety measures against infinite loops, check if we've looped too many
        # times or if we've seen this behavior before in the current loop.
        iter_count += 1
        if idx >= len(behaviors) or idx in traversed:
            # Disabling default action for now; doesn't seem to improve things?
            # if len(results) == 0:
            #     # if the result set is empty, add something
            #     results.append(default_attack())
            return results, card_branches, combo_branches, erase_attribute_branches, on_board_attribute_branches,\
                   damage_branches, attributes_attacked_branches, skills_used_branches
        traversed.append(idx)

        # Extract the current behavior and its type.
        instance = behaviors[idx]
        if instance is None or isinstance(instance.behavior, ESNone):
            # The current action could be None because we nulled it out in preprocessing, just continue.
            idx += 1
            continue

        b = instance.behavior
        cond = instance.condition

        # Detection for preempts, null the behavior afterwards so we don't trigger it again.
        if isinstance(b, ESPreemptive):
            behaviors[idx] = None
            ctx.is_preemptive = b.level <= ctx.level
            idx += 1
            continue

        if isinstance(b, ESAttackPreemptive):
            behaviors[idx] = None
            ctx.is_preemptive = True
            results.append(instance)
            return (results, card_branches, combo_branches, erase_attribute_branches, on_board_attribute_branches,
                    damage_branches, attributes_attacked_branches, skills_used_branches)

        if isinstance(b, ESAttackUpStatus):
            # This is a special case; it's not a terminal action unlike other enrages.
            results.append(instance)
            idx += 1
            continue

        # Processing for actions and unparsed stuff, this section should accumulate
        # items into results.
        if isinstance(b, (ESUnknown, ESAction)):
            # Check if we should execute this action at all.
            if cond:
                use_chance_at_hp = cond.use_chance(hp=ctx.hp)
                # This skill can never execute at this HP; either AI is 0 or the HP is below the threshold
                if use_chance_at_hp == 0:
                    idx += 1
                    continue

                if use_chance_at_hp == 100 and not isinstance(b, ESDispel):
                    # This always executes so it is a terminal action.
                    if not ctx.check_skill_use(cond):
                        idx += 1
                        continue
                    if not ctx.apply_skill_effects(b):
                        idx += 1
                        continue
                    results.append(instance)
                    if b.is_conditional():
                        idx += 1
                        continue
                    return (results, card_branches, combo_branches, erase_attribute_branches,
                            on_board_attribute_branches, damage_branches, attributes_attacked_branches,
                            skills_used_branches)
                else:
                    # Not a terminal action, so accumulate it and continue.
                    if ctx.check_skill_use(cond) and ctx.check_no_apply_skill_effects(b):
                        results.append(instance)
                    idx += 1
                    continue
            else:
                # Stuff without a condition is always terminal.
                if not ctx.apply_skill_effects(b):
                    idx += 1
                    continue
                return (results, card_branches, combo_branches, erase_attribute_branches, on_board_attribute_branches,
                        damage_branches, attributes_attacked_branches, skills_used_branches)

        if isinstance(b, ESBranchFlag):
            if b.branch_value == b.branch_value & ctx.flags:
                # If we satisfy the flag, branch to it.
                idx = b.target_round
            else:
                # Otherwise move to the next action.
                idx += 1
            continue

        if isinstance(b, ESEndPath):
            # Forcibly ends the loop, generally used after multiple <100% actions.
            # Disabling default action for now; doesn't seem to improve things?
            # if len(results) == 0:
            #     # if the result set is empty, add something
            #     results.append(default_attack())
            return (results, card_branches, combo_branches, erase_attribute_branches, on_board_attribute_branches,
                    damage_branches, attributes_attacked_branches, skills_used_branches)

        if isinstance(b, ESFlagOperation):
            # Operations which change flag state, we always move to the next behavior after.
            if b.operation == 'OR':
                ctx.flags = ctx.flags | b.flag
            elif b.operation == 'SET':
                ctx.flags = b.flag
            elif b.operation == 'UNSET':
                ctx.flags = ctx.flags & ~b.flag
            else:
                raise ValueError('unsupported flag operation:', b.operation)
            idx += 1
            continue

        if isinstance(b, ESBranchHP):
            # Branch based on current HP.
            if b.operation == '<':
                take_branch = ctx.hp < b.branch_value
            else:
                take_branch = ctx.hp >= b.branch_value
            idx = b.target_round if take_branch else idx + 1
            continue

        if isinstance(b, ESBranchLevel):
            # Branch based on monster level.
            if b.operation == '<=':
                take_branch = ctx.level <= b.branch_value
            elif b.operation == '=':
                take_branch = ctx.level == b.branch_value
            else:
                take_branch = ctx.level >= b.branch_value
            idx = b.target_round if take_branch else idx + 1
            continue

        if isinstance(b, ESSetCounter):
            # Adjust the global counter value.
            if b.operation == '=':
                ctx.counter = b.counter
            elif b.operation == '+':
                ctx.counter += b.counter
            elif b.operation == '-':
                ctx.counter -= b.counter
            idx += 1
            continue

        if isinstance(b, ESSetCounterIf):
            # Adjust the counter if it has a specific value.
            if ctx.counter == b.counter_is:
                ctx.counter = b.counter
            idx += 1
            continue

        if isinstance(b, ESCountdown):
            ctx.counter -= 1
            if ctx.counter > 0:
                results.append(countdown_message())
                return (results, card_branches, combo_branches, erase_attribute_branches, on_board_attribute_branches,
                        damage_branches, attributes_attacked_branches, skills_used_branches)
            else:
                idx += 1
                continue

        if isinstance(b, ESBranchCounter):
            # Branch based on the counter value.
            if b.operation == '=':
                take_branch = ctx.counter == b.branch_value
            elif b.operation == '<=':
                take_branch = ctx.counter <= b.branch_value
            elif b.operation == '>=':
                take_branch = ctx.counter >= b.branch_value
            else:
                raise ValueError('unsupported counter operation:', b.operation)
            idx = b.target_round if take_branch else idx + 1
            continue

        if isinstance(b, ESBranchCard):
            # Branch if it's checking for a card we have on the team.
            card_on_team = any([card in ctx.cards for card in b.branch_cards])
            idx = b.target_round if card_on_team else idx + 1
            card_branches.append(b.branch_cards)
            continue

        if isinstance(b, ESBranchCombo):
            # Branch if we made the appropriate number of combos last round.
            idx = b.target_round if ctx.combos >= b.branch_value else idx + 1
            combo_branches.append(b.branch_value)
            continue

        if isinstance(b, ESBranchRemainingEnemies):
            # TODO: This should be <= probably
            idx = b.target_round if ctx.enemies == b.branch_value else idx + 1
            continue

        if isinstance(b, ESBranchEraseAttr):
            # Branch if we erased the appropriate attributes last round
            idx = b.target_round if ctx.attributes_erased == b.branch_attrs_erased else idx + 1
            erase_attribute_branches.append(b.branch_attrs_erased)
            continue

        if isinstance(b, ESBranchAttrOnBoard):
            # Branch if an attribute appears on the board
            idx = b.target_round if ctx.attributes_on_board == b.branch_attr else idx + 1
            on_board_attribute_branches.append(b.branch_attr)
            continue

        if isinstance(b, ESBranchDamage):
            # Branch if we did enough damage
            idx = b.target_round if ctx.damage_done >= b.branch_damage else idx + 1
            damage_branches.append(b.branch_damage)
            continue

        if isinstance(b, ESBranchDamageAttribute):
            # Branch if we attacked with the appropriate attributes last round
            idx = b.target_round if ctx.attributes_attacked == b.attributes else idx + 1
            attributes_attacked_branches.append(b.attributes)
            continue

        if isinstance(b, ESBranchSkillUse):
            # Branch if we made the appropriate number of active skills last round.
            idx = b.target_round if ctx.skills_used >= b.branch_value else idx + 1
            skills_used_branches.append(b.branch_value)
            continue

        raise ValueError('unsupported operation:', type(b), b)

    if iter_count == 1000:
        print('error, iter count exceeded 1000')
    return (results, card_branches, combo_branches, erase_attribute_branches, on_board_attribute_branches,
            damage_branches, attributes_attacked_branches, skills_used_branches)


def info_from_behaviors(behaviors: List[Optional[ESInstance]]):
    """Extract some static info from the behavior list and clean it up where necessary."""
    base_abilities = []
    death_actions = []
    hp_checkpoints = set()
    hp_checkpoints.add(100)
    hp_checkpoints.add(0)
    card_checkpoints = set()
    has_enemy_remaining_branch = False

    for idx, instance in enumerate(behaviors):
        if instance is None:
            continue

        cond = instance.condition
        es = instance.behavior

        # Extract the passives and null them out to simplify processing
        if isinstance(es, ESPassive):
            base_abilities.append(instance)
            behaviors[idx] = None
            continue

        # Extract death actions and null them out
        if isinstance(es, (ESDeathCry, ESSkillSetOnDeath)):
            # Skip pointless death actions
            if es.has_action():
                death_actions.append(instance)
            behaviors[idx] = None
            continue

        # Find candidate branch HP values
        if isinstance(es, ESBranchHP):
            hp_checkpoints.add(es.branch_value)
            hp_checkpoints.add(es.branch_value - 1)

        # Find candidate action HP values
        if cond and cond.hp_threshold:
            hp_checkpoints.add(cond.hp_threshold)
            hp_checkpoints.add(cond.hp_threshold - 1)

        # Find checks for specific cards.
        if isinstance(es, ESBranchCard):
            card_checkpoints.add(tuple(es.branch_cards))

        # Find checks for specific amounts of enemies.
        if isinstance(es, (ESBranchRemainingEnemies, ESAttackUPRemainingEnemies, ESRecoverEnemyAlly)):
            has_enemy_remaining_branch = True

    return base_abilities, hp_checkpoints, card_checkpoints, has_enemy_remaining_branch, death_actions


def extract_preemptives(ctx: Context, behaviors: List[ESInstance], card_checkpoints: Set[Tuple[int]]):
    """Simulate the initial run through the behaviors looking for preemptives.

    If we find a preemptive, continue onwards. If not, roll the context back.
    """
    original_ctx = ctx.clone()

    cur_loop = loop_through(ctx, behaviors)
    if not ctx.is_preemptive:
        # Roll back the context.
        return original_ctx, None

    # Save the current loop as preempt
    return ctx, cur_loop


def extract_turn_behaviors(ctx: Context, behaviors: List[ESInstance], hp_checkpoint: int) -> List[List[ESInstance]]:
    """Simulate the first 20 turns at a specific hp checkpoint."""
    hp_ctx = ctx.clone()
    hp_ctx.hp = hp_checkpoint
    turn_data = []
    loop_search_size = 40 if ctx.long_loop else 20
    for idx in range(0, loop_search_size):
        started_enraged = hp_ctx.is_enraged()
        turn_data.append(loop_through(hp_ctx, behaviors))
        enraged_this_turn = not started_enraged and hp_ctx.is_enraged()
        hp_ctx.turn_event(enraged_this_turn)

    return turn_data


def extract_loop_indexes(turn_data: List[List[ESBehavior]]) -> Tuple[int, int]:
    """Find loops in the data."""
    # Loop over every turn
    for i_idx, check_data in enumerate(turn_data):
        # Loop over every following turn. If the outer turn matches an inner turn moveset,
        # we found a loop.
        possible_loops = []
        for j_idx in range(i_idx + 1, len(turn_data)):
            comp_data = turn_data[j_idx]
            if check_data == comp_data:
                possible_loops.append((i_idx, j_idx))
        if len(possible_loops) == 0:
            continue

        # Check all possible loops
        for check_start, check_end in possible_loops.copy():
            # Now that we found a loop, confirm that it continues
            loop_behavior = turn_data[check_start:check_end]
            loop_verified = False

            for j_idx in range(check_end, len(turn_data), len(loop_behavior)):
                # Check to make sure we don't run over the edge of the array
                j_loop_end_idx = j_idx + len(loop_behavior)
                if j_loop_end_idx > len(turn_data):
                    # We've overlapped the end of the array with no breaks, quit
                    break

                comp_data = turn_data[j_idx:j_loop_end_idx]
                loop_verified = loop_behavior == comp_data
                if not loop_verified:
                    break

            if not loop_verified:
                # The loop didn't continue so this is a bad selection, remove
                possible_loops.remove((check_start, check_end))

        if len(possible_loops) > 0:
            return possible_loops[0][0], possible_loops[0][1]
    raise Exception('No loop found')


def extract_loop_skills(hp: int, turn_data: list, loop_start: int, loop_end: int) -> HpActions:
    """Create timed and repeating skill groups."""
    timed_skill_groups = []
    if loop_start > 0:
        for idx in range(0, loop_start):
            timed_skill_groups.append(TimedSkillGroup(idx + 1, hp, turn_data[idx]))

    loop_size = loop_end - loop_start
    repeating_skill_groups = []
    for idx in range(loop_start, loop_end):
        repeating_skill_groups.append(RepeatSkillGroup(idx + 1 - loop_start, loop_size, hp, turn_data[idx]))

    return HpActions(hp, timed_skill_groups, repeating_skill_groups)


def compute_enemy_actions(ctx: Context, behaviors: List[ESInstance], hp_checkpoints: List[int]) -> List[HpActions]:
    # Compute turn behaviors for every hp checkpoint
    hp_to_turn_behaviors = {hp: extract_turn_behaviors(ctx, behaviors, hp) for hp in hp_checkpoints}

    # Convert turn behaviors into fixed turns and repeating loops.
    hp_to_actions = {}  # type Map[int, HpActions]
    for hp, turn in hp_to_turn_behaviors.items():
        loop_start, loop_end = extract_loop_indexes(turn)
        hp_to_actions[hp] = extract_loop_skills(hp, turn, loop_start, loop_end)

    # Starting from the top hp bracket and extending down, compute the true timed actions.
    for chp_idx in range(len(hp_checkpoints)):
        # Extract the hp, and timed actions for the current index.
        hp = hp_checkpoints[chp_idx]
        actions = hp_to_actions[hp]
        timed = actions.timed
        # Loop over every timed action.
        for turn_idx in range(len(timed)):
            cur_skills = timed[turn_idx].skills
            # Loop over every subsequent hp checkpoint
            for nhp_idx in range(chp_idx + 1, len(hp_checkpoints)):
                comp_hp = hp_checkpoints[nhp_idx]
                comp_actions = hp_to_actions[comp_hp]
                # Check if the checkpoint has a timed action at that slot, and
                # if it is equivalent. If so, smear the parent to that hp and
                # delete the child.
                # This takes care of 'true' timed actions (actions which always execute on turn n)
                # as well as hp thresholded actions that span checkpoints.
                comp_timed = comp_actions.timed
                if turn_idx >= len(comp_timed):
                    # This timed set had less slots than the parent, we're done.
                    break

                if cur_skills == comp_timed[turn_idx].skills:
                    # This timed skill can execute at multiple checkpoints; we want this to be
                    # the following checkpoint, because it encompases the next checkpoint. If there
                    # is no next checkpoint, we use 1 as a placeholder for 'always execute'.
                    next_comp_hp = hp_checkpoints[nhp_idx + 1] if nhp_idx < len(hp_checkpoints) - 1 else 1
                    timed[turn_idx].execute_above_hp = next_comp_hp

                    # Clear out the dupe timed skill.
                    comp_timed[turn_idx].skills.clear()
                    timed[turn_idx].hp_range = comp_hp

        repeating = actions.repeating
        # Loop over the repeating action set at each checkpoint. If the whole repeating action
        # set is equivalent, smear it.
        for nhp_idx in range(chp_idx + 1, len(hp_checkpoints)):
            comp_hp = hp_checkpoints[nhp_idx]
            comp_actions = hp_to_actions[comp_hp]
            comp_repeating = comp_actions.repeating
            if make_repeating_comparable(hp, repeating) == make_repeating_comparable(comp_hp, comp_repeating):
                for x in repeating:
                    x.hp_range = comp_hp
                comp_repeating.clear()
            else:
                # Don't continue scraping away if the intervening hp threshold is different.
                # This fixes things like where the full HP turnset is X and the < N HP turnset
                # is also X.
                break

    return list(sorted(hp_to_actions.values(), key=lambda act: act.hp, reverse=True))


def make_repeating_comparable(hp: int, repeating: List[RepeatSkillGroup]):
    """Helper function to make a repeating skill group comparable against another one.

    A group is effectively comparable if it has the same skill ids in the same order, with the same use chance
    with each skill. This handles the case where the skill groups can be the same, but one subskill can have a higher
    rate at a lower threshold; we don't want to lose this information.
    """
    return [(y.enemy_skill_id, y.condition.use_chance(hp)) for x in repeating for y in x.skills]


def convert(card: Card, enemy_behavior: List[ESInstance], level: int, long_loop: bool) -> ProcessedSkillset:
    force_one_enemy = int(card.unknown_009) == 5 and (
            card.monster_no % 100000 not in [4227, 5119])  # hacky fix for hexa/qilin
    enemy_skill_max_counter = card.enemy_skill_max_counter
    enemy_skill_counter_increment = card.enemy_skill_counter_increment

    skillset = ProcessedSkillset(level, card)

    # Behavior is 1-indexed, so stick a fake row in to start
    # It's actually not, this is a lie. Most branches are just 1-indexed.
    behaviors = [None]  # type: List[Optional[ESInstance]]
    behaviors += list(enemy_behavior)

    (base_abilities, hp_checkpoints, card_checkpoints,
     has_enemy_remaining_branch, death_actions) = info_from_behaviors(behaviors)
    skillset.base_abilities = base_abilities
    skillset.death_actions = death_actions

    # Ensure the HP checkpoints are in descended order
    hp_checkpoints = sorted(hp_checkpoints, reverse=True)
    ctx = Context(level, enemy_skill_max_counter, enemy_skill_counter_increment, long_loop)

    if force_one_enemy:
        ctx.enemies = 1
        has_enemy_remaining_branch = False

    ctx, preemptives = extract_preemptives(ctx, behaviors, card_checkpoints)
    if ctx is None:
        # Some monsters have no skillset at all
        return skillset

    if preemptives is not None:
        skillset.preemptives = preemptives
        if any([p.behavior.ends_battle() for p in preemptives]):
            # This monster terminates the battle immediately.
            return skillset

    # Compute the standard action moveset
    hp_actions = compute_enemy_actions(ctx.clone(), behaviors, hp_checkpoints)
    clean_skillset(skillset.moveset, hp_actions)

    # Simulate enemies being defeated
    if has_enemy_remaining_branch:
        enemy_movesets = []
        # Loop from 6 back to 1, simulating possible movesets.
        for ecount in range(6, 0, -1):
            enemy_moveset = EnemyRemainingMoveset(ecount)
            enemy_ctx = ctx.clone()
            enemy_ctx.enemies = ecount
            enemy_actions = compute_enemy_actions(enemy_ctx, behaviors, hp_checkpoints)
            clean_skillset(enemy_moveset, enemy_actions)
            enemy_movesets.append(enemy_moveset)

        # Dedupe the enemy remaining movesets, with the 'standard' moveset as the
        # initial state. We only want to keep deltas from that state.
        all_movesets = [skillset.moveset] + enemy_movesets
        for cms_idx in range(len(all_movesets)):
            cms = all_movesets[cms_idx]

            for nms_idx in range(cms_idx + 1, len(all_movesets)):
                nms = all_movesets[nms_idx]

                if cms.dispel_action == nms.dispel_action:
                    nms.dispel_action = None
                if cms.status_action == nms.status_action:
                    nms.status_action = None

                for cms_action in cms.hp_actions:
                    nms_action = find_action_by_hp(cms_action.hp, nms.hp_actions)
                    if nms_action is None:
                        continue

                    if cms_action.timed == nms_action.timed:
                        nms_action.timed.clear()
                    if cms_action.repeating == nms_action.repeating:
                        nms_action.repeating.clear()

        for moveset in enemy_movesets:
            moveset.hp_actions = [x for x in moveset.hp_actions if x.timed or x.repeating]
            if moveset.hp_actions:
                skillset.enemy_remaining_movesets.append(moveset)

    return skillset


def collapse_repeating_groups(groups: List[TimedSkillGroup]) -> List[TimedSkillGroup]:
    """For repeating movesets, collapse consecutive repeats."""
    if len(groups) <= 1:
        # No work we can do here
        return groups

    cur_item = groups[0]
    new_groups = [cur_item]
    for idx in range(1, len(groups)):
        next_item = groups[idx]
        if cur_item.skills == next_item.skills and cur_item.turn != next_item.turn:
            cur_item.end_turn = next_item.turn
            cur_item.execute_above_hp = cur_item.execute_above_hp or next_item.execute_above_hp
        else:
            new_groups.append(next_item)
            cur_item = next_item
    return new_groups


def clean_skillset(moveset: Moveset, hp_actions: List[HpActions]):
    """Perform a variety of cleanups and compute the final skillset."""

    def extract_and_clear_action(skills, action_type):
        """Clears an action by type from the skill list and returns any matches."""
        actions = [s for s in skills if isinstance(s.behavior, action_type)]
        skills[:] = [s for s in skills if not isinstance(s.behavior, action_type)]
        return actions

    # Extract special hoisted actions if present, clearing them in their home sets.
    status_skills = []
    dispel_skills = []
    for hp_action in hp_actions:
        dispels_found = 0
        for t in hp_action.timed:
            dispels_found += len(extract_and_clear_action(list(t.skills), ESDispel))
        for r in hp_action.repeating:
            dispels_found += len(extract_and_clear_action(list(r.skills), ESDispel))

        for t in hp_action.timed:
            status_skills.extend(extract_and_clear_action(t.skills, ESAttackUpStatus))
            # Check if there are a substantial number of dispels, only then will we clear them.
            if dispels_found > 5:
                dispel_skills.extend(extract_and_clear_action(t.skills, ESDispel))

        for r in hp_action.repeating:
            status_skills.extend(extract_and_clear_action(r.skills, ESAttackUpStatus))
            # Check if there are a substantial number of dispels, only then will we clear them.
            if dispels_found > 5:
                dispel_skills.extend(extract_and_clear_action(r.skills, ESDispel))

    # If we found anything, set them. These are lists but they should just contain the
    # same item repeatedly, unless a monster has multiple status-enrage/dispels?
    if status_skills:
        moveset.status_action = status_skills[0]
    if dispel_skills:
        moveset.dispel_action = dispel_skills[0]

    # Collapse unnecessary outputs
    for hp_action in hp_actions:
        hp_action.timed = collapse_repeating_groups(hp_action.timed)
        hp_action.repeating = collapse_repeating_groups(hp_action.repeating)

    # Only add non-empty hp checkpoints
    for hp_action in hp_actions:
        # Make sure repeating groups have at least one skill in them.
        hp_action.timed = [x for x in hp_action.timed if x.skills]
        hp_action.repeating = [x for x in hp_action.repeating if x.skills]
        if hp_action.timed or hp_action.repeating:
            moveset.hp_actions.append(hp_action)

    # Clean up optional timed skills that bleed over into repeating skills.
    for hp_action in moveset.hp_actions:
        if len(hp_action.timed) != 1:
            continue
        timed = hp_action.timed[0]
        if len(timed.skills) > 1 and len(hp_action.repeating) == 1:
            timed.skills = [x for x in timed.skills if x not in hp_action.repeating[0].skills]

    # Clean up unnecessary 'execute above' from the final hp threshold.
    if len(moveset.hp_actions):
        for timed_action in moveset.hp_actions[-1].timed:
            timed_action.execute_above_hp = None


def extract_levels(enemy_behavior: List[ESInstance]):
    """Scan through the behavior list and compile a list of level values, always including 1."""
    levels = set()
    levels.add(1)
    for b in enemy_behavior:
        if isinstance(b.behavior, ESBranchLevel):
            # Always extract the target level, the level above, and (if possible) the level below.
            # These will be deduped later.
            levels.add(b.behavior.branch_value)
            levels.add(b.behavior.branch_value + 1)
            if b.behavior.branch_value > 1:
                levels.add(b.behavior.branch_value - 1)

        elif hasattr(b.behavior, 'level'):
            levels.add(b.behavior.level)
    return levels


def find_action_by_hp(hp: int, actions: List[HpActions]) -> Optional[HpActions]:
    return {a.hp: a for a in actions}.get(hp)
