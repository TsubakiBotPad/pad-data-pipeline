import re
import time
from typing import List

from enum import Enum


# Values here are used to compose the skill_data_list -> type_data field, which
# is a field formatted via the values in the condition enums, csv, encased
# in parens as such: (38),(41),(215)
#
# Value names/IDs come from the get_skill_condition table.
#
# If values are added/removed there, should be replicated here.
#
# This is a pretty fragile implementation; changes to skill text generation
# can easily break this. Should replace with something more robust after
# the skill parser is replaced.
#
# Other fields in skill_data_list are useful, they populate the visual
# effect for a skill. Not populating those yet.
class AsCondition(Enum):
    ETC = 999

    ENHANCED_ORBS = 2
    ENHANCED_ATTACK = 3
    REDUCE_DEFENSE = 4
    GRAVITY = 5
    ATTACK_STANCE = 7
    GUARD_STANCE = 8
    MENACE = 9
    STOP_TIME = 10
    REDUCE_DAMAGE = 11
    VOID_DAMAGE = 12
    SINGLE_TARGET_ATTACK = 13
    MASSIVE_ATTACK = 14
    POISON = 15
    COUNTERATTACK = 16
    GRUDGE_STRIKE = 17
    HEAL = 18
    ORB_CONVERT = 19
    ATTACK_AND_HEAL = 20
    ENHANCED_HEAL = 21
    THE_SWITCH = 22
    ATTACK_CHANGER = 23
    ATTRIBUTE_ATTACK = 24
    DOUBLE_ORBS_CONVERT = 38
    ALL_ORBS_CONVERT = 39
    SUICIDE = 40
    RECOVER_BIND = 41
    DROP_CHANCE = 50
    FIXED_DAMAGE = 60
    LINE_ORBS_CONVERTER = 70
    EXTENDS_TIME = 80
    CHANGE_ATTRIBUTE = 100
    REDUCE_SKILL_TURN = 110
    LOCK = 120  # Deprecated!
    ORB_REFRESH = 130
    CHANGE_ENEMIES_ATTRIBUTE = 140
    ADD_COMBO = 160
    NEW_GRAVITY = 180
    HEAL_BIND_RECOVERY = 190
    AWOKEN_INVALID_RECOVERY = 215
    BIND_AWOKEN_INVALID_RECOVERY = 220
    REMOVE_LOCK = 230
    VOID_DAMAGE_ABSORBS = 240
    VOID_ATT_ABSORBS = 250
    VOID_SKYFALLS = 260
    ORB_LOCK = 270
    COMBO_ROOT = 280


class LsCondition(Enum):
    AUTO_HEAL = 1
    ENHANCED_HP = 25
    ENHANCED_ATK = 26
    ENHANCED_RCV = 27
    ENHANCED_HP_ATK = 28
    ENHANCED_HP_RCV = 29
    ENHANCED_ATK_RCV = 30
    ENHANCED_HP_ATK_RCV = 31
    REDUCE_DAMAGE = 32
    DUAL_DAMAGE_REDUCTION = 33  # deprecate this
    ADDITIONAL_ATTACK = 34
    COUNTERATTACK = 35
    RESOLVE = 36
    EXTEND_TIME = 37
    COIN = 150
    EGG = 160
    EXP = 170
    BOARD_CHANGE_7X6 = 200
    NO_SKYFALL_COMBOS = 210
    ETC = 999


def format_conditions(skill_conditions):
    sorted_cond_values = sorted([x.value for x in skill_conditions])
    return ','.join(['({})'.format(x) for x in sorted_cond_values])


