import logging
from collections import OrderedDict, namedtuple
from typing import List

from pad.raw.skill import MonsterSkill
from pad.raw.skills.en.active_skill_text import EnASTextConverter as ASTextConverter

human_fix_logger = logging.getLogger('human_fix')


def cc(x): return x


def ccf(x): return float(x)


def multi(x): return x / 100


def multi2(x): return x / 100 if x != 0 else 1.0


def listify(x): return [x]


def list_con(x): return list(x)


def list_con_pos(x): return [i for i in x if i > 0]


def binary_con(x): return [] if x == -1 else [i for i, v in enumerate(str(bin(x))[:1:-1]) if v == '1']


def list_binary_con(x): return [b for i in x for b in binary_con(i)]


def atk_from_slice(x): return multi(x[2]) if 1 in x[:2] else 1.0


def rcv_from_slice(x): return multi(x[2]) if 2 in x[:2] else 1.0


def merge_defaults(inp, defaults):
    return list(inp) + defaults[len(inp):]


class ActiveSkill(object):
    skill_type = -1

    def __init__(self, ms: MonsterSkill):
        if self.skill_type != ms.skill_type:
            raise ValueError('Expected {} but got {}'.format(self.skill_type, ms.skill_type))
        self.skill_id = ms.skill_id

        self.name = ms.name
        self.raw_description = ms.clean_description
        self.raw_data = ms.data
        self.skill_type = ms.skill_type
        self.levels = ms.levels
        self.turn_max = ms.turn_max
        self.turn_min = ms.turn_min

    def text(self, converter: ASTextConverter) -> str:
        return '<unsupported>: {}'.format(self.raw_description)

    def full_text(self, converter: ASTextConverter) -> str:
        return self.text(converter) or ''


class ASMultiplierMultiTargetAttrNuke(ActiveSkill):
    # Do not add this to the ALL_SKILLS list! skill_type=0 can imply 'no skill'
    skill_type = 0

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.attribute = data[0]
        self.multiplier = multi(data[1])
        self.mass_attack = True
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.attr_nuke_convert(self)


class ASFixedMultiTargetAttrNuke(ActiveSkill):
    skill_type = 1

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1])
        self.attribute = data[0]
        self.damage = data[1]
        self.mass_attack = True
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.fixed_attr_nuke_convert(self)


class ASMultiplierSelfAttrSingleTargetNuke(ActiveSkill):
    skill_type = 2

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1, False])
        self.multiplier = multi(data[0])
        self.mass_attack = False
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.self_att_nuke_convert(self)


class ASDamageReduction(ActiveSkill):
    skill_type = 3

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1, 0])
        self.duration = data[0]
        self.shield = multi(data[1])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.shield_convert(self)


class ASPoisonEnemies(ActiveSkill):
    skill_type = 4

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1])
        self.multiplier = multi(data[0])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.poison_convert(self)


class ASFreeOrbMovement(ActiveSkill):
    skill_type = 5

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.duration = data[0]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.ctw_convert(self)


class ASGravity(ActiveSkill):
    skill_type = 6

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.percentage_hp = multi(data[0])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.gravity_convert(self)


class ASHpRecoverFromRcv(ActiveSkill):
    skill_type = 7

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.rcv_multiplier_as_hp = multi(data[0])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.heal_active_convert(self)


class ASHpRecoverStatic(ActiveSkill):
    skill_type = 8

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.hp = data[0]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.heal_active_convert(self)


class ASOneAttrtoOneAttr(ActiveSkill):
    skill_type = 9

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.from_attr = [data[0]]
        self.to_attr = [data[1]]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.random_orb_change_convert(self)


class ASOrbRefresh(ActiveSkill):
    skill_type = 10

    def text(self, converter: ASTextConverter) -> str:
        return converter.board_refresh(self)


class ASDelay(ActiveSkill):
    skill_type = 18

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.turns = data[0]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.delay_convert(self)


