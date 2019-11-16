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


def ordinal(n):
    return "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])


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
            return 'Change own attribute to random one of ' + ', '.join(map(str, attributes))

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
            ', '.join([ordinal(x) for x in positions]), position_type, ', '.join(map(str, attributes)))

    @staticmethod
    def board_change(attributes):
        return 'Change all orbs to {:s}'.format(', '.join(map(str, attributes)))

    @staticmethod
    def random_orb_spawn(count, attributes):
        if count == 42:
            return Describe.board_change(attributes)
        else:
            return 'Spawn random {:d} {:s} orbs'.format(count, ', '.join(map(str, attributes)))

    @staticmethod
    def fixed_orb_spawn(attributes):
        return 'Spawn {:s} orbs in the specified positions'.format(', '.join(map(str, attributes)))

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
            return 'Lock all {:s} orbs'.format(', '.join(map(str, attributes)))
        else:
            return 'Lock {:d} random {:s} orbs'.format(count, ', '.join(map(str, attributes)))

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
        return 'Unable to match {:s} orbs for {:d} turns'.format(', '.join(map(str, attributes)), turns)

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

    @staticmethod
    def branch(condition, compare, value, round):
        return 'Branch on {} {} {}, target rnd {}'.format(condition, compare, value, round)
