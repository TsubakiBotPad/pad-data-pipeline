import logging

from pad.raw.skills.en.skill_common import EnBaseTextConverter, capitalize_first, pluralize2, minmax, pluralize, ordinal
from pad.raw.skills.skill_common import TargetType, Source, Unit, Status, OrbShape, Absorb

human_fix_logger = logging.getLogger('human_fix')

TARGET_NAMES = {
    TargetType.unset: '<targets unset>',

    # Specific Subs
    TargetType.random: 'random card',
    TargetType.self_leader: 'player leader',
    TargetType.both_leader: 'both leaders',
    TargetType.friend_leader: 'friend leader',
    TargetType.subs: 'random sub',
    TargetType.attrs: 'attributes',
    TargetType.types: 'type',
    TargetType.card: 'card',
    TargetType.all: 'all cards',

    # Specific Players/Enemies (For Recovery)
    TargetType.player: 'player',
    TargetType.enemy: 'enemy',
    TargetType.enemy_ally: 'enemy ally',

    # Full Team Aspect
    TargetType.awokens: 'awoken skills',
    TargetType.actives: 'active skills',
}


def targets_to_str(targets):
    return targets if isinstance(targets, str) \
        else ' and '.join([TARGET_NAMES[x] for x in targets])


def possessive(s):
    if s[-1] == 's':
        return s+"'"
    return s+"'s"


ORB_SHAPES = {
    OrbShape.l_shape: 'L shape',
    OrbShape.cross: 'cross',
    OrbShape.column: 'column',
    OrbShape.row: 'row',
}

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
    Source.types: EnBaseTextConverter().typing_to_str,
    Source.attrs: EnBaseTextConverter().attributes_to_str,
}