def parse_as_conditions(skill_text: str) -> List[AsCondition]:
    """Takes the processor-generated active skill text and produces a list of conditions."""
    skill_text = skill_text.lower()
    results = set()

    if 'activate a random skill' in skill_text:
        results.add(AsCondition.ETC)

    if 'enhance all' in skill_text:
        results.add(AsCondition.ENHANCED_ORBS)

    for part in skill_text.split(';'):
        atk_match = re.match('(.*)x atk(.*)', part)
        # Filter out 'Deal 20x ATK Wood' and 'Poison all enemies (1x ATK)'
        if atk_match and 'deal' not in atk_match.group(1) and not atk_match.group(2).startswith(')'):
            results.add(AsCondition.ENHANCED_ATTACK)

    if "reduce enemies' defense" in skill_text:
        results.add(AsCondition.REDUCE_DEFENSE)

    if "reduce enemies' hp" in skill_text:
        results.add(AsCondition.GRAVITY)

    colors = ['fire', 'water', 'wood', 'light', 'dark']
    if any(['heal orbs to {} orbs'.format(x) in skill_text for x in colors]):
        results.add(AsCondition.ATTACK_STANCE)

    if 'to heal orbs' in skill_text:
        results.add(AsCondition.GUARD_STANCE)

    if 'delay enemies' in skill_text:
        results.add(AsCondition.MENACE)

    if 'freely move orbs' in skill_text:
        results.add(AsCondition.STOP_TIME)

    if 'reduce damage taken by 100%' in skill_text:
        results.add(AsCondition.VOID_DAMAGE)
    elif 'reduce damage taken' in skill_text:
        results.add(AsCondition.REDUCE_DAMAGE)

    if 'void all' in skill_text:
        results.add(AsCondition.VOID_DAMAGE)

    if 'poison all enemies' in skill_text:
        results.add(AsCondition.POISON)

    if 'counterattack' in skill_text:
        results.add(AsCondition.COUNTERATTACK)

    if 'depending on hp level' in skill_text:
        results.add(AsCondition.GRUDGE_STRIKE)

    if 'orbs at random' in skill_text:
        results.add(AsCondition.ORB_CONVERT)

    all_colors = colors + ['heal', 'poison', 'mortal poison', 'jammer']
    if any(['change {} orbs'.format(x) in skill_text for x in all_colors]):
        results.add(AsCondition.ORB_CONVERT)
    if any(['change {}, '.format(x) in skill_text for x in all_colors]):
        results.add(AsCondition.ORB_CONVERT)

    skill_mod = re.sub(r'0[.]\d+x', ' ', skill_text)
    if 'x rcv' in skill_mod:
        results.add(AsCondition.ENHANCED_HEAL)

    if 'becomes team leader' in skill_text:
        results.add(AsCondition.THE_SWITCH)

    if 'become mass attack' in skill_text:
        results.add(AsCondition.ATTACK_CHANGER)

    if re.match('.*change.*orbs to.*;.*change.*orbs to.*', skill_text):
        results.add(AsCondition.DOUBLE_ORBS_CONVERT)

    if 'change all orbs' in skill_text:
        results.add(AsCondition.ALL_ORBS_CONVERT)

    if 'reduce hp' in skill_text:
        results.add(AsCondition.SUICIDE)

    awoken_recovery = 'awoken skill binds' in skill_text
    bind_recovery = 'remove all binds' in skill_text or 'reduce binds' in skill_text
    heal = 'recover' in skill_text and 'damage to an enemy and recover' not in skill_text

    if heal:
        results.add(AsCondition.HEAL)
    if bind_recovery:
        results.add(AsCondition.RECOVER_BIND)
    if heal and bind_recovery:
        results.add(AsCondition.HEAL_BIND_RECOVERY)
    if awoken_recovery:
        results.add(AsCondition.AWOKEN_INVALID_RECOVERY)
    if bind_recovery and awoken_recovery:
        results.add(AsCondition.BIND_AWOKEN_INVALID_RECOVERY)

    if 'are more likely to appear' in skill_text:
        results.add(AsCondition.DROP_CHANCE)

    if 'damage to an enemy and recover' in skill_text:
        results.add(AsCondition.ATTACK_AND_HEAL)
    elif 'fixed damage to' in skill_text:
        results.add(AsCondition.FIXED_DAMAGE)
    elif 'damage to an enemy' in skill_text or 'atk to an enemy' in skill_text:
        results.add(AsCondition.SINGLE_TARGET_ATTACK)
    elif 'damage to all enemies' in skill_text or 'atk to all enemies' in skill_text:
        results.add(AsCondition.MASSIVE_ATTACK)
    elif any(['damage to all {} att'.format(x) in skill_text for x in colors]):
        results.add(AsCondition.ATTRIBUTE_ATTACK)

    if 'column to' in skill_text or 'row to' in skill_text:
        results.add(AsCondition.LINE_ORBS_CONVERTER)

    if 'increase orb move time' in skill_text:
        results.add(AsCondition.EXTENDS_TIME)
    if re.match('.*\dx orb move time.*', skill_text):
        results.add(AsCondition.EXTENDS_TIME)

    if 'change own att' in skill_text:
        results.add(AsCondition.CHANGE_ATTRIBUTE)

    if 'charge allies' in skill_text:
        results.add(AsCondition.REDUCE_SKILL_TURN)

    if 'replace all orbs' in skill_text:
        results.add(AsCondition.ORB_REFRESH)

    if 'change all enemies to' in skill_text:
        results.add(AsCondition.CHANGE_ENEMIES_ATTRIBUTE)

    if 'increase combo count' in skill_text:
        results.add(AsCondition.ADD_COMBO)

    if 'enemies max hp' in skill_text:
        results.add(AsCondition.NEW_GRAVITY)

    if 'unlock' in skill_text:
        results.add(AsCondition.REMOVE_LOCK)

    if 'damage absorb shield' in skill_text:
        results.add(AsCondition.VOID_DAMAGE_ABSORBS)

    if 'att. absorb shield' in skill_text:
        results.add(AsCondition.VOID_ATT_ABSORBS)

    if 'no skyfall' in skill_text:
        results.add(AsCondition.VOID_SKYFALLS)

    if ' lock ' in skill_text:
        results.add(AsCondition.ORB_LOCK)

    if 'show path to' in skill_text:
        results.add(AsCondition.COMBO_ROOT)

    return results


