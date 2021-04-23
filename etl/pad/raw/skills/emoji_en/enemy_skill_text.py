from pad.raw.skills.emoji_en.skill_common import *

import logging

human_fix_logger = logging.getLogger('human_fix')
# This is 1/4 dictionaries that need to be replaced. 3 and 4 are in EmojiBaseTextConverter
emoji_dict = {
    'recover': "{recover_health}",
    'roulette': "{roulette}",
    'unknown': "{unknown_type}",
    'defense': "{defense_status}",
    'defense25': "{defense25_status}",
    'defense50': "{defense50_status}",
    'defense75': "{defense75_status}",
    'defense80': "{defense80_status}",
    'defense90': "{defense90_status}",
    'defense95': "{defense95_status}",
    'defense99': "{defense99_status}",
    'combo_absorb': "{combo_absorb_status}️",
    'absorb': "{absorb_status}",
    'damage_absorb': "{damage_absorb_status}",
    'void': "{damage_void_status}",
    'status_shield': "{status_shield_status}",
    'resolve': "{resolve_status}",
    'rcv_buff': "{recover_buff_status}️",
    'atk_debuff': "{attack_debuff_status}",
    'rcv_debuff': "{recover_debuff_status}",
    'movetime_buff': "{movetime_buff_status}",
    'movetime_debuff': "{movetime_debuff_status}",
    'dispel': "{dispel_status}",
    'swap': "{leader_swap_status}",
    'skill_delay': '{skill_delay}',
    'locked': '{lock_orbs}',
    'tape': '{tape_status}',
    'starting_position': '{fixed_start}',
    'cloud': '{cloud_status}',
    'gravity': '{gravity}',
    'invincible': '{invincible_status}',
    'invincible_off': '{invincible_off_status}',
    'force_target': '{force_target_status}',
    'leader_alter': '{leader_alter_status}',
    'board_size': '{board_size_status}',
    'super_resolve': '{super_resolve_status}',
    'turn_change': '{turn_change}',
    'enrage': '{enrage_status}',
    'skill_bind': '{skill_bind}',
    'do_nothing': '{do_nothing}',
    'awoken_bind': '{awoken_bind}',
    'no_skyfall': '{no_skyfall_status}',
    'bind': "{bind}",
    'skyfall': '{skyfall_status}',
    'blind': "{blind}",
    'super_blind': "{super_blind}",
    'to': "{to}",
    'attack': '{attack}',
    'multi_attack': '{multi_attack}',
    'self': '{target_self}',
    'health': '{health}',
    'combo': '{combo_orb}'
}

# This is unused because in discord the skyfall orbs are really hard to see, if I can make a better appearing symbol I
# can bring this back
SkyfallAttributes = {
    -9: '{locked_bomb_skyfall}',
    -1: '{random_type_skyfall}',
    None: '{fire_skyfall}',
    0: '{fire_skyfall}',
    1: '{water_skyfall}',
    2: '{wood_skyfall}',
    3: '{light_skyfall}',
    4: '{dark_skyfall}',
    5: '{heal_skyfall}',
    6: '{jammer_skyfall}',
    7: '{poison_skyfall}',
    8: '{mortal_poison_skyfall}',
    9: '{bomb_skyfall}',
}

# This is used (2/4)
UnmatchableAttributes = {
    -1: '{no_match_random}',
    None: "{no_match_fire}",
    0: "{no_match_fire}",
    1: "{no_match_water}",
    2: "{no_match_wood}",
    4: "{no_match_dark}",
    3: "{no_match_light}",
    5: "{no_match_heal}",
    6: '{no_match_jammer}',
    7: '{no_match_poison}',
    8: '{no_match_mortal_poison}',
    9: '{no_match_bomb}',
}
# This is unused, see SkyfallAttributes
LockedSkyfallAttributes = {
    -9: '{locked_bomb_skyfall}',
    -1: '{locked_random_skyfall}',
    None: '{locked_fire_skyfall}',
    0: '{locked_fire_skyfall}',
    1: '{locked_water_skyfall}',
    2: '{locked_wood_skyfall}',
    3: '{locked_light_skyfall}',
    4: '{locked_dark_skyfall}',
    5: '{locked_heal_skyfall}',
    6: '{locked_jammer_skyfall}',
    7: '{locked_poison_skyfall}',
    8: '{locked_mortal_poison_skyfall}',
    9: '{locked_bomb_skyfall}',
}