class ASDefenseBreak(ActiveSkill):
    skill_type = 19

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.duration = data[0]
        self.shield = multi(data[1])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.defense_reduction_convert(self)


class ASTwoAttrtoOneTwoAttr(ActiveSkill):
    skill_type = 20

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.from_attr = [data[0], data[2]]
        self.to_attr = [data[1], data[3]] if data[1] != data[3] else [data[1]]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.double_orb_convert(self)


class ASDamageVoid(ActiveSkill):
    skill_type = 21

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.duration = data[0]
        self.attribute = data[1]
        self.shield = multi(data[2])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.elemental_shield_convert(self)


class ASAtkBasedNuke(ActiveSkill):
    skill_type = 35

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.atk_multiplier = multi(data[0])
        self.recover_multiplier = multi(data[1])
        self.mass_attack = False
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.drain_attack_convert(self)


class ASSingleTargetTeamAttrNuke(ActiveSkill):
    skill_type = 37

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [])
        self.attribute = data[0]
        self.multiplier = multi(data[1])
        self.mass_attack = False
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.attr_nuke_convert(self)


class ASAttrOnAttrNuke(ActiveSkill):
    skill_type = 42

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 1])
        self.enemy_attribute = data[0]
        self.attack_attribute = data[1]
        self.damage = data[2]
        super().__init__(ms)

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
        self.multiplier = multi(data[2])
        self.atk = self.multiplier
        super().__init__(ms)

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
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.mass_attack_convert(self)


class ASOrbEnhance(ActiveSkill):
    skill_type = 52

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.orbs = [data[0]]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.enhance_convert(self)


class ASTrueDamageNuke(ActiveSkill):
    skill_type = 55

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.damage = data[0]
        self.mass_attack = False
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.laser_convert(self)


class ASTrueDamageNukeAll(ActiveSkill):
    skill_type = 56

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.damage = data[0]
        self.mass_attack = True
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.laser_convert(self)


class ASAttrMassAttack(ActiveSkill):
    skill_type = 58

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1, 1])
        self.attribute = data[0]
        self.minimum_multiplier = multi(data[1])
        self.maximum_multiplier = multi(data[2])
        self.mass_attack = True
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.random_nuke_convert(self)


class ASAttrRandomNuke(ActiveSkill):
    skill_type = 59

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1, 1])
        self.attribute = data[0]
        self.minimum_multiplier = multi(data[1])
        self.maximum_multiplier = multi(data[2])
        self.mass_attack = False
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.random_nuke_convert(self)


class ASCounterattack(ActiveSkill):
    skill_type = 60

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1, 1, 0])
        self.duration = data[0]
        self.multiplier = multi(data[1])
        self.attribute = data[2]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.counterattack_convert(self)


class ASBoardChange(ActiveSkill):
    skill_type = 71

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [])
        self.from_attr = list(range(10))
        self.to_attr = [v for v in data if v != -1]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.board_change_convert(self)


class ASHpConditionalTargetNuke(ActiveSkill):
    skill_type = 84

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1, 1, 0])
        self.attribute = data[0]
        self.minimum_multiplier = multi(data[1])
        self.maximum_multiplier = multi(data[2])
        self.hp_remaining = multi(data[3])
        self.mass_attack = False
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.suicide_random_nuke_convert(self)


class ASHpConditionalMassNuke(ActiveSkill):
    skill_type = 85

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 1, 1, 0])
        self.attribute = data[0]
        self.minimum_multiplier = multi(data[1])
        self.maximum_multiplier = multi(data[2])
        self.hp_remaining = multi(data[3])
        self.mass_attack = True
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.suicide_random_nuke_convert(self)


class ASTargetNukeWithHpPenalty(ActiveSkill):
    skill_type = 86

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.attribute = data[0]
        self.damage = data[1]
        self.hp_remaining = multi(data[3])
        self.mass_attack = False
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.suicide_nuke_convert(self)


