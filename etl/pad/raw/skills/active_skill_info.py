import logging
from collections import Counter, defaultdict, namedtuple
from copy import copy
from fractions import Fraction
from numbers import Rational
from typing import Any, Iterable, List, Mapping, Optional, Union

from pad.raw.skill import MonsterSkill
from pad.raw.skills.behaviors.active_behaviors import ASBBoardChange, ASBBuff, ASBCustom, ASBDamage, ASBInflictDebuff, \
    ASBOrbChange, ASBRecover, \
    ASBSuperSkill, ASBehavior, behavior_to_json
from pad.raw.skills.skill_common import Board, binary_con, merge_defaults, mult

human_fix_logger = logging.getLogger('human_fix')

ASTextConverter = Any


class ActiveSkill:
    skill_type = -1
    compound_skill_type = 0

    def __init__(self, ms: MonsterSkill,
                 behavior: Union[List[ASBehavior], ASBehavior],
                 *,
                 transform_ids: Mapping[int, Rational] = None,
                 board: Board = None,
                 needs_context: bool = False):
        if transform_ids is None:
            transform_ids = {None: 1}
        if board is None:
            board = Board()
        if behavior is None:
            behavior = []
        elif not isinstance(behavior, list):
            behavior = [behavior]

        if self.skill_type != ms.skill_type:
            raise ValueError('Expected {} but got {}'.format(self.skill_type, ms.skill_type))

        self.skill_id = ms.skill_id
        self.name = ms.name
        self.raw_description = ms.clean_description
        self.raw_data = ms.data
        self.skill_type = ms.skill_type
        self.levels = ms.levels
        self.cooldown_turns_max = ms.cooldown_turns_max
        self.cooldown_turns_min = ms.cooldown_turns_min

        self._transform_ids = transform_ids
        self._board = board
        self._behavior = behavior

        # If this is true, text can take an optional context: Iterable[ActiveSkill] argument
        self.needs_context = needs_context

    @property
    def subskills(self) -> List["ActiveSkill"]:
        return [self]

    @property
    def parts(self) -> List["ActiveSkill"]:
        return [self]

    @property
    def transform_ids(self) -> Mapping[int, Rational]:
        return self._transform_ids

    @property
    def board(self) -> Board:
        return self._board

    @property
    def behavior(self) -> List[ASBehavior]:
        return self._behavior

    def text(self, converter: ASTextConverter) -> str:
        return '<unsupported>: {}'.format(self.raw_description)

    def templated_text(self, converter: ASTextConverter) -> str:
        return self.text(converter) or ''

    def full_text(self, converter: ASTextConverter) -> str:
        return converter.process_raw(self.templated_text(converter))


class ASConditional(ActiveSkill):
    pass


class ASMultiPart(ActiveSkill):
    multipart_type = 'multipart'

    def __init__(self, ms: MonsterSkill):
        self.child_ids: List[int] = ms.data
        self.child_skills: List[ActiveSkill] = []

        super().__init__(ms, ASBSuperSkill(self.multipart_type, self.child_skills))

    @property
    def parts(self):
        return sum([s.parts for s in self.child_skills], [])

    @property
    def transform_ids(self):
        for part in self.child_skills:
            if any(mid is not None for mid in part.transform_ids.keys()):
                return part.transform_ids
        return {None: 1}

    @property
    def board(self):
        if not self.child_skills:
            return Board()
        board = self.child_skills[0].board
        for part in self.child_skills:
            board |= part.board
        return board

    @property
    def behavior(self):
        return [asb for act in self.child_skills for asb in act.behavior]


class ASCompound(ASMultiPart):
    @property
    def subskills(self) -> List["ActiveSkill"]:
        return self.child_skills


class ASMultiplierMultiTargetAttrNuke(ActiveSkill):
    # Do not add this to the ALL_SKILLS list! skill_type=0 can imply 'no skill'
    skill_type = 0

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.attribute = data[0]
        self.multiplier = mult(data[1])
        self.mass_attack = True
        super().__init__(ms, ASBDamage('flat', self.multiplier, self.attribute))

    def text(self, converter: ASTextConverter) -> str:
        return converter.attr_nuke_convert(self)


class ASFixedMultiTargetAttrNuke(ActiveSkill):
    skill_type = 1

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1])
        self.attribute = data[0]
        self.damage = data[1]
        self.mass_attack = True
        super().__init__(ms, ASBDamage('multiplier', self.damage, self.attribute))

    def text(self, converter: ASTextConverter) -> str:
        return converter.fixed_attr_nuke_convert(self)


class ASMultiplierSelfAttrSingleTargetNuke(ActiveSkill):
    skill_type = 2

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1])
        self.multiplier = mult(data[0])
        self.mass_attack = False
        super().__init__(ms, ASBDamage('multiplier', self.multiplier))

    def text(self, converter: ASTextConverter) -> str:
        return converter.self_att_nuke_convert(self)


