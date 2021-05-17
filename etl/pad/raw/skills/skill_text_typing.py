from pad.common.utils import format_int_list
from pad.raw.skills.active_skill_info import *
from pad.raw.skills.leader_skill_info import *


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
class ASCondition(Enum):
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
    COMBO_ROUTE = 280
    REDUCE_MATCH_RESTRICTION = 281
    PIERCE_DAMAGE_VOID = 282


class LSCondition(Enum):
    AUTO_HEAL = 1
    ENHANCED_HP = 25
    ENHANCED_ATK = 26
    ENHANCED_RCV = 27
    ENHANCED_HP_ATK = 28
    ENHANCED_HP_RCV = 29
    ENHANCED_ATK_RCV = 30
    ENHANCED_HP_ATK_RCV = 31
    REDUCE_DAMAGE = 32
    ADDITIONAL_ATTACK = 34
    COUNTERATTACK = 35
    RESOLVE = 36
    EXTEND_TIME = 37
    COIN = 150
    EGG = 160
    EXP = 170
    BOARD_CHANGE_7X6 = 200
    NO_SKYFALL_COMBOS = 210
    EXTRA_COMBOS = 211
    ORB_SOUNDS = 999


def format_conditions(skill_conditions):
    sorted_cond_values = sorted([x.value for x in skill_conditions])
    return format_int_list(sorted_cond_values)