class ASMassNukeWithHpPenalty(ActiveSkill):
    skill_type = 87

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.attribute = data[0]
        self.damage = data[1]
        self.hp_remaining = multi(data[3])
        self.mass_attack = True
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.suicide_nuke_convert(self)


class ASTypeBurst(ActiveSkill):
    skill_type = 88

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.duration = data[0]
        self.types = [data[1]]
        self.multiplier = multi(data[2])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.type_attack_boost_convert(self)


class ASAttrBurstMultiPart(ActiveSkill):
    skill_type = 90

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0])
        self.duration = data[0]
        self.attributes = data[1:3]
        self.multiplier = multi(data[3])
        self.rcv_boost = False

        if 5 in self.attributes:
            self.rcv_boost = True
            self.attributes.remove(5)

        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        if self.duration == 0:
            return ''
        return converter.attribute_attack_boost_convert(self)


class ASBicolorOrbEnhance(ActiveSkill):
    skill_type = 91

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [])
        self.orbs = data[0:2]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.enhance_convert(self)


class ASTypeBurstNew(ActiveSkill):
    skill_type = 92

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 1])
        self.duration = data[0]
        self.types = data[1:3]
        self.multiplier = multi(data[3])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.type_attack_boost_convert(self)


class ASLeaderSwap(ActiveSkill):
    skill_type = 93

    def __init__(self, ms: MonsterSkill):
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.leader_swap(self)


class ASLowHpConditionalAttrDamageBoost(ActiveSkill):
    skill_type = 110

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 1, 1])
        self.mass_attack = data[0] == 0
        self.attribute = data[1]
        self.high_multiplier = multi(data[2])
        self.low_multiplier = multi(data[3])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.grudge_strike_convert(self)


class ASMiniNukeandHpRecovery(ActiveSkill):
    skill_type = 115

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.attribute = data[0]
        self.atk_multiplier = multi(data[1])
        self.recover_multiplier = multi(data[2])
        self.mass_attack = False
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.drain_attr_attack_convert(self)


class PartWithTextAndCount(object):
    def __init__(self, act: ActiveSkill, text: str):
        self.act = act
        self.text = text
        self.repeat = 1

    def full_text(self, converter: ASTextConverter):
        return self.text if self.repeat == 1 else converter.fmt_repeated(self.text, self.repeat)


class ASMultiPartSkill(ActiveSkill):
    skill_type = 116

    def __init__(self, ms: MonsterSkill):
        self.child_ids = ms.data
        self.child_skills = []
        super().__init__(ms)

    @property
    def parts(self):
        return self.child_skills

    def text(self, converter: ASTextConverter) -> str:
        text_to_item = OrderedDict()
        for p in self.parts:
            p_text = p.text(converter)
            if p_text in text_to_item:
                text_to_item[p_text].repeat += 1
            else:
                text_to_item[p_text] = PartWithTextAndCount(p, p_text)

        return converter.two_part_active(map(lambda x: x.full_text(converter), text_to_item.values()))


class ASHpRecoveryandBindClear(ActiveSkill):
    skill_type = 117

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0])
        self.card_bind = data[0]
        self.rcv_multiplier_as_hp = multi(data[1])
        self.hp = data[2]
        self.percentage_max_hp = multi(data[3])
        self.awoken_bind = data[4]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.heal_active_convert(self)


class ASRandomSkill(ActiveSkill):
    skill_type = 118

    def __init__(self, ms: MonsterSkill):
        self.random_skill_ids = ms.data
        self.random_skills = []
        super().__init__(ms)

    @property
    def parts(self):
        return sum([s.parts if isinstance(s, ASMultiPartSkill) else [s]
                    for s in self.random_skills], [])

    def text(self, converter: ASTextConverter) -> str:
        return converter.random_skill(self)