class ASDamageReduction(ActiveSkill):
    skill_type = 3

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1, 0])
        self.duration = data[0]
        self.shield = mult(data[1])
        super().__init__(ms, ASBBuff('shield', self.duration,
                                     {'strength': self.shield, 'attribute': []}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.shield_convert(self)


class ASPoisonEnemies(ActiveSkill):
    skill_type = 4

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1])
        self.multiplier = mult(data[0])
        super().__init__(ms, ASBInflictDebuff('poison', {'mult': self.multiplier}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.poison_convert(self)


class ASFreeOrbMovement(ActiveSkill):
    skill_type = 5

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.duration = data[0]
        super().__init__(ms, ASBCustom('free_movement', {'duration': self.duration}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.ctw_convert(self)


class ASGravity(ActiveSkill):
    skill_type = 6

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.percentage_hp = mult(data[0])
        super().__init__(ms, ASBDamage('gravity', self.percentage_hp))

    def text(self, converter: ASTextConverter) -> str:
        return converter.gravity_convert(self)


class ASHpRecoverFromRcv(ActiveSkill):
    skill_type = 7

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.rcv_multiplier_as_hp = mult(data[0])
        super().__init__(ms, ASBRecover('multiplier', self.rcv_multiplier_as_hp))

    def text(self, converter: ASTextConverter) -> str:
        return converter.heal_active_convert(self)


class ASHpRecoverStatic(ActiveSkill):
    skill_type = 8

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.hp = data[0]
        super().__init__(ms, ASBRecover('flat', self.hp))

    def text(self, converter: ASTextConverter) -> str:
        return converter.heal_active_convert(self)


class ASOneAttrtoOneAttr(ActiveSkill):
    skill_type = 9

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.from_attr = [data[0]]
        self.to_attr = [data[1]]
        super().__init__(ms, ASBOrbChange(self.from_attr, self.to_attr))

    def text(self, converter: ASTextConverter) -> str:
        return converter.random_orb_change_convert(self)


class ASOrbRefresh(ActiveSkill):
    skill_type = 10

    def __init__(self, ms: MonsterSkill):
        super().__init__(ms, ASBCustom('orb_refresh'))

    def text(self, converter: ASTextConverter) -> str:
        return converter.board_refresh(self)


class ASDelay(ActiveSkill):
    skill_type = 18

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.turns = data[0]
        super().__init__(ms, ASBInflictDebuff('delay', {'turns': self.turns}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.delay_convert(self)


class ASDefenseBreak(ActiveSkill):
    skill_type = 19

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.duration = data[0]
        self.shield = mult(data[1])
        super().__init__(ms, ASBInflictDebuff('guard_break', {'percent': self.shield}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.defense_reduction_convert(self)


class ASTwoAttrtoOneTwoAttr(ActiveSkill):
    skill_type = 20

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.from_attr = [data[0], data[2]]
        self.to_attr = [data[1], data[3]] if data[1] != data[3] else [data[1]]
        super().__init__(ms, ASBOrbChange(self.from_attr, self.to_attr))

    def text(self, converter: ASTextConverter) -> str:
        return converter.double_orb_convert(self)


class ASDamageVoid(ActiveSkill):
    skill_type = 21

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.duration = data[0]
        self.attribute = data[1]
        self.shield = mult(data[2])
        super().__init__(ms, ASBBuff('shield', self.duration,
                                     {'strength': self.shield, 'attribute': [self.attribute]}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.elemental_shield_convert(self)


class ASAtkBasedNuke(ActiveSkill):
    skill_type = 35

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.atk_multiplier = mult(data[0])
        self.recover_multiplier = mult(data[1])
        self.mass_attack = False
        super().__init__(ms, ASBDamage('multiplier', self.atk_multiplier,
                                       mass_attack=False, recover=self.recover_multiplier))

    def text(self, converter: ASTextConverter) -> str:
        return converter.drain_attack_convert(self)


class ASSingleTargetTeamAttrNuke(ActiveSkill):
    skill_type = 37

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1])
        self.attribute = data[0]
        self.multiplier = mult(data[1])
        self.mass_attack = False
        super().__init__(ms, ASBDamage('multiplier', self.multiplier,
                                       mass_attack=False, attribute=self.attribute))

    def text(self, converter: ASTextConverter) -> str:
        return converter.attr_nuke_convert(self)


class ASAttrOnAttrNuke(ActiveSkill):
    skill_type = 42

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 1])
        self.enemy_attribute = data[0]
        self.attack_attribute = data[1]
        self.damage = data[2]
        super().__init__(ms, ASBDamage('flat', self.damage, self.attack_attribute,
                                       target_attribute=self.enemy_attribute))

    def text(self, converter: ASTextConverter) -> str:
        return converter.damage_to_att_enemy_convert(self)


class ASAttrBurst(ActiveSkill):
    skill_type = 50

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.duration = data[0]
        self.attributes = [data[1]]
        self.rcv_boost = False
        if 5 in self.attributes:
            self.rcv_boost = True
            self.attributes.remove(5)
        self.multiplier = mult(data[2])
        self.atk = self.multiplier
        super().__init__(ms, ASBBuff('stat_mult', self.duration,
                                     {'stats': (1.0, self.multiplier, self.multiplier if self.rcv_boost else 1.0),
                                      'target': {
                                          'attributes': self.attributes,
                                          'types': [],
                                          'target_bitmap': 0}}))

    def text(self, converter: ASTextConverter) -> str:
        # TODO: uhhh maybe this can be cleaned up
        if self.attributes == [] and self.rcv_boost:
            return converter.rcv_boost_convert(self)
        else:
            return converter.attribute_attack_boost_convert(self)


class ASMassAttack(ActiveSkill):
    skill_type = 51

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.duration = data[0]
        super().__init__(ms, ASBBuff('mass_attack', self.duration))

    def text(self, converter: ASTextConverter) -> str:
        return converter.mass_attack_convert(self)


class ASOrbEnhance(ActiveSkill):
    skill_type = 52

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.orbs = [data[0]]
        super().__init__(ms, ASBCustom('enhance', {'attributes': self.orbs}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.enhance_convert(self)


class ASTrueDamageNuke(ActiveSkill):
    skill_type = 55

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.damage = data[0]
        self.mass_attack = False
        super().__init__(ms, ASBDamage('flat', self.damage,
                                       laser=True, mass_attack=False))

    def text(self, converter: ASTextConverter) -> str:
        return converter.laser_convert(self)


class ASTrueDamageNukeAll(ActiveSkill):
    skill_type = 56

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.damage = data[0]
        self.mass_attack = True
        super().__init__(ms, ASBDamage('flat', self.damage,
                                       laser=True, mass_attack=True))

    def text(self, converter: ASTextConverter) -> str:
        return converter.laser_convert(self)


class ASAttrMassAttack(ActiveSkill):
    skill_type = 58

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1, 1])
        self.attribute = data[0]
        self.minimum_multiplier = mult(data[1])
        self.maximum_multiplier = mult(data[2])
        self.mass_attack = True
        super().__init__(ms, ASBDamage('multiplier', self.maximum_multiplier,
                                       mass_attack=True, attribute=self.attribute,
                                       min_damage=self.minimum_multiplier))

    def text(self, converter: ASTextConverter) -> str:
        return converter.random_nuke_convert(self)


class ASAttrRandomNuke(ActiveSkill):
    skill_type = 59

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1, 1])
        self.attribute = data[0]
        self.minimum_multiplier = mult(data[1])
        self.maximum_multiplier = mult(data[2])
        self.mass_attack = False
        super().__init__(ms, ASBDamage('multiplier', self.maximum_multiplier,
                                       mass_attack=False, attribute=self.attribute,
                                       min_damage=self.minimum_multiplier))

    def text(self, converter: ASTextConverter) -> str:
        return converter.random_nuke_convert(self)


class ASCounterattack(ActiveSkill):
    skill_type = 60

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1, 1, 0])
        self.duration = data[0]
        self.multiplier = mult(data[1])
        self.attribute = data[2]
        super().__init__(ms, ASBBuff('counterattack', self.duration, {'mult': self.multiplier}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.counterattack_convert(self)


class ASBoardChange(ActiveSkill):
    skill_type = 71

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [])
        self.from_attr = list(range(10))
        self.to_attr = [v for v in data if v != -1]

        board = None
        if len(self.to_attr) == 1:
            board = Board([[self.to_attr[0] for _ in range(7)] for _ in range(6)])

        super().__init__(ms, ASBOrbChange(self.from_attr, self.to_attr), board=board)

    def text(self, converter: ASTextConverter) -> str:
        return converter.board_change_convert(self)


class ASHpConditionalTargetNuke(ActiveSkill):
    skill_type = 84

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1, 1, 0])
        self.attribute = data[0]
        self.minimum_multiplier = mult(data[1])
        self.maximum_multiplier = mult(data[2])
        self.hp_remaining = mult(data[3])
        self.mass_attack = False
        super().__init__(ms, [ASBCustom('suicide', hp_left=self.hp_remaining),
                              ASBDamage('multiplier', self.maximum_multiplier,
                                        attribute=self.attribute, mass_attack=False,
                                        min_damage=self.maximum_multiplier)])

    def text(self, converter: ASTextConverter) -> str:
        return converter.suicide_random_nuke_convert(self)


class ASHpConditionalMassNuke(ActiveSkill):
    skill_type = 85

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1, 1, 0])
        self.attribute = data[0]
        self.minimum_multiplier = mult(data[1])
        self.maximum_multiplier = mult(data[2])
        self.hp_remaining = mult(data[3])
        self.mass_attack = True
        super().__init__(ms, [ASBCustom('suicide', hp_left=self.hp_remaining),
                              ASBDamage('multiplier', self.maximum_multiplier,
                                        attribute=self.attribute, mass_attack=True,
                                        min_damage=self.maximum_multiplier)])

    def text(self, converter: ASTextConverter) -> str:
        return converter.suicide_random_nuke_convert(self)