# This is unused, see SkyfallAttributes
AbsorbAttributes = {
    -9: '{locked_bomb_absorb}',
    -1: '{random_absorb}',
    None: '{fire_absorb}',
    0: '{fire_absorb}',
    1: '{water_absorb}',
    2: '{wood_absorb}',
    3: '{light_absorb}',
    4: '{dark_absorb}',
    5: '{heal_absorb}',
    6: '{jammer_absorb}',
    7: '{poison_absorb}',
    8: '{mortal_poison_absorb}',
    9: '{bomb_absorb}',
}

# This is unused, not enough emoji slots.
LockedAttributes = {
    -9: '{locked_bomb}',
    -1: '{locked_random}',
    None: '{locked_fire}',
    0: '{locked_fire}',
    1: '{locked_water}',
    2: '{{locked_wood}',
    3: '{locked_light}',
    4: '{locked_dark}',
    5: '{locked_heal}',
    6: '{locked_jammer}',
    7: '{locked_poison}',
    8: '{locked_mortal_poison}',
    9: '{locked_bomb}',
}

TARGET_NAMES = {
    TargetType.unset: '<targets unset>',

    # Specific Subs
    TargetType.random: 'random',
    TargetType.self_leader: 'player leader',
    TargetType.both_leader: 'both leaders',
    TargetType.friend_leader: 'friend leader',
    TargetType.subs: 'random sub',
    TargetType.attrs: 'attributes',
    TargetType.types: 'type',
    TargetType.card: '',

    # Specific Players/Enemies (For Recovery)
    TargetType.player: 'player',
    TargetType.enemy: 'enemy',
    TargetType.enemy_ally: 'enemy ally',

    # Full Team Aspect
    TargetType.awokens: '{awoken_skill_bind}',
    TargetType.actives: '{active_skill_bind}',
}


def targets_to_str(targets):
    return targets if isinstance(targets, str) \
        else ' and '.join([TARGET_NAMES[x] for x in targets])


ORB_SHAPES = {
    OrbShape.l_shape: 'L shape',
    OrbShape.cross: 'cross',
    OrbShape.column: 'column',
    OrbShape.row: 'row',
}

STATUSES = {
    Status.movetime: '{movetime_debuff_status}',
    Status.atk: '{attack_debuff_status}',
    Status.hp: '{set_hp_status}',
    Status.rcv: '{recover_debuff_status}',
}

UNITS = {
    Unit.unknown: '?',
    Unit.seconds: 's',
    Unit.percent: '%',
    Unit.none: '',
}

SOURCE_FUNCS = {
    Source.all_sources: lambda x: 'all sources',
    Source.types: EmojiBaseTextConverter().typing_to_str,
    Source.attrs: EmojiBaseTextConverter().attributes_to_str,
}


def ordinal(n):
    return str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(-1 if 10 < n < 19 else n % 10, 'th')