class ASIncreasedSkyfallChance(ActiveSkill):
    skill_type = 126

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.orbs = binary_con(data[0])
        self.duration = data[1]
        self.max_duration = data[2]
        self.percentage = multi(data[3])
        super().__init__(ms)

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
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.column_change_convert(self)


class ASRowOrbChange(ActiveSkill):
    skill_type = 128

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [])
        # TODO: simplify this
        self.rows = [OrbLine(int(i), binary_con(orbs)) for indices, orbs in
                     zip(data[::2], data[1::2]) for i in binary_con(indices)]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.row_change_convert(self)


class ASIncreasedOrbMovementTime(ActiveSkill):
    skill_type = 132

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.duration = data[0]
        self.static = data[1] / 10
        self.percentage = multi(data[2])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.move_time_buff_convert(self)


class ASOrbEnhanceNew(ActiveSkill):
    skill_type = 140

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.orbs = binary_con(data[0])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.enhance_convert(self)


class ASRandomLocationOrbSpawn(ActiveSkill):
    skill_type = 141

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.amount = data[0]
        self.orbs = binary_con(data[1])
        self.excluding_orbs = binary_con(data[2])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.spawn_orb_convert(self)


class ASAttributeChange(ActiveSkill):
    skill_type = 142

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.duration = data[0]
        self.attribute = data[1]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.attribute_change_convert(self)


class ASHpMultiplierNuke(ActiveSkill):
    skill_type = 143

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.multiplier = multi(data[0])
        self.attribute = data[1]
        # Note; another slot must contain the attribute, since this is a fixed nuke.
        self.mass_attack = True
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.hp_nuke_convert(self)


class ASAttrNukeOfAttrTwoAtk(ActiveSkill):
    skill_type = 144

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.team_attributes = binary_con(data[0])
        self.multiplier = multi(data[1])
        self.mass_attack = data[2] == 0
        self.attack_attribute = data[3]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.attack_attr_x_team_atk_convert(self)


class ASHpRecovery(ActiveSkill):
    skill_type = 145

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.team_rcv_multiplier_as_hp = multi(data[0])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.heal_active_convert(self)


class ASHaste(ActiveSkill):
    skill_type = 146

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.turns = data[0]
        self.max_turns = data[1] or self.turns
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.haste_convert(self)


class ASOrbLock(ActiveSkill):
    skill_type = 152

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.orbs = binary_con(data[0])
        self.count = data[1]  # This can be 42/99 (both mean 'all') or a fixed number
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.lock_convert(self)


class ASEnemyAttrChange(ActiveSkill):
    skill_type = 153

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.attribute = data[0]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.change_enemies_attribute_convert(self)


class ASThreeAttrtoOneAttr(ActiveSkill):
    skill_type = 154

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.from_attr = binary_con(data[0])
        self.to_attr = binary_con(data[1])
        super().__init__(ms)

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
            self.amount_per = multi(data[5])
        super().__init__(ms)

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
            self.amount_per = data[7] / 100
        elif self.toggle == 3:
            self.amount_per = multi(data[7])
        super().__init__(ms)

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
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.extra_combo_convert(self)


class ASTrueGravity(ActiveSkill):
    skill_type = 161

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.percentage_max_hp = multi(data[0])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.true_gravity_convert(self)


class ASOrbLockRemoval(ActiveSkill):
    skill_type = 172

    def __init__(self, ms: MonsterSkill):
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.unlock_all_orbs(self)


class ASVoidDamageAbsorption(ActiveSkill):
    skill_type = 173

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.duration = data[0]
        self.attribute_absorb = bool(data[1])
        self.damage_absorb = bool(data[3])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.absorb_mechanic_void_convert(self)


class ASFixedPosConvertSomething(ActiveSkill):
    skill_type = 176

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 0])
        self.row_pos_1 = binary_con(data[0])
        self.row_pos_2 = binary_con(data[1])
        self.row_pos_3 = binary_con(data[2])
        self.row_pos_4 = binary_con(data[3])
        self.row_pos_5 = binary_con(data[4])
        self.attribute = data[5]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.fixed_pos_convert(self)