class ASTargetNukeWithHpPenalty(ActiveSkill):
    skill_type = 86

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.attribute = data[0]
        self.damage = data[1]
        self.hp_remaining = mult(data[3])
        self.mass_attack = False
        super().__init__(ms, [ASBCustom('suicide', hp_left=self.hp_remaining),
                              ASBDamage('flat', self.damage,
                                        attribute=self.attribute, mass_attack=False)])

    def text(self, converter: ASTextConverter) -> str:
        return converter.suicide_nuke_convert(self)


class ASMassNukeWithHpPenalty(ActiveSkill):
    skill_type = 87

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.attribute = data[0]
        self.damage = data[1]
        self.hp_remaining = mult(data[3])
        self.mass_attack = True
        super().__init__(ms, [ASBCustom('suicide', hp_left=self.hp_remaining),
                              ASBDamage('flat', self.damage,
                                        attribute=self.attribute, mass_attack=True)])

    def text(self, converter: ASTextConverter) -> str:
        return converter.suicide_nuke_convert(self)


class ASTypeBurst(ActiveSkill):
    skill_type = 88

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.duration = data[0]
        self.types = [data[1]]
        self.multiplier = mult(data[2])
        super().__init__(ms, ASBBuff('stat_mult', self.duration,
                                     {'stats': (1.0, self.multiplier, 1.0),
                                      'target': {
                                          'attributes': [],
                                          'types': self.types,
                                          'target_bitmap': 0}}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.type_attack_boost_convert(self)


class ASAttrBurstMultiPart(ActiveSkill):
    skill_type = 90

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0])
        self.duration = data[0]
        self.attributes = data[1:3]
        self.multiplier = mult(data[3])
        self.rcv_boost = False

        if 5 in self.attributes:
            self.rcv_boost = True
            self.attributes.remove(5)

        super().__init__(ms, ASBBuff('stat_mult', self.duration,
                                     {'stats': (1.0, self.multiplier, self.multiplier if self.rcv_boost else 1.0),
                                      'target': {
                                          'attributes': self.attributes,
                                          'types': [],
                                          'target_bitmap': 0}}))

    def text(self, converter: ASTextConverter) -> str:
        if self.duration == 0:
            return ''
        return converter.attribute_attack_boost_convert(self)


