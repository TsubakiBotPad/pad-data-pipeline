from enum import Enum

ATTRIBUTE_MAP = {
    # TODO: tieout
    -9: 'locked Bomb',
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


def attributes_to_str(attributes):
    return ', '.join([ATTRIBUTE_MAP[x] for x in attributes])


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


def typing_to_str(types):
    return ', '.join([TYPING_MAP[x] for x in types])


class TargetType(Enum):
    random = 0
    self_leader = 1
    both_leader = 2
    friend_leader = 3
    subs = 4
    attributes = 5
    types = 6


TARGET_NAMES = {
    TargetType.random: 'random cards',
    TargetType.self_leader: 'player leader',
    TargetType.both_leader: 'both leaders',
    TargetType.friend_leader: 'friend leader',
    TargetType.subs: 'random subs',
    TargetType.attributes: 'attributes',
    TargetType.types: 'types',
}


def targets_to_str(targets):
    return ' and '.join([TARGET_NAMES[x] for x in targets])


def ordinal(n):
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(-1 if 10 < n < 19 else n % 10, 'th')


def pluralize(noun, number, irregular_plural=None):
    if number not in (1, '1'):
        noun = irregular_plural or noun + 's'  # Removes possibility to use '' as irregular_plural
    return noun


def pluralize2(noun, number, irregular_plural=None):
    if number not in (1, '1'):
        noun = irregular_plural or noun + 's'  # Removes possibility to use '' as irregular_plural
    return "{} {}".format(number, noun)


def minmax(nmin, nmax):
    if None in [nmin, nmax] or nmin == nmax:
        return str(int(nmin or nmax))
    else:
        return "{}~{}".format(int(nmin), int(nmax))


class Describe:
    @staticmethod
    def not_set():
        return 'No description set'

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
        output = 'Deal {:s}% damage'. \
            format(minmax(int(min_hit) * int(mult), int(max_hit) * int(mult)))
        if min_hit and max_hit != 1:
            output += ' ({:s}, {:d}% each)'. \
                format(pluralize2("hit", minmax(min_hit, max_hit)), mult)
        return output

    @staticmethod
    def skip():
        return 'Do nothing'

    @staticmethod
    def bind(min_turns, max_turns, target_count=None, target_type='cards'):
        if target_count:
            output = 'Bind {:d} {:s} '.format(target_count, target_type)
        else:
            output = 'Bind {:s} '.format(target_type)
        output += 'for '
        output += pluralize2('turn', minmax(min_turns, max_turns))
        return output

    @staticmethod
    def orb_change(orb_from, orb_to, random_count=None, exclude_hearts=None):
        if not isinstance(orb_from, list):
            orb_from = [orb_from]
        if not isinstance(orb_to, list):
            orb_to = [orb_to]

        output = 'Change '
        output += attributes_to_str(orb_from)
        if random_count is not None:
            output += ' {}'.format(random_count)
        output += ' to '
        output += attributes_to_str(orb_to)
        if exclude_hearts:
            output += ' (excluding hearts)'

        return output

    @staticmethod
    def blind():
        return 'Blind all orbs on the board'

    @staticmethod
    def blind_sticky_random(turns, min_count, max_count):
        if min_count == 42:
            return 'Blind all orbs for {:s}'.format(pluralize2('turn', turns))
        else:
            return 'Blind random {:s} orbs for {:s}' \
                .format(minmax(min_count, max_count), pluralize2('turn', turns))

    @staticmethod
    def blind_sticky_fixed(turns):
        return 'Blind orbs in specific positions for {:s}'.format(pluralize2('turn', turns))

    @staticmethod
    def dispel_buffs():
        return 'Voids player buff effects'

    @staticmethod
    def recover(min_amount, max_amount, target='enemy'):
        return '{:s} recover {:s}% HP'.format(target, minmax(min_amount, max_amount)).capitalize()

    @staticmethod
    def enrage(mult, turns):
        output = ['Increase damage to {:d}%'.format(mult)]
        if turns == 0:
            output.append('attack')
        else:
            output.append('{:s}'.format(pluralize2('turn', turns)))
        return ' for the next '.join(output)

    @staticmethod
    def status_shield(turns):
        return 'Voids status ailments for {:s}'.format(pluralize2('turn', turns))

    @staticmethod
    def debuff(d_type, amount, unit, turns):
        d_type = d_type or ''
        amount = amount or 0
        unit = unit or '?'
        turns = turns or 0
        return '{:s} {:.0f}{:s} for {:s}' \
            .format(d_type, amount, unit, pluralize2('turn', turns)).capitalize()

    @staticmethod
    def end_battle():
        return 'Reduce self HP to 0'

    @staticmethod
    def change_attribute(attributes):
        if len(attributes) == 1:
            return 'Change own attribute to {}'.format(ATTRIBUTE_MAP[attributes[0]])
        else:
            return 'Change own attribute to random one of ' + attributes_to_str(attributes)

    @staticmethod
    def gravity(percent):
        return 'Player -{:d}% HP'.format(percent)

    @staticmethod
    def absorb(source, min_turns, max_turns=None):
        if max_turns is None or min_turns == max_turns:
            return 'Absorb {:s} damage for {:s}' \
                .format(source, pluralize2('turn', min_turns))
        else:
            return 'Absorb {:s} damage for {:s}' \
                .format(source, pluralize2("turn", minmax(min_turns, max_turns)))

    @staticmethod
    def skyfall(attributes, chance, min_turns, max_turns=None, locked=False):
        lock = 'Locked ' if locked else ''
        orbs = attributes_to_str(attributes)
        # TODO: tieout
        if lock and orbs == 'Random':
            orbs = 'random'
        return '{:s}{:s} skyfall +{:d}% for {:s}' \
            .format(lock, orbs, chance, pluralize2('turn', minmax(min_turns, max_turns)))

    @staticmethod
    def void(threshold, turns):
        return 'Void damage >= {:d} for {:s}'.format(threshold, pluralize2('turn', turns))

    @staticmethod
    def damage_reduction(source, percent=None, turns=None):
        if percent is None:
            return 'Immune to damage from {:s} for {:s}'.format(source, pluralize2('turn', turns))
        else:
            if turns:
                return 'Reduce damage from {:s} by {:d}% for {:s}' \
                    .format(source, percent, pluralize2('turn', turns))
            else:
                return 'Reduce damage from {:s} by {:d}%'.format(source, percent)

    @staticmethod
    def invuln_off():
        return 'Remove damage immunity effect'

    @staticmethod
    def resolve(percent):
        return 'Survive attacks with 1 HP when HP > {:d}%'.format(percent)

    @staticmethod
    def leadswap(turns):
        return 'Leader changes to random sub for {:s}'.format(pluralize2('turn', turns))

    @staticmethod
    def row_col_spawn(position_type, positions, attributes):
        return 'Change {:s} {:s} to {:s} orbs'.format(
            ', '.join([ordinal(x) for x in positions]), position_type, attributes_to_str(attributes))

    @staticmethod
    def row_col_multi(desc_arr):
        return 'Change ' + ', '.join(desc_arr)

    @staticmethod
    def board_change(attributes):
        return 'Change all orbs to {:s}'.format(attributes_to_str(attributes))

    @staticmethod
    def random_orb_spawn(count, attributes):
        if count == 42:
            return Describe.board_change(attributes)
        else:
            return 'Spawn random {:d} {:s} {:s}' \
                .format(count, attributes_to_str(attributes), pluralize('orb', count))

    @staticmethod
    def fixed_orb_spawn(attributes):
        return 'Spawn {:s} orbs in the specified positions'.format(attributes_to_str(attributes))

    @staticmethod
    def skill_delay(min_turns, max_turns):
        return 'Delay active skills by {:s}' \
            .format(pluralize2('turn', minmax(min_turns, max_turns)))

    @staticmethod
    def orb_lock(count, attributes):
        if count == 42:
            return 'Lock all {:s} orbs'.format(attributes_to_str(attributes))
        else:
            return 'Lock {:d} random {:s} {:s}'.format(count, attributes_to_str(attributes), pluralize('orb', count))

    @staticmethod
    def orb_seal(turns, position_type, positions):
        return 'Seal {:s} {:s} for {:s}' \
            .format(', '.join([ordinal(x) for x in positions]), position_type, pluralize2('turn', turns))

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
        return '{:s} cloud appear for {:s} at {:s}' \
            .format(shape, pluralize2('turn', turns), ', '.join(pos))

    @staticmethod
    def fixed_start():
        return 'Fix orb movement starting point to random position on the board'

    @staticmethod
    def turn_change(turn_counter, threshold=None):
        if threshold:
            return 'Enemy turn counter change to {:d} when HP <= {:d}%'.format(turn_counter, threshold)
        else:
            return 'Enemy turn counter change to {:d}'.format(turn_counter)

    @staticmethod
    def attribute_block(turns, attributes):
        return 'Unable to match {:s} orbs for {:s}' \
            .format(attributes_to_str(attributes), pluralize2('turn', turns))

    @staticmethod
    def spinners(turns, speed, random_num=None):
        if random_num is None:
            return 'Specific orbs change every {:.1f}s for {:s}' \
                .format(speed / 100, pluralize2('turn', turns))
        else:
            return 'Random {:d} orbs change every {:.1f}s for {:s}' \
                .format(random_num, speed / 100, pluralize2('turn', turns))

    @staticmethod
    def max_hp_change(turns, max_hp, percent):
        if percent:
            return 'Change player HP to {:d}% for {:s}'.format(max_hp, pluralize2('turn', turns))
        else:
            return 'Change player HP to {:d} for {:s}'.format(max_hp, pluralize2('turn', turns))

    @staticmethod
    def fixed_target(turns):
        return 'Forces attacks to hit this enemy for {:s}'.format(pluralize2('turn', turns))

    @staticmethod
    def death_cry(message):
        if message is None:
            return 'Show death effect'
        else:
            return 'Show message: {:s}'.format(message)

    @staticmethod
    def attribute_exists(atts):
        return 'when {:s} orbs are on the board'.format(attributes_to_str(atts))

    @staticmethod
    def countdown(counter):
        return 'Display \'{:d}\' and skip turn'.format(counter)

    @staticmethod
    def gacha_fever(attribute, orb_req):
        return 'Fever Mode: clear {:d} {:s} {:s}'.format(orb_req, ATTRIBUTE_MAP[attribute], pluralize('orb', orb_req))

    @staticmethod
    def lead_alter(turns, target):
        return 'Change leader to [{:d}] for {:s}'.format(target, pluralize2('turn', turns))

    @staticmethod
    def force_7x6(turns):
        return 'Change board size to 7x6 for {:s}'.format(pluralize2('turn', turns))

    @staticmethod
    def no_skyfall(turns):
        return 'No skyfall for {:s}'.format(pluralize2('turn', turns))

    @staticmethod
    def branch(condition, compare, value, rnd):
        return 'Branch on {} {} {}, target rnd {}'.format(condition, compare, value, rnd)