def parse_ls_conditions(skill_text: str) -> List[LsCondition]:
    """Takes the processor-generated leader skill text and produces a list of conditions."""
    skill_text = skill_text.lower()
    results = set()

    if 'additional heal when matching' in skill_text:
        results.add(LsCondition.AUTO_HEAL)

    # Strip out stuff like 0.25x because there's no reduction category,
    # don't want it to match for enhanced categories.
    skill_mod = re.sub(r'0[.]\d+x', ' ', skill_text)
    skill_mod = skill_mod.replace('x rcv additional heal', '')

    hp, atk, rcv = False, False, False
    if 'x all stats' in skill_mod:
        hp, atk, rcv = True, True, True
    if 'x hp & atk' in skill_mod:
        hp, atk = True, True
    if 'x hp & rcv' in skill_mod:
        hp, rcv = True, True
    if 'x atk & rcv' in skill_mod:
        atk, rcv = True, True
    if 'x hp' in skill_mod:
        hp = True
    if 'x atk' in skill_mod:
        atk = True
    if 'x rcv' in skill_mod:
        rcv = True

    if hp:
        if atk:
            if rcv:
                results.add(LsCondition.ENHANCED_HP_ATK_RCV)
            else:
                results.add(LsCondition.ENHANCED_HP_ATK)
        elif rcv:
            results.add(LsCondition.ENHANCED_HP_RCV)
        else:
            results.add(LsCondition.ENHANCED_HP)
    elif atk:
        if rcv:
            results.add(LsCondition.ENHANCED_ATK_RCV)
        else:
            results.add(LsCondition.ENHANCED_ATK)
    elif rcv:
        results.add(LsCondition.ENHANCED_RCV)

    if 'reduce damage taken' in skill_text:
        results.add(LsCondition.REDUCE_DAMAGE)

    if 'additional damage when matching' in skill_text:
        results.add(LsCondition.ADDITIONAL_ATTACK)

    if 'counterattack' in skill_text:
        results.add(LsCondition.COUNTERATTACK)

    if 'may survive when hp is reduced to 0' in skill_text:
        results.add(LsCondition.RESOLVE)

    if 'increase orb movement time' in skill_text:
        results.add(LsCondition.EXTEND_TIME)

    if 'x coin drop rate' in skill_text:
        results.add(LsCondition.COIN)

    if 'x egg drop rate' in skill_text:
        results.add(LsCondition.EGG)

    if 'x rank exp' in skill_text:
        results.add(LsCondition.EXP)

    if 'board becomes 7x6' in skill_text:
        results.add(LsCondition.BOARD_CHANGE_7X6)

    if 'no skyfall' in skill_text:
        results.add(LsCondition.NO_SKYFALL_COMBOS)

    etc_text = [
        'taiko',
        'power-up',
        'fuse',
        'sells for',
        'special evo material',
        'monster points',
    ]
    if any([x in skill_text for x in etc_text]):
        results.add(LsCondition.ETC)

    return results