class ASBicolorOrbEnhance(ActiveSkill):
    skill_type = 91

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.orbs = data[0:2]
        super().__init__(ms, ASBCustom('enhance', {'attributes': self.orbs}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.enhance_convert(self)


class ASTypeBurstNew(ActiveSkill):
    skill_type = 92

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 1])
        self.duration = data[0]
        self.types = data[1:3]
        self.multiplier = mult(data[3])
        super().__init__(ms, ASBBuff('stat_mult', self.duration,
                                     {'stats': (1.0, self.multiplier, 1.0),
                                      'target': {
                                          'attributes': [],
                                          'types': self.types,
                                          'target_bitmap': 0}}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.type_attack_boost_convert(self)


class ASLeaderSwap(ActiveSkill):
    skill_type = 93

    def __init__(self, ms: MonsterSkill):
        super().__init__(ms, ASBCustom('leader_swap', {'position': -1}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.leader_swap(self)


class ASLowHpConditionalAttrDamageBoost(ActiveSkill):
    skill_type = 110

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 1, 1])
        self.mass_attack = data[0] == 0
        self.attribute = data[1]
        self.high_multiplier = mult(data[2])
        self.low_multiplier = mult(data[3])
        super().__init__(ms, ASBDamage('grudge_multiplier', self.high_multiplier, min_damage=self.low_multiplier,
                                       attribute=self.attribute))

    def text(self, converter: ASTextConverter) -> str:
        return converter.grudge_strike_convert(self)


class ASMiniNukeandHpRecovery(ActiveSkill):
    skill_type = 115

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.attribute = data[0]
        self.atk_multiplier = mult(data[1])
        self.recover_multiplier = mult(data[2])
        self.mass_attack = False
        super().__init__(ms, ASBDamage('multiplier', self.atk_multiplier, recover=self.recover_multiplier,
                                       attribute=self.attribute))

    def text(self, converter: ASTextConverter) -> str:
        return converter.drain_attr_attack_convert(self)


class ASMultiPartSkill(ASMultiPart):
    skill_type = 116

    def text(self, converter: ASTextConverter) -> str:
        return converter.multi_part_active(self)


class ASHpRecoveryandBindClear(ActiveSkill):
    skill_type = 117

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0])
        self.card_bind = data[0]
        self.rcv_multiplier_as_hp = mult(data[1])
        self.hp = data[2]
        self.percentage_max_hp = mult(data[3])
        self.awoken_bind = bool(data[4])
        super().__init__(ms, ASBRecover('flat' if self.hp else
                                        'multiplier' if self.rcv_multiplier_as_hp else
                                        'percentage' if self.percentage_max_hp else 'unknown',
                                        self.hp or self.rcv_multiplier_as_hp or self.percentage_max_hp,
                                        skill_bind=self.card_bind, awoken_bind=self.awoken_bind))

    def text(self, converter: ASTextConverter) -> str:
        return converter.heal_active_convert(self)


class ASRandomSkill(ASCompound):
    skill_type = 118
    compound_skill_type = 1
    multipart_type = 'random'

    def text(self, converter: ASTextConverter) -> str:
        return converter.random_skill(self)

    @property
    def transform_ids(self):
        transform_ids = defaultdict(int)
        for part in self.child_skills:
            if not part.transform_ids:
                transform_ids[None] += 1
                continue
            for tfid, count in part.transform_ids.items():
                transform_ids[tfid] += Fraction(count, sum(part.transform_ids.values()))
        return transform_ids

    @property
    def board(self):
        board = Board()
        for part in self.child_skills:
            board &= part.board
        return board


class ASIncreasedSkyfallChance(ActiveSkill):
    skill_type = 126

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.orbs = binary_con(data[0])
        self.duration = data[1]
        self.max_duration = data[2]
        self.percentage = mult(data[3])
        super().__init__(ms, ASBBuff('skyfall_chance', self.duration,
                                     {'attributes': self.orbs, 'percentage': self.percentage}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.change_skyfall_convert(self)


OrbLine = namedtuple("OrbLine", ["index", "attrs"])


class ASColumnOrbChange(ActiveSkill):
    skill_type = 127

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [])
        # TODO: simplify this
        self.columns = [OrbLine(int(i), binary_con(orbs)) for indices, orbs in
                        zip(data[::2], data[1::2]) for i in binary_con(indices)]
        board = Board()
        for col in self.columns:
            # Ignore random cols
            if len(col.attrs) == 1:
                idx = col.index if col.index < 3 else col.index + 1
                board |= Board([[col.attrs[0] if j == idx else -1 for j in range(7)] for _ in range(6)])
        super().__init__(ms, ASBBoardChange(board.data), board=board)

    def text(self, converter: ASTextConverter) -> str:
        return converter.column_change_convert(self)


class ASRowOrbChange(ActiveSkill):
    skill_type = 128

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [])
        # TODO: simplify this
        self.rows = [OrbLine(int(i), binary_con(orbs)) for indices, orbs in
                     zip(data[::2], data[1::2]) for i in binary_con(indices)]

        board = Board()
        for row in self.rows:
            # Ignore random cols
            if len(row.attrs) == 1:
                idx = row.index if row.index < 2 else row.index + 1
                board |= Board([[row.attrs[0] if i == idx else -1 for _ in range(7)] for i in range(6)])

        super().__init__(ms, ASBBoardChange(board.data), board=board)

    def text(self, converter: ASTextConverter) -> str:
        return converter.row_change_convert(self)