class EnEmojiESTextConverter(EmojiBaseTextConverter):
    def not_set(self):
        return '(N/A)'

    def default_attack(self):
        return '({})'.format(emoji_dict['attack'])

    # don't really care right now
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
        # have to process this in the bot in order to get full damage numbers
        return '(Attack:{}-{}, {})'.format(min_hit, max_hit, mult)
        """if mult is None:
            return None
        output = 'Deal {:s}% damage'. \
            format(minmax(int(min_hit) * int(mult), int(max_hit) * int(mult)))
        if min_hit and max_hit != 1:
            output += ' ({:s}, {:,}% each)'. \
                format(pluralize2("hit", minmax(min_hit, max_hit)), mult)
        return output"""

    def skip(self):
        return '({})'.format(emoji_dict['do_nothing'])

    def bind(self, min_turns, max_turns, target_count=None, target_types=TargetType.card, source: Source = None):
        if isinstance(target_types, TargetType):
            target_types = [target_types]
        elif source is not None:
            target_types = SOURCE_FUNCS[source]([target_types]) + ' cards'
        targets = targets_to_str(target_types)
        output = '({} {} '.format(emoji_dict['bind'], pluralize2(targets, target_count))
        output += 'for ' + minmax(min_turns, max_turns) + ')'
        return output

    def orb_change(self, orb_from, orb_to, random_count=None, random_type_count=None, exclude_hearts=False):
        if not isinstance(orb_from, list):
            orb_from = [orb_from]
        orb_from = self.attributes_to_emoji(orb_from)

        if not isinstance(orb_to, list):
            orb_to = [orb_to]
        orb_to = self.attributes_to_emoji(orb_to)

        output = ''
        if random_count is not None:
            orbs_text = pluralize('orb', random_count)
            if orb_from == 'Random':
                output += '({} random'.format(random_count)
            else:
                output += '({} random {}'.format(random_count, orb_from)
            if exclude_hearts:
                output += ' [ignore {}]'.format(self._ATTRS[5])
        elif random_type_count is not None:
            types_text = pluralize('type', random_type_count)
            output += '({} random orb {}'.format(random_type_count, types_text)
        else:
            if 'Random' in orb_from:
                output += '(1 Att'
            else:
                output += '({}'.format(orb_from)
        output += emoji_dict['to']
        if 'Random' in orb_to:
            output += 'random att)'
        else:
            output += '{})'.format(orb_to)
        return output

    def blind(self):
        return '({})'.format(emoji_dict['blind'])

    def blind_sticky_random(self, turns, min_count, max_count):
        if min_count == 42:
            return '({} for {})'.format(emoji_dict['super_blind'], turns)
        else:
            return '({} {} for {})' \
                .format(minmax(min_count, max_count), emoji_dict['super_blind'], turns)

    def blind_sticky_fixed(self, turns):
        return '({} for {} [Fixed Position])'.format(emoji_dict['super_blind'], turns)

    def blind_sticky_skyfall(self, turns, chance, b_turns):
        return '([{} for {}] +{}%{} for {})'.format(emoji_dict['super_blind'], b_turns, chance,
                                                    emoji_dict['skyfall'], turns)

    def dispel_buffs(self):
        return '(Dispel)'

    def recover(self, min_amount, max_amount, target_type, player_threshold=None):
        target = targets_to_str([target_type])
        if player_threshold and player_threshold != 100:
            return "({}{}%HP{}{})".format(emoji_dict['recover'], minmax(min_amount, max_amount), emoji_dict['to'],
                                          capitalize_first(target))
        else:
            return "({}{}%HP{}{})".format(emoji_dict['recover'], minmax(min_amount, max_amount), emoji_dict['to'],
                                          capitalize_first(target))

    def enrage(self, mult, turns):
        turns = turns or 1
        return "({}{}% for {})".format(emoji_dict['enrage'], mult, turns)

    def status_shield(self, turns):
        return "({} for {})".format(emoji_dict['status_shield'], turns)

    def debuff(self, d_type, amount, unit, turns):
        amount = amount or 0
        if amount % 1 != 0:
            human_fix_logger.error('Amount {} will be truncated. Change debuff'.format(amount))
        unit = UNITS[unit]
        turns = turns or 0
        type_text = capitalize_first(STATUSES[d_type] or '')
        if d_type == Status.movetime:
            if amount > 100:
                type_text = emoji_dict['movetime_buff']
        elif d_type == Status.rcv:
            if amount > 100:
                type_text = emoji_dict['rcv_buff']
        return '({:s} {:.0f}{:s} for {})'.format(type_text, amount, unit, turns)

    def end_battle(self):
        return '(End Battle)'

    def change_attribute(self, attributes):
        if len(attributes) == 1:
            return "({}{}{})".format(emoji_dict['self'], emoji_dict['to'], self._ATTRS[attributes[0]])
        else:
            return "({}{} random {})".format(emoji_dict['self'], emoji_dict['to'], self.attributes_to_emoji(attributes))
        # return 'Change own attribute to random one of ' + self.attributes_to_str(attributes, 'or')

    def gravity(self, percent):
        return "(-{}%{})".format(percent, emoji_dict['gravity'])

    def absorb(self, abs_type: Absorb, condition, min_turns, max_turns=None):
        if abs_type == Absorb.attr:
            source = self.attributes_to_emoji(condition)
            return "({}:{} for {})".format(emoji_dict['absorb'], source, minmax(min_turns, max_turns))
        elif abs_type == Absorb.combo:
            return "({}{} for {})".format(emoji_dict['combo_absorb'], condition, minmax(min_turns, max_turns))
        elif abs_type == Absorb.damage:
            return "({}{} for {})".format(emoji_dict['damage_absorb'], f'{condition:,}', minmax(min_turns, max_turns))
        else:
            raise ValueError("unknown absorb type: {}".format(abs_type))

    def skyfall(self, attributes, chance, min_turns, max_turns=None, locked=False):
        lock = 'Locked ' if locked else ''
        orbs = self.attributes_to_str(attributes)
        # TODO: tieout
        if lock and orbs == 'Random':
            orbs = orbs.lower()
        if not locked:
            return "([{}:{}]+{}% for {})".format(emoji_dict['skyfall'], self.attributes_to_emoji(attributes), chance,
                                                 minmax(min_turns, max_turns))
        if locked:
            return "([{}{}:{}]+{}% for {})".format(emoji_dict['locked'], emoji_dict['skyfall'],
                                                   self.attributes_to_emoji(attributes), chance,
                                                   minmax(min_turns, max_turns))

    def void(self, threshold, turns):
        return "({}{} for {})".format(emoji_dict['void'], f'{threshold:,}', turns)

    def damage_reduction(self, source_type: Source, source=None, percent=None, turns=None):
        source = (SOURCE_FUNCS[source_type])(source)
        if percent is None:
            return '({})'.format(emoji_dict['invincible'])
        else:
            if turns:
                return "({}{} for {})".format(emoji_dict['defense'], percent, turns)
            else:
                return '({}-{}%)'.format(source, percent)

    def invuln_off(self):
        return '({})'.format(emoji_dict['invincible_off'])

    def resolve(self, percent):
        return "({}{}%)".format(emoji_dict['resolve'], percent)

    def superresolve(self, percent, remaining):
        return "({}{})".format(emoji_dict['super_resolve'], percent)

    def leadswap(self, turns):
        return "({} for {})".format(emoji_dict['swap'], turns)

    def row_col_spawn(self, position_type, positions, attributes):
        return '([{:s}: {:s}]{}{:s})'.format(
            pluralize(ORB_SHAPES[position_type], len(positions)),
            self.concat_list_and([ordinal(x) for x in positions]),
            emoji_dict['to'],
            self.attributes_to_emoji(attributes))

    def row_col_multi(self, desc_arr):
        return ''.join(desc_arr)

    def board_change(self, attributes):
        return '(All{}{})'.format(emoji_dict['to'], self.attributes_to_emoji(attributes))

    def random_orb_spawn(self, count, attributes):
        if count == 42:
            return self.board_change(attributes)
        else:
            return '(Any {}{}{})'.format(count, emoji_dict['to'], self.attributes_to_emoji(attributes))

    def fixed_orb_spawn(self, attributes):
        return '(Specific Positions{}{})'.format(emoji_dict['to'], self.attributes_to_emoji(attributes))

    def skill_delay(self, min_turns, max_turns):
        return "({}-[{}])".format(emoji_dict['skill_delay'], minmax(min_turns, max_turns))

    def orb_lock(self, count, attributes):
        if count == 42 and attributes == self.ATTRS_EXCEPT_BOMBS:
            return '({}:All)'.format(emoji_dict['locked'])
        elif count == 42:
            return '({}:{})'.format(emoji_dict['locked'], self.attributes_to_emoji(attributes))
        elif attributes == self.ATTRS_EXCEPT_BOMBS:
            return '({}:{} Any)'.format(emoji_dict['locked'], count)
        else:
            return '({}:{} {})'.format(emoji_dict['locked'], count, self.attributes_to_emoji(attributes))

    def orb_seal(self, turns, position_type, positions):
        return '({}[{:s}:{:s}] for {})' \
            .format(emoji_dict['tape'],
                    pluralize(ORB_SHAPES[position_type], len(positions)),
                    self.concat_list_and([ordinal(x) for x in positions]),
                    turns)

    def cloud(self, turns, width, height, x, y):
        if x is None and y is None:
            return "({}{}x{} for {})".format(emoji_dict['cloud'], width, height, turns)
        row = x or 'Random'
        col = y or 'Random'
        return "({}{}x{} at [{},{}] for {})".format(emoji_dict['cloud'], width, height, row, col, turns)

    def fixed_start(self):
        return '({})'.format(emoji_dict['starting_position'])

    def turn_change(self, turn_counter, threshold=None):
        if threshold:
            return '(Turn{}{})'.format(emoji_dict['to'], turn_counter)
        else:
            return '(Turn{}{})'.format(emoji_dict['to'], turn_counter)

    def attribute_block(self, turns, attributes):
        return '({} for {})'.format(self.attributes_to_emoji(attributes, UnmatchableAttributes), turns)

    def spinners(self, turns, speed, random_num=None):
        if random_num is None:
            return '(Specific {}{} for {})'.format(emoji_dict['roulette'], speed, turns)
        else:
            return "({}{}Random {} for {})".format(emoji_dict['roulette'], random_num, speed, turns)

    def max_hp_change(self, turns, max_hp, percent):
        if percent:
            return "({}= {}% for {})".format(emoji_dict['health'], max_hp, turns)
        else:
            return "({}= {} for {})".format(emoji_dict['health'], max_hp, turns)

    def fixed_target(self, turns):
        return "({} for {})".format(emoji_dict['force_target'], turns)

    def death_cry(self, message):
        return '(Waste your turn dying)'

    def attribute_exists(self, atts):
        return 'when {:s} orbs are on the board'.format(self.attributes_to_str(atts, 'or'))

    def countdown(self, counter):
        return 'Display \'{:d}\' and skip turn'.format(counter)

    def use_skillset(self, skill_set_id):
        return 'Use skill set #{}'.format(skill_set_id)

    def gacha_fever(self, attribute, orb_req):
        return 'Fever Mode: clear {:d} {:s} {:s}'.format(orb_req, self._ATTRS[attribute], pluralize('orb', orb_req))

    def lead_alter(self, turns, target):
        return "({}[{}] for {})".format(emoji_dict['leader_alter'], target, turns)

    def force_board_size(self, turns: int, size_param: int):
        size = {1: '7x6', 2: '5x4', 3: '6x5'}.get(size_param, 'unknown')
        return "({}{} for {})".format(size, emoji_dict['board_size'], turns)

    def no_skyfall(self, turns):
        return '({} for {})'.format(emoji_dict['no_skyfall'], turns)

    def combo_skyfall(self, turns, chance):
        return '({}{}{}% for {})'.format(emoji_dict['skyfall'], emoji_dict['combo'], chance, turns)

    def debuff_atk(self, turns, amount):
        return "({}{}% for {})".format(emoji_dict['atk_debuff'], amount, turns)

    def branch(self, condition, compare, value, rnd):
        return 'Branch on {} {} {}, target rnd {}'.format(condition, compare, value, rnd)

    def join_skill_descs(self, descs):
        return ' + '.join(descs)


__all__ = ['EnEmojiESTextConverter']