def parse_as_conditions(skill, child=False) -> List[ASCondition]:
    """Takes the processor-generated active skill text and produces a list of conditions."""
    if not child:
        skill = skill.cur_skill
    results = set()

    if isinstance(skill, ASMultiPartSkill):
        for s in skill.parts:
            results |= parse_as_conditions(s, True)
        if len([s for s in skill.parts if isinstance(s, (ASOneAttrtoOneAttr,
                                                         ASTwoAttrtoOneTwoAttr,
                                                         ASThreeAttrtoOneAttr))]) >= 2:
            results.add(ASCondition.DOUBLE_ORBS_CONVERT)

    if isinstance(skill, ASRandomSkill):
        results.add(ASCondition.ETC)
        for s in skill.random_skills:
            results |= parse_as_conditions(s, True)

    if isinstance(skill, (ASOrbEnhance, ASBicolorOrbEnhance, ASOrbEnhanceNew)):
        results.add(ASCondition.ENHANCED_ORBS)

    if isinstance(skill, (ASAttrBurst, ASAttrBurstMultiPart)):
        if skill.attributes:
            results.add(ASCondition.ENHANCED_ATTACK)
        if skill.rcv_boost and skill.multiplier >= 1:
            results.add(ASCondition.ENHANCED_HEAL)

    if isinstance(skill, (ASTypeBurst, ASTypeBurstNew)):
        results.add(ASCondition.ENHANCED_ATTACK)

    if isinstance(skill, ASDefenseBreak):
        results.add(ASCondition.REDUCE_DEFENSE)

    if isinstance(skill, ASGravity):
        results.add(ASCondition.GRAVITY)

    if isinstance(skill, (ASOneAttrtoOneAttr, ASTwoAttrtoOneTwoAttr, ASThreeAttrtoOneAttr)):
        results.add(ASCondition.ORB_CONVERT)
        if 5 in skill.from_attr:
            results.add(ASCondition.ATTACK_STANCE)
        if 5 in skill.to_attr:
            results.add(ASCondition.GUARD_STANCE)

    if isinstance(skill, ASDelay):
        results.add(ASCondition.MENACE)

    if isinstance(skill, ASFreeOrbMovement):
        results.add(ASCondition.STOP_TIME)

    if isinstance(skill, (ASDamageReduction, ASDamageVoid)):
        if skill.shield == 1:
            results.add(ASCondition.VOID_DAMAGE)
        else:
            results.add(ASCondition.REDUCE_DAMAGE)

    if isinstance(skill, (ASAwokenSkillBurst, ASAwokenSkillBurst2)):
        if skill.toggle == 1:
            results.add(ASCondition.ENHANCED_HEAL)
        elif skill.toggle in [0, 2]:
            results.add(ASCondition.ENHANCED_ATTACK)
        elif skill.toggle == 3:
            results.add(ASCondition.REDUCE_DAMAGE)

    if isinstance(skill, ASPoisonEnemies):
        results.add(ASCondition.POISON)

    if isinstance(skill, ASCounterattack):
        results.add(ASCondition.COUNTERATTACK)

    if isinstance(skill, ASLowHpConditionalAttrDamageBoost):
        results.add(ASCondition.GRUDGE_STRIKE)

    if isinstance(skill, ASLeaderSwap):
        results.add(ASCondition.THE_SWITCH)

    if isinstance(skill, ASMassAttack):
        results.add(ASCondition.ATTACK_CHANGER)

    if isinstance(skill, ASTwoAttrtoOneTwoAttr):
        if len(skill.to_attr) > 1:
            results.add(ASCondition.DOUBLE_ORBS_CONVERT)

    if isinstance(skill, (ASBoardChange, ASShowComboPath)):
        results.add(ASCondition.ALL_ORBS_CONVERT)
    if isinstance(skill, ASThreeAttrtoOneAttr):
        if skill.from_attr == list(range(10)):
            results.add(ASCondition.ALL_ORBS_CONVERT)

    if isinstance(skill, (ASHpConditionalTargetNuke, ASHpConditionalMassNuke,
                          ASTargetNukeWithHpPenalty, ASMassNukeWithHpPenalty,
                          ASSuicide195)):
        results.add(ASCondition.SUICIDE)

    if isinstance(skill, (ASHpRecovery, ASHpRecoverFromRcv, ASHpRecoverStatic, ASHpRecoveryandBindClear)):
        if any([getattr(skill, 'hp', 0),
                getattr(skill, 'rcv_multiplier_as_hp', 0),
                getattr(skill, 'percentage_max_hp', 0),
                getattr(skill, 'team_rcv_multiplier_as_hp', 0)]):
            results.add(ASCondition.HEAL)
    if isinstance(skill, ASAutoHealConvert):
        if skill.duration:
            results.add(ASCondition.HEAL)
    if isinstance(skill, (ASAutoHealConvert, ASHpRecoveryandBindClear)):
        if skill.card_bind:
            results.add(ASCondition.RECOVER_BIND)
        if skill.awoken_bind:
            results.add(ASCondition.AWOKEN_INVALID_RECOVERY)

    if ASCondition.RECOVER_BIND in results and ASCondition.AWOKEN_INVALID_RECOVERY in results:
        results.add(ASCondition.BIND_AWOKEN_INVALID_RECOVERY)
    if ASCondition.RECOVER_BIND in results and ASCondition.HEAL in results:
        results.add(ASCondition.HEAL_BIND_RECOVERY)

    if isinstance(skill, ASIncreasedSkyfallChance):
        results.add(ASCondition.DROP_CHANCE)

    if isinstance(skill, (ASMiniNukeandHpRecovery, ASAtkBasedNuke)):
        results.add(ASCondition.ATTACK_AND_HEAL)

    if isinstance(skill, (ASTrueDamageNuke, ASTrueDamageNukeAll, ASMultiLaserConvert)):
        results.add(ASCondition.FIXED_DAMAGE)

    if hasattr(skill, 'mass_attack'):
        if skill.mass_attack:
            results.add(ASCondition.MASSIVE_ATTACK)
        else:
            results.add(ASCondition.SINGLE_TARGET_ATTACK)

    if isinstance(skill, ASAttrOnAttrNuke):
        results.add(ASCondition.ATTRIBUTE_ATTACK)

    if isinstance(skill, (ASColumnOrbChange, ASRowOrbChange)):
        results.add(ASCondition.LINE_ORBS_CONVERTER)

    if isinstance(skill, ASIncreasedOrbMovementTime):
        results.add(ASCondition.EXTENDS_TIME)

    if isinstance(skill, ASAttributeChange):
        results.add(ASCondition.CHANGE_ATTRIBUTE)

    if isinstance(skill, ASHaste):
        results.add(ASCondition.REDUCE_SKILL_TURN)

    if isinstance(skill, ASOrbRefresh):
        results.add(ASCondition.ORB_REFRESH)

    if isinstance(skill, ASEnemyAttrChange):
        results.add(ASCondition.CHANGE_ENEMIES_ATTRIBUTE)

    if isinstance(skill, ASAddAdditionalCombos):
        results.add(ASCondition.ADD_COMBO)

    if isinstance(skill, ASTrueGravity):
        results.add(ASCondition.NEW_GRAVITY)

    if isinstance(skill, (ASOrbLockRemoval, ASShowComboPath)):
        results.add(ASCondition.REMOVE_LOCK)

    if isinstance(skill, ASVoidDamageAbsorption):
        if skill.damage_absorb:
            results.add(ASCondition.VOID_DAMAGE_ABSORBS)
        if skill.attribute_absorb:
            results.add(ASCondition.VOID_ATT_ABSORBS)

    if isinstance(skill, ASReduceVoidDamage):
        results.add(ASCondition.PIERCE_DAMAGE_VOID)

    if isinstance(skill, ASNoSkyfallForXTurns):
        results.add(ASCondition.VOID_SKYFALLS)

    if isinstance(skill, ASOrbLock):
        results.add(ASCondition.ORB_LOCK)

    if isinstance(skill, ASShowComboPath):
        results.add(ASCondition.COMBO_ROUTE)

    if isinstance(skill, ASReduceDisableMatch):
        results.add(ASCondition.REDUCE_MATCH_RESTRICTION)

    if child:
        return results
    return sorted(results, key=lambda x: x.value)