class ASIncreasedOrbMovementTime(ActiveSkill):
    skill_type = 132

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.duration = data[0]
        self.static = data[1] / 10
        self.percentage = mult(data[2])
        super().__init__(ms, ASBBuff('orb_movement', self.duration,
                                     {'unit': 'flat' if self.static else 'multiplier',
                                      'amount': self.static or self.percentage}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.move_time_buff_convert(self)


class ASOrbEnhanceNew(ActiveSkill):
    skill_type = 140

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.orbs = binary_con(data[0])
        super().__init__(ms, ASBCustom('enhance', {'attributes': self.orbs}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.enhance_convert(self)


class ASRandomLocationOrbSpawn(ActiveSkill):
    skill_type = 141

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.amount = data[0]
        self.orbs = binary_con(data[1])
        self.excluding_orbs = binary_con(data[2])
        super().__init__(ms, behavior=ASBOrbChange(self.excluding_orbs, self.orbs, self.amount,
                                                   from_invert=True))

    def text(self, converter: ASTextConverter) -> str:
        return converter.spawn_orb_convert(self)


class ASAttributeChange(ActiveSkill):
    skill_type = 142

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.duration = data[0]
        self.attribute = data[1]
        super().__init__(ms, ASBBuff('attribute_change', self.duration,
                                     {'attribute': self.attribute,
                                      'target': {
                                          'attributes': [],
                                          'types': [],
                                          'target_bitmap': 1}}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.attribute_change_convert(self)


class ASHpMultiplierNuke(ActiveSkill):
    skill_type = 143

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.multiplier = mult(data[0])
        self.attribute = data[1]
        # Note; another slot must contain the attribute, since this is a fixed nuke.
        self.mass_attack = True
        super().__init__(ms, ASBDamage('hp_multiplier', self.multiplier, attribute=self.attribute))

    def text(self, converter: ASTextConverter) -> str:
        return converter.hp_nuke_convert(self)


class ASAttrNukeOfAttrTwoAtk(ActiveSkill):
    skill_type = 144

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.team_attributes = binary_con(data[0])
        self.multiplier = mult(data[1])
        self.mass_attack = data[2] == 0
        self.attack_attribute = data[3]
        super().__init__(ms, ASBDamage('team_multiplier', self.multiplier, attribute=self.attack_attribute,
                                       team_mult_attr=self.team_attributes, mass_attack=self.mass_attack))

    def text(self, converter: ASTextConverter) -> str:
        return converter.attack_attr_x_team_atk_convert(self)


class ASHpRecovery(ActiveSkill):
    skill_type = 145

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.team_rcv_multiplier_as_hp = mult(data[0])
        super().__init__(ms, ASBRecover('team_multiplier', self.team_rcv_multiplier_as_hp))

    def text(self, converter: ASTextConverter) -> str:
        return converter.heal_active_convert(self)


class ASHaste(ActiveSkill):
    skill_type = 146

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.turns = data[0]
        self.max_turns = data[1] or self.turns
        super().__init__(ms, ASBCustom('skill_charge', {'turns': [self.turns, self.max_turns]}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.haste_convert(self)


class ASOrbLock(ActiveSkill):
    skill_type = 152

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.orbs = binary_con(data[0])
        self.count = data[1]  # This can be 42/99 (both mean 'all') or a fixed number
        super().__init__(ms, ASBCustom('lock', {'attributes': self.orbs, 'count': self.count}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.lock_convert(self)


class ASEnemyAttrChange(ActiveSkill):
    skill_type = 153

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.turns = 9999
        self.attribute = data[0]
        super().__init__(ms, ASBBuff('enemy_attribute_change', self.turns,
                                     {'attribute': self.attribute}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.change_enemies_attribute_convert(self)


class ASThreeAttrtoOneAttr(ActiveSkill):
    skill_type = 154

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.from_attr = binary_con(data[0])
        self.to_attr = binary_con(data[1])
        super().__init__(ms, behavior=ASBOrbChange(self.from_attr, self.to_attr))

    def text(self, converter: ASTextConverter) -> str:
        return converter.random_orb_change_convert(self)


class ASAwokenSkillBurst(ActiveSkill):
    skill_type = 156

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1, 0, 0, 0, 0, 0])
        self.duration = data[0]
        self.awakenings = data[1:4]
        self.toggle = data[4]
        self.amount_per = None
        if self.toggle == 1:
            self.amount_per = data[5] / 100
        elif self.toggle == 2:
            self.amount_per = (data[5] - 100) / 100
        elif self.toggle == 3:
            self.amount_per = mult(data[5])
        # TODO: Add other toggles
        super().__init__(ms, ASBBuff('stat_mult', self.duration,
                                     {'stats': (1.0, self.amount_per, 1.0),
                                      'per': {'attributes': [],
                                              'types': [],
                                              'awakenings': self.awakenings}}))

    def text(self, converter: ASTextConverter) -> str:
        if self.toggle == 1:
            return converter.awakening_heal_convert(self)
        elif self.toggle == 2:
            return converter.awakening_attack_boost_convert(self)
        elif self.toggle == 3:
            return converter.awakening_shield_convert(self)
        else:
            return ''


class ASAwokenSkillBurst2(ActiveSkill):
    skill_type = 168

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1, 1, 0, 0, 0, 0, 0, 1])
        self.duration = data[0]
        self.awakenings = data[1:4]
        self._unknown = data[5]
        self.toggle = data[6]
        self.amount_per = None
        if self.toggle == 1:
            self.amount_per = data[7]
        elif self.toggle in [0, 2]:
            self.amount_per = mult(data[7])
        elif self.toggle == 3:
            self.amount_per = mult(data[7])
        # TODO: Add other toggles
        super().__init__(ms, ASBBuff('stat_mult', self.duration,
                                     {'stats': (1.0, self.amount_per, 1.0),
                                      'per': {'attributes': [],
                                              'types': [],
                                              'awakenings': self.awakenings}}))

    def text(self, converter: ASTextConverter) -> str:
        if self.toggle == 1:
            return converter.awakening_heal_convert(self)
        elif self.toggle in [0, 2]:
            return converter.awakening_attack_boost_convert(self)
        elif self.toggle == 3:
            return converter.awakening_shield_convert(self)
        else:
            return ''


class ASAddAdditionalCombos(ActiveSkill):
    skill_type = 160

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.duration = data[0]
        self.combos = data[1]
        super().__init__(ms, ASBBuff('increase_combo', self.duration,
                                     {'additional_combos': self.combos}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.extra_combo_convert(self)


class ASTrueGravity(ActiveSkill):
    skill_type = 161

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.percentage_max_hp = mult(data[0])
        super().__init__(ms, ASBDamage('true_gravity', self.percentage_max_hp))

    def text(self, converter: ASTextConverter) -> str:
        return converter.true_gravity_convert(self)


class ASOrbLockRemoval(ActiveSkill):
    skill_type = 172

    def __init__(self, ms: MonsterSkill):
        super().__init__(ms, ASBCustom('board_unlock'))

    def text(self, converter: ASTextConverter) -> str:
        return converter.unlock_all_orbs(self)


class ASVoidDamageAbsorption(ActiveSkill):
    skill_type = 173

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.duration = data[0]
        self.attribute_absorb = bool(data[1])
        self.damage_absorb = bool(data[3])
        super().__init__(ms, ASBBuff('void', self.duration,
                                     {'damage_void': False,
                                      'attribute_absorb': self.attribute_absorb,
                                      'damage_absorb': self.damage_absorb}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.absorb_mechanic_void_convert(self)


class ASFixedPosConvertSomething(ActiveSkill):
    skill_type = 176

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 0])
        self.pos_map = [binary_con(row) for row in data[:5]]
        self.attribute = data[5]

        board_data = [[self.attribute if j in self.pos_map[i] else -1 for j in range(6)] for i in range(5)]
        board_data.insert(2, copy(board_data[2]))
        [row.insert(3, row[3]) for row in board_data]
        board = Board(board_data)
        super().__init__(ms, ASBBoardChange(board.data), board=board)

    def text(self, converter: ASTextConverter) -> str:
        return converter.fixed_pos_convert(self)


class ASAutoHealConvert(ActiveSkill):
    skill_type = 179

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0])
        self.duration = data[0]
        self.percentage_max_hp = mult(data[2])
        self.card_bind = data[3]
        self.awoken_bind = data[4]
        super().__init__(ms, [ASBBuff('autoheal', self.duration,
                                      {'percentage': self.percentage_max_hp}),
                              ASBRecover('n/a', 0,
                                         skill_bind=self.card_bind, awoken_bind=self.awoken_bind)])

    def text(self, converter: ASTextConverter) -> str:
        return converter.auto_heal_convert(self)


class ASIncreasedEnhanceOrbSkyfall(ActiveSkill):
    skill_type = 180

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.duration = data[0]
        self.percentage_increase = mult(data[1])
        super().__init__(ms, ASBBuff('increase_skyfall', self.duration,
                                     {'percentage': self.percentage_increase,
                                      'attributes': [],
                                      'type': 'enhanced'}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.enhance_skyfall_convert(self)


class ASNoSkyfallForXTurns(ActiveSkill):
    skill_type = 184

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.duration = data[0]
        super().__init__(ms, ASBBuff('no_skyfall', self.duration))

    def text(self, converter: ASTextConverter) -> str:
        return converter.no_skyfall_convert(self)


class ASMultiLaserConvert(ActiveSkill):
    skill_type = 188

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.damage = data[0]
        self.mass_attack = False
        super().__init__(ms, ASBDamage('flat', self.damage,
                                       mass_attack=False, laser=True))

    def text(self, converter: ASTextConverter) -> str:
        return converter.multi_hit_laser_convert(self)


class ASShowComboPath(ActiveSkill):
    skill_type = 189

    def __init__(self, ms: MonsterSkill):
        super().__init__(ms, ASBCustom('show_path'))

    def text(self, converter: ASTextConverter) -> str:
        return converter.unlock_board_path_toragon(self)


class ASReduceVoidDamage(ActiveSkill):
    skill_type = 191

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.duration = data[0]
        super().__init__(ms, ASBBuff('void', self.duration,
                                     {'damage_void': True,
                                      'attribute_absorb': False,
                                      'damage_absorb': False}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.void_mechanic_convert(self)


class ASSuicide195(ActiveSkill):
    skill_type = 195

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.hp_remaining = mult(data[0])
        super().__init__(ms, ASBCustom('suicide', hp_left=self.hp_remaining))

    def text(self, converter: ASTextConverter) -> str:
        return converter.suicide_convert(self)


class ASReduceDisableMatch(ActiveSkill):
    skill_type = 196

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.duration = data[0]
        super().__init__(ms, ASBRecover('n/a', 0, match_bind=self.duration))

    def text(self, converter: ASTextConverter) -> str:
        return converter.match_disable_convert(self)


class ASChangeMonster(ActiveSkill):
    skill_type = 202

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        super().__init__(ms, ASBCustom('transform', {'monsters': data}),
                         transform_ids=Counter(data))

    def text(self, converter: ASTextConverter) -> str:
        return converter.change_monster(self)


class ASSkyfallLock(ActiveSkill):
    skill_type = 205

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1])
        self.orbs = binary_con(data[0])
        self.duration = data[1]
        super().__init__(ms, ASBBuff('increase_skyfall', self.duration,
                                     {'percentage': 1.0,
                                      'attributes': self.orbs,
                                      'type': 'locked'}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.skyfall_lock(self)


class ASSpawnSpinner(ActiveSkill):
    skill_type = 207

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1, 100, 0, 0, 0, 0, 0, 0])
        self.turns = data[0]
        self.speed = mult(data[1])
        self.pos_map = [binary_con(row) for row in data[2:7]]
        self.random_count = data[7]
        super().__init__(ms, ASBBuff('spinner', self.turns,
                                     {'speed': self.speed,
                                      'shape': self.pos_map,
                                      'random_count': self.random_count}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.spawn_spinner(self)


class ASRandomLocationDoubleOrbSpawn(ActiveSkill):
    skill_type = 208

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 0])
        self.amount = data[0]
        self.orbs = binary_con(data[1])
        self.excluding_orbs = binary_con(data[2])
        self.amount2 = data[3]
        self.orbs2 = binary_con(data[4])
        self.excluding_orbs2 = binary_con(data[5])
        super().__init__(ms, behavior=[ASBOrbChange(self.excluding_orbs, self.orbs, self.amount,
                                                    from_invert=True),
                                       ASBOrbChange(self.excluding_orbs2, self.orbs2, self.amount2,
                                                    from_invert=True)])

    def text(self, converter: ASTextConverter) -> str:
        return converter.double_spawn_orb_convert(self)


class ASDisableAllySkills(ActiveSkill):
    skill_type = 214

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.turns = data[0]
        super().__init__(ms, ASBBuff('disable_skills', self.turns))

    def text(self, converter) -> str:
        return converter.ally_active_disable(self.turns)


class ASCreateUnmatchable(ActiveSkill):
    skill_type = 215

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.duration = data[0]
        self.orbs = binary_con(data[1])
        super().__init__(ms, ASBBuff('unmachable', self.duration,
                                     {'attributes': self.orbs}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.create_unmatchable(self)


class ASDelayAllySkills(ActiveSkill):
    skill_type = 218

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.min_turns = data[0]
        self.max_turns = data[0] or self.min_turns
        super().__init__(ms, ASBCustom('skill_charge', {'turns': [-self.max_turns, -self.min_turns]}))

    def text(self, converter) -> str:
        return converter.ally_active_delay(self.min_turns, self.max_turns)


class ASTimedEnemyAttrChange(ActiveSkill):
    skill_type = 224

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.turns = data[0]
        self.attribute = data[1]
        super().__init__(ms, ASBBuff('enemy_attribute_change', self.turns,
                                     {'attribute': self.attribute}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.change_enemies_attribute_convert(self)


class ASConditionalHPThreshold(ASConditional):
    skill_type = 225

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.lower_limit = data[0]
        self.upper_limit = data[1] or 100
        super().__init__(ms, ASBCustom('conditional',
                                       {'type': 'hp',
                                        'boundaries': [self.lower_limit, self.upper_limit]}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.conditional_hp_thresh(self)


class ASNailOrbSkyfall(ActiveSkill):
    skill_type = 226

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.duration = data[0]
        self.chance = mult(data[1])
        super().__init__(ms, ASBBuff('increase_skyfall', self.duration,
                                     {'percentage': self.chance,
                                      'attributes': [],
                                      'type': 'nail'}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.nail_orb_skyfall(self)


class ASLeaderSwapRightSub(ActiveSkill):
    skill_type = 227

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [])
        self.sub_slot = 4
        super().__init__(ms, ASBCustom('leader_swap', {'position': 4}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.lead_swap_sub(self)


class ASTeamCompositionBuff(ActiveSkill):
    skill_type = 228

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0])
        self.duration = data[0]
        self.attributes = binary_con(data[1])
        self.types = binary_con(data[2])
        self.atk_boost = mult(data[3])
        self.rcv_boost = mult(data[4])
        super().__init__(ms, ASBBuff('stat_mult', self.duration,
                                     {'stats': (1.0, self.atk_boost, self.rcv_boost),
                                      'per': {'attributes': self.attributes,
                                              'types': self.types,
                                              'awakenings': []}}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.composition_buff(self)


class ASTeamTargetStatBuff(ActiveSkill):
    skill_type = 230

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1, 100])
        self.duration = data[0]
        self.target = data[1]
        self.atk_mult = mult(data[2])
        super().__init__(ms, ASBBuff('stat_mult', self.duration,
                                     {'stats': (1.0, self.atk_mult, 1.0),
                                      'target': {
                                          'attributes': [],
                                          'types': [],
                                          'target_bitmap': self.target}}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.team_target_stat_change(self)


class ASAwokenSkillStatBoost(ActiveSkill):
    skill_type = 231

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1, 0, 0, 0, 0, 0, 0, 0])
        self.duration = data[0]
        self.awakenings = data[1:4]
        self.unknown_4 = data[4]
        self.unknown_5 = data[5]
        self.atk_per = mult(data[6])
        self.rcv_per = mult(data[7])
        super().__init__(ms, ASBBuff('stat_mult', self.duration,
                                     {'stats': (1.0, self.atk_per, self.rcv_per),
                                      'per': {'attributes': [],
                                              'types': [],
                                              'awakenings': self.awakenings}}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.awakening_stat_boost_convert(self)


class ASEvolvingSkill(ASCompound):
    skill_type = 232
    compound_skill_type = 2
    multipart_type = 'evolving'

    def text(self, converter: ASTextConverter) -> str:
        return converter.evolving_active(self)


class ASLoopingEvolvingSkill(ASCompound):
    skill_type = 233
    compound_skill_type = 3
    multipart_type = 'looping'

    def text(self, converter: ASTextConverter) -> str:
        return converter.looping_evolving_active(self)


class ASConditionalFloorThreshold(ASConditional):
    skill_type = 234

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 9999])
        self.lower_limit = data[0]
        self.upper_limit = data[1] or 9999
        super().__init__(ms, ASBCustom('conditional',
                                       {'type': 'floor',
                                        'boundaries': [self.lower_limit, self.upper_limit]}),
                         needs_context=True)

    def text(self, converter: ASTextConverter, context: Optional[Iterable[ActiveSkill]] = None) \
            -> str:
        return converter.conditional_floor_thresh(self, context)


class ASRandomChangeMonster(ActiveSkill):
    skill_type = 236

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [])
        super().__init__(ms, ASBCustom('transform', {'monsters': data}), transform_ids=Counter(data))

    def text(self, converter: ASTextConverter) -> str:
        return converter.random_change_monster(self)


class ASHPBoostMonster(ActiveSkill):
    skill_type = 237

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.duration = data[0]
        self.hp = mult(data[1])
        super().__init__(ms, ASBBuff('stat_mult', self.duration,
                                     {'stats': (self.hp, 1.0, 1.0)}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.hp_boost(self)


class ASInflictES(ActiveSkill):
    skill_type = 1000

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.selector_type = data[0]
        self.players = binary_con(data[1])
        self.es_ref = data[2]
        super().__init__(ms, ASBCustom('inflict_es',
                                       {'selector': self.selector_type,
                                        'players': self.players,
                                        'esid': self.es_ref}))

    def text(self, converter: ASTextConverter) -> str:
        return converter.inflict_es(self)


def convert(skill_list: List[MonsterSkill]):
    skill_type_to_constructor = {}
    for skill in ALL_ACTIVE_SKILLS:
        if skill.skill_type in skill_type_to_constructor:
            raise ValueError('Unexpected duplicate skill_type: ' + str(skill.skill_type))
        skill_type_to_constructor[skill.skill_type] = skill

    results = {}
    for s in skill_list:
        skill_constructor = None

        if s.skill_type == 0 and len(s.data) > 1 and s.data[1] != 0:
            # This is an annoying special case
            skill_constructor = ASMultiplierMultiTargetAttrNuke
        elif s.skill_type in skill_type_to_constructor:
            skill_constructor = skill_type_to_constructor[s.skill_type]

        if skill_constructor is not None:
            results[s.skill_id] = skill_constructor(s)

    # Fill in MultiSkills
    for s in results.values():
        if not isinstance(s, ASMultiPart):
            continue

        for p_id in s.child_ids:
            if p_id not in results:
                human_fix_logger.error('Failed to look up multi-part active skill id: %d', p_id)
                continue
            p_skill = results[p_id]
            s.child_skills.append(p_skill)

    return list(results.values())


ALL_ACTIVE_SKILLS = [
    ASFixedMultiTargetAttrNuke,
    ASMultiplierSelfAttrSingleTargetNuke,
    ASDamageReduction,
    ASPoisonEnemies,
    ASFreeOrbMovement,
    ASGravity,
    ASHpRecoverFromRcv,
    ASHpRecoverStatic,
    ASOneAttrtoOneAttr,
    ASOrbRefresh,
    ASDelay,
    ASDefenseBreak,
    ASTwoAttrtoOneTwoAttr,
    ASDamageVoid,
    ASAtkBasedNuke,
    ASSingleTargetTeamAttrNuke,
    ASAttrOnAttrNuke,
    ASAttrBurst,
    ASMassAttack,
    ASOrbEnhance,
    ASTrueDamageNuke,
    ASTrueDamageNukeAll,
    ASAttrMassAttack,
    ASAttrRandomNuke,
    ASCounterattack,
    ASBoardChange,
    ASHpConditionalTargetNuke,
    ASHpConditionalMassNuke,
    ASTargetNukeWithHpPenalty,
    ASMassNukeWithHpPenalty,
    ASTypeBurst,
    ASAttrBurstMultiPart,
    ASBicolorOrbEnhance,
    ASTypeBurstNew,
    ASLeaderSwap,
    ASLowHpConditionalAttrDamageBoost,
    ASMiniNukeandHpRecovery,
    ASMultiPartSkill,
    ASHpRecoveryandBindClear,
    ASRandomSkill,
    ASIncreasedSkyfallChance,
    ASColumnOrbChange,
    ASRowOrbChange,
    ASIncreasedOrbMovementTime,
    ASOrbEnhanceNew,
    ASRandomLocationOrbSpawn,
    ASRandomLocationDoubleOrbSpawn,
    ASAttributeChange,
    ASHpMultiplierNuke,
    ASAttrNukeOfAttrTwoAtk,
    ASHpRecovery,
    ASHaste,
    ASOrbLock,
    ASEnemyAttrChange,
    ASThreeAttrtoOneAttr,
    ASAwokenSkillBurst,
    ASAwokenSkillBurst2,
    ASAddAdditionalCombos,
    ASTrueGravity,
    ASOrbLockRemoval,
    ASVoidDamageAbsorption,
    ASFixedPosConvertSomething,
    ASIncreasedEnhanceOrbSkyfall,
    ASNoSkyfallForXTurns,
    ASMultiLaserConvert,
    ASShowComboPath,
    ASAutoHealConvert,
    ASReduceVoidDamage,
    ASSuicide195,
    ASReduceDisableMatch,
    ASChangeMonster,
    ASSkyfallLock,
    ASSpawnSpinner,
    ASDisableAllySkills,
    ASCreateUnmatchable,
    ASDelayAllySkills,
    ASTimedEnemyAttrChange,
    ASConditionalHPThreshold,
    ASNailOrbSkyfall,
    ASLeaderSwapRightSub,
    ASTeamCompositionBuff,
    ASTeamTargetStatBuff,
    ASAwokenSkillStatBoost,
    ASEvolvingSkill,
    ASLoopingEvolvingSkill,
    ASConditionalFloorThreshold,
    ASInflictES,
    ASRandomChangeMonster,
    ASHPBoostMonster,
]