class EnESTextConverter(EnBaseTextConverter):
    def not_set(self):
        return 'No description set'

    def default_attack(self):
        return 'Default Attack'

    def condition(self, chance, hp=None, one_time=False):
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
        return capitalize_first(' '.join(output)) if len(output) > 0 else None

    def attack(self, mult, min_hit=1, max_hit=1):
        if mult is None:
            return None
        output = 'Deal {:s}% damage'. \
            format(minmax(int(min_hit) * int(mult), int(max_hit) * int(mult)))
        if min_hit and max_hit != 1:
            output += ' ({:s}, {:,}% each)'. \
                format(pluralize2("hit", minmax(min_hit, max_hit)), mult)
        return output

    def skip(self):
        return 'Do nothing'

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
            orbs_text = pluralize('orb', random_count)
            if orb_from == 'Random':
                output += '{} random {:s}'.format(random_count, orbs_text)
            else:
                output += '{} random {} {}'.format(random_count, orb_from, orbs_text)
            if exclude_hearts:
                output += ' (excluding hearts)'
        elif random_type_count is not None:
            types_text = pluralize('type', random_type_count)
            output += '{} random orb {}'.format(random_type_count, types_text)
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
        return 'Blind all orbs on the board'

    def blind_sticky_random(self, turns, min_count, max_count):
        if min_count == 42:
            return 'Blind all orbs for {:s}'.format(pluralize2('turn', turns))
        else:
            return 'Blind random {:s} orbs for {:s}' \
                .format(minmax(min_count, max_count), pluralize2('turn', turns))

    def blind_sticky_fixed(self, turns):
        return 'Blind orbs in specific positions for {:s}'.format(pluralize2('turn', turns))

    def blind_sticky_skyfall(self, turns, chance, b_turns):
        return 'For {:s}, {}% chance for skyfall orbs to be blinded for {:s}'.format(
            pluralize2('turn', turns), chance, pluralize2('turn', b_turns))

    def dispel_buffs(self):
        return 'Voids player buff effects'

    def recover(self, min_amount, max_amount, target_type, player_threshold=None):
        target = targets_to_str([target_type])
        if player_threshold and player_threshold != 100:
            return capitalize_first(
                '{:s} recover {:s} HP when below {}% HP'.format(
                    target, minmax(min_amount, max_amount, True), player_threshold))
        else:
            return capitalize_first('{:s} recover {:s} HP'.format(target, minmax(min_amount, max_amount, True)))

    def enrage(self, mult, turns):
        output = 'Increase damage to {:,}% for the next '.format(mult)
        output += pluralize2('turn', turns) if turns else 'attack'
        return output

    def status_shield(self, turns):
        return 'Voids status ailments for {:s}'.format(pluralize2('turn', turns))

    def debuff(self, d_type, amount, unit, turns):
        amount = amount or 0
        if amount % 1 != 0:
            human_fix_logger.error('Amount {} will be truncated. Change debuff'.format(amount))
        unit = UNITS[unit]
        turns = turns or 0
        type_text = capitalize_first(STATUSES[d_type] or '')
        turn_text = pluralize2('turn', turns)
        return '{:s} {:.0f}{:s} for {:s}'.format(type_text, amount, unit, turn_text)

    def end_battle(self):
        return 'Reduce self HP to 0'

    def change_attribute(self, attributes):
        if len(attributes) == 1:
            return 'Change own attribute to {}'.format(self.ATTRIBUTES[attributes[0]])
        else:
            return 'Change own attribute to random one of ' + self.attributes_to_str(attributes, 'or')

    def gravity(self, percent):
        return 'Player -{:,}% HP'.format(percent)

    def absorb(self, abs_type: Absorb, condition, min_turns, max_turns=None):
        if abs_type == Absorb.attr:
            source = self.attributes_to_str(condition)
            return 'Absorb {:s} damage for {:s}' \
                .format(source, pluralize2("turn", min_turns, max_turns))
        elif abs_type == Absorb.combo:
            source = 'combos <= {:d}'.format(condition)
        elif abs_type == Absorb.damage:
            source = 'damage >= {:,d}'.format(condition)
        else:
            raise ValueError("unknown absorb type: {}".format(abs_type))

        return 'Absorb damage when {:s} for {:s}' \
            .format(source, pluralize2("turn", min_turns, max_turns))

    def skyfall(self, attributes, chance, min_turns, max_turns=None, locked=False):
        lock = 'Locked ' if locked else ''
        orbs = self.attributes_to_str(attributes)
        # TODO: tieout
        if lock and orbs == 'Random':
            orbs = orbs.lower()
        return '{:s}{:s} skyfall +{:d}% for {:s}' \
            .format(lock, orbs, chance, pluralize2('turn', min_turns, max_turns))

    def void(self, threshold, turns):
        return 'Void damage >= {:,} for {:s}'.format(threshold, pluralize2('turn', turns))

    def damage_reduction(self, source_type: Source, source=None, percent=None, turns=None):
        source = (SOURCE_FUNCS[source_type])(source)
        if source_type != Source.all_sources:
            source += ' ' + source_type.name
        if percent is None:
            return 'Immune to damage from {:s} for {:s}' \
                .format(source, pluralize2('turn', turns))
        else:
            if turns:
                return 'Reduce damage from {:s} by {:d}% for {:s}' \
                    .format(source, percent, pluralize2('turn', turns))
            else:
                return 'Reduce damage from {:s} by {:d}%' \
                    .format(source, percent)

    def invuln_off(self):
        return 'Remove damage immunity effect'

    def resolve(self, percent):
        return 'Survive attacks with 1 HP when HP > {:d}%'.format(percent)

    def superresolve(self, percent, remaining):
        return 'Damage which would reduce HP from above {:d}% to below {:d}% is nullified'.format(percent, remaining)

    def leadswap(self, turns):
        return 'Leader changes to random sub for {:s}'.format(pluralize2('turn', turns))

    def row_col_spawn(self, position_type, positions, attributes):
        return 'Change the {:s} {:s} to {:s} orbs'.format(
            self.concat_list_and([ordinal(x) for x in positions]),
            pluralize(ORB_SHAPES[position_type], len(positions)),
            self.attributes_to_str(attributes))

    def row_col_multi(self, desc_arr):
        return 'Change ' + self.concat_list_and(map(lambda x: x[7:], desc_arr))

    def board_change(self, attributes):
        return 'Change all orbs to {:s}'.format(self.attributes_to_str(attributes))

    def random_orb_spawn(self, count, attributes):
        if count == 42:
            return self.board_change(attributes)
        else:
            return 'Spawn {:d} random {:s} {:s}'.format(
                count, self.attributes_to_str(attributes, 'and'), pluralize('orb', count))

    def fixed_orb_spawn(self, attributes):
        return 'Spawn {:s} orbs in the specified positions'.format(self.attributes_to_str(attributes))

    def skill_delay(self, min_turns, max_turns):
        return 'Delay active skills by {:s}' \
            .format(pluralize2('turn', minmax(min_turns, max_turns)))

    def orb_lock(self, count, attributes):
        if count == 42 and attributes == self.ATTRS_EXCEPT_BOMBS:
            return 'Lock all orbs'
        elif count == 42:
            return 'Lock all {:s} orbs'.format(self.attributes_to_str(attributes))
        elif attributes == self.ATTRS_EXCEPT_BOMBS:
            return 'Lock {:d} random {:s}'.format(count, pluralize('orb', count))
        else:
            return 'Lock {:d} random {:s} {:s}'.format(count, self.attributes_to_str(attributes),
                                                       pluralize('orb', count))

    def orb_seal(self, turns, position_type, positions):
        return 'Seal the {:s} {:s} for {:s}' \
            .format(self.concat_list_and([ordinal(x) for x in positions]),
                    pluralize(ORB_SHAPES[position_type], len(positions)),
                    pluralize2('turn', turns))

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
        return 'Fix orb movement starting point to random position on the board'

    def turn_change(self, turn_counter, threshold=None):
        if threshold:
            return 'Enemy turn counter change to {:d} when HP <= {:d}%'.format(turn_counter, threshold)
        else:
            return 'Enemy turn counter change to {:d}'.format(turn_counter)

    def attribute_block(self, turns, attributes):
        return 'Unable to match {:s} orbs for {:s}' \
            .format(self.attributes_to_str(attributes), pluralize2('turn', turns))

    def spinners(self, turns, speed, random_num=None):
        if random_num is None:
            return 'Specific orbs change every {:.1f}s for {:s}' \
                .format(speed / 100, pluralize2('turn', turns))
        else:
            return 'Random {:d} orbs change every {:.1f}s for {:s}' \
                .format(random_num, speed / 100, pluralize2('turn', turns))

    def max_hp_change(self, turns, max_hp, percent):
        if percent:
            return 'Change player HP to {:,}% for {:s}'.format(max_hp, pluralize2('turn', turns))
        else:
            return 'Change player HP to {:,} for {:s}'.format(max_hp, pluralize2('turn', turns))

    def fixed_target(self, turns):
        return 'Forces attacks to hit this enemy for {:s}'.format(pluralize2('turn', turns))

    def death_cry(self, message):
        if message is None:
            return 'Show death effect'
        else:
            return 'Show message: {:s}'.format(message)

    def attribute_exists(self, atts):
        return 'when {:s} orbs are on the board'.format(self.attributes_to_str(atts, 'or'))

    def countdown(self, counter):
        return 'Display \'{:d}\' and skip turn'.format(counter)

    def use_skillset(self, skill_set_id):
        return 'Use skill set #{}'.format(skill_set_id)

    def gacha_fever(self, attribute, orb_req):
        return 'Fever Mode: clear {:d} {:s} {:s}'.format(orb_req, self.ATTRIBUTES[attribute], pluralize('orb', orb_req))

    def lead_alter(self, turns, target):
        return 'Change leader to [{:d}] for {:s}'.format(target, pluralize2('turn', turns))

    def force_board_size(self, turns: int, size_param: int):
        size = {1: '7x6', 2: '5x4', 3: '6x5'}.get(size_param, 'unknown')
        return 'Change board size to {} for {:s}'.format(size, pluralize2('turn', turns))

    def no_skyfall(self, turns):
        return 'No skyfall for {:s}'.format(pluralize2('turn', turns))

    def combo_skyfall(self, turns, chance):
        return 'For {:s}, {}% chance for combo orb skyfall.'.format(pluralize2('turn', turns), chance)

    def debuff_atk(self, turns, amount):
        return 'ATK -{}% for {:s}'.format(amount, pluralize2('turn', turns))

    def target_skill_haste(self, min_turns, max_turns, target):
        return f'Haste {possessive(TARGET_NAMES[target])} skills by {pluralize2("turn", min_turns, max_turns)}'

    def target_skill_delay(self, min_turns, max_turns, target):
        return f'Delay {possessive(TARGET_NAMES[target])} skills by {pluralize2("turn", min_turns, max_turns)}'

    def branch(self, condition, compare, value, rnd):
        return 'Branch on {} {} {}, target rnd {}'.format(condition, compare, value, rnd)

    def join_skill_descs(self, descs):
        return ' + '.join(descs)