def parse_ls_conditions(skill, child=False) -> List[LSCondition]:
    """Takes the processor-generated leader skill text and produces a list of conditions."""
    if not child:
        skill = skill.cur_skill
    results = set()

    if isinstance(skill, LSMultiPartSkill):
        for s in skill.parts:
            results |= parse_ls_conditions(s, True)

    if child:
        pass
    elif skill.hp > 1:
        if skill.atk > 1:
            if skill.rcv > 1:
                results.add(LSCondition.ENHANCED_HP_ATK_RCV)
            else:
                results.add(LSCondition.ENHANCED_HP_ATK)
        elif skill.rcv > 1:
            results.add(LSCondition.ENHANCED_HP_RCV)
        else:
            results.add(LSCondition.ENHANCED_HP)
    elif skill.atk > 1:
        if skill.rcv > 1:
            results.add(LSCondition.ENHANCED_ATK_RCV)
        else:
            results.add(LSCondition.ENHANCED_ATK)
    elif skill.rcv > 1:
        results.add(LSCondition.ENHANCED_RCV)

    if skill.shield > 0:
        results.add(LSCondition.REDUCE_DAMAGE)

    if isinstance(skill, LSAutoheal):
        results.add(LSCondition.AUTO_HEAL)

    if skill.mult_bonus_damage or skill.bonus_damage:
        results.add(LSCondition.ADDITIONAL_ATTACK)

    if isinstance(skill, LSCounterattack):
        results.add(LSCondition.COUNTERATTACK)

    if isinstance(skill, LSResolve):
        results.add(LSCondition.RESOLVE)

    if skill.extra_time:
        results.add(LSCondition.EXTEND_TIME)

    if isinstance(skill, LSCoinDropBoost):
        results.add(LSCondition.COIN)

    if isinstance(skill, LSEggDropRateBoost):
        results.add(LSCondition.EGG)

    if isinstance(skill, LSRankXpBoost):
        results.add(LSCondition.EXP)

    if isinstance(skill, (LSSevenBySix, LSSevenBySixStatBoost)):
        results.add(LSCondition.BOARD_CHANGE_7X6)

    if isinstance(skill, (LSNoSkyfallBoost, LSOrbRemainingMultiplier)):
        results.add(LSCondition.NO_SKYFALL_COMBOS)

    if isinstance(skill, LSTaikoDrum):
        results.add(LSCondition.ORB_SOUNDS)

    if skill.extra_combos:
        results.add(LSCondition.EXTRA_COMBOS)

    if child:
        return results
    return sorted(results, key=lambda x: x.value)