class ASAutoHealConvert(ActiveSkill):
    skill_type = 179

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, None, 0, 0, 0])
        self.duration = data[0]
        self.percentage_max_hp = multi(data[2])
        self.card_bind = data[3]
        self.awoken_bind = data[4]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.auto_heal_convert(self)


class ASIncreasedEnhanceOrbSkyfall(ActiveSkill):
    skill_type = 180

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.duration = data[0]
        self.percentage_increase = multi(data[1])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.enhance_skyfall_convert(self)


class ASNoSkyfallForXTurns(ActiveSkill):
    skill_type = 184

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.duration = data[0]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.no_skyfall_convert(self)


class ASMultiLaserConvert(ActiveSkill):
    skill_type = 188

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.damage = data[0]
        self.mass_attack = False
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.multi_hit_laser_convert(self)


class ASShowComboPath(ActiveSkill):
    skill_type = 189

    def __init__(self, ms: MonsterSkill):
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.unlock_board_path_toragon(self)


class ASReduceVoidDamage(ActiveSkill):
    skill_type = 191

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.duration = data[0]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.void_mechanic_convert(self)


class ASSuicide195(ActiveSkill):
    skill_type = 195

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.hp_remaining = multi(data[0])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.suicide_convert(self)


class ASReduceDisableMatch(ActiveSkill):
    skill_type = 196

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.duration = data[0]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.match_disable_convert(self)


class ASChangeMonster(ActiveSkill):
    skill_type = 202

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.change_to = data[0]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.change_monster(self)


class ASSkyfallLock(ActiveSkill):
    skill_type = 205

    def __init__(self, ms: MonsterSkill):
        # The '1' in slot 0 is suspicious but it seems set for everything so it changes nothing.
        data = merge_defaults(ms.data, [1, 1])
        self.orbs = binary_con(data[0])
        self.duration = data[1]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.skyfall_lock(self)


class ASSpawnSpinner(ActiveSkill):
    skill_type = 207

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1, 100, 0, 0, 0, 0, 0, 1])
        # Only one example of this so far, so these are all just guesses
        self.turns = data[0]
        self.speed = multi(data[1])
        self.count = data[7]
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.spawn_spinner(self.turns, self.speed, self.count)


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
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.double_spawn_orb_convert(self)


class ASDisableAllySkills(ActiveSkill):
    skill_type = 214

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.turns = data[0]
        super().__init__(ms)

    def text(self, converter) -> str:
        return converter.ally_active_disable(self.turns)


class ASCreateUnmatchable(ActiveSkill):
    skill_type = 215

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.duration = data[0]
        self.orbs = binary_con(data[1])
        super().__init__(ms)

    def text(self, converter: ASTextConverter) -> str:
        return converter.create_unmatchable(self)


class ASDelayAllySkills(ActiveSkill):
    skill_type = 218

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.turns = data[0]
        super().__init__(ms)

    def text(self, converter) -> str:
        return converter.ally_active_delay(self.turns)


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

    # Fills in ASMultiPartSkills
    for s in results.values():
        if not isinstance(s, ASMultiPartSkill):
            continue

        for p_id in s.child_ids:
            if p_id not in results:
                human_fix_logger.error('failed to look up multipart active skill id: %d', p_id)
                continue
            p_skill = results[p_id]
            s.child_skills.append(p_skill)

    # Fills in ASRandomSkill
    for s in results.values():
        if not isinstance(s, ASRandomSkill):
            continue

        for p_id in s.random_skill_ids:
            if p_id not in results:
                human_fix_logger.error('failed to look up random leader skill id: %d', p_id)
                continue
            p_skill = results[p_id]
            s.random_skills.append(p_skill)
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
]
