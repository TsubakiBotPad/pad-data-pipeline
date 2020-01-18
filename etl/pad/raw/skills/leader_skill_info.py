import logging
from typing import List, Optional
from functools import reduce

from pad.raw.skill import MonsterSkill
from pad.raw.skills.leader_skill_conversion import LSTextConverter
from pad.raw.skills.en.skill_common import *

human_fix_logger = logging.getLogger('human_fix')


def mult(x):
    return x / 100


def multi_floor(x):
    return x / 100 if x != 0 else 1.0


# TODO: clean all these things up
def atk_from_slice(x):
    return x[2] / 100 if 1 in x[:2] else 1.0


def rcv_from_slice(x):
    return x[2] / 100 if 2 in x[:2] else 1.0


def binary_con(x):
    return [i for i, v in enumerate(str(bin(x))[:1:-1]) if v == '1']


def list_binary_con(x):
    return [b for i in x for b in binary_con(i)]


def list_con_pos(x):
    return [i for i in x if i > 0]


def merge_defaults(input, defaults):
    return list(input) + defaults[len(input):]


class LeaderSkill(object):
    skill_type = -1

    def __init__(self, skill_type: int, ms: MonsterSkill,
                 hp: float = 1, atk: float = 1, rcv: float = 1, shield: float = 0):
        if skill_type != ms.skill_type:
            raise ValueError('Expected {} but got {}'.format(skill_type, ms.skill_type))
        self.skill_id = ms.skill_id
        self.skill_type = ms.skill_type
        if not hasattr(self, 'tags'): self.tags = []
        self.name = ms.name
        self.raw_description = ms.clean_description
        self._hp = round(hp, 2)
        self._atk = round(atk, 2)
        self._rcv = round(rcv, 2)
        self._shield = round(shield, 2)

    @property
    def hp(self):
        return self._hp

    @property
    def atk(self):
        return self._atk

    @property
    def rcv(self):
        return self._rcv

    @property
    def shield(self):
        return self._shield

    @property
    def parts(self):
        return [self]

    def text(self, converter: LSTextConverter) -> str:
        return '<unsupported>: {}'.format(self.raw_description)

    def full_text(self, converter: LSTextConverter) -> str:
        text = self.text(converter) or ''
        return converter.full_text(self.text(converter), self.tags)


class LSAttrAtkBoost(LeaderSkill):
    skill_type = 11

    def __init__(self, ms: MonsterSkill):
        self.attributes = [ms.data[0]]
        atk = mult(ms.data[1])
        super().__init__(11, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSBonusAttack(LeaderSkill):
    skill_type = 12

    def __init__(self, ms: MonsterSkill):
        self.multiplier = mult(ms.data[0])
        super().__init__(12, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.after_attack_convert(self)


class LSAutoheal(LeaderSkill):
    skill_type = 13

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.multiplier = mult(data[0])
        super().__init__(13, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.heal_on_convert(self)


class LSResolve(LeaderSkill):
    skill_type = 14

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.threshold = mult(data[0])
        super().__init__(14, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.resolve_convert(self)


class LSMovementTimeIncrease(LeaderSkill):
    skill_type = 15

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.time = mult(data[0])
        super().__init__(15, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.bonus_time_convert(self)


class LSDamageReduction(LeaderSkill):
    skill_type = 16

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        shield = mult(data[0])
        super().__init__(16, ms, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSAttrDamageReduction(LeaderSkill):
    skill_type = 17

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.reduction_attributes = [data[0]]
        shield = mult(data[1])
        super().__init__(17, ms, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTypeAtkBoost(LeaderSkill):
    skill_type = 22

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.types = [data[0]]
        atk = mult(data[1])
        super().__init__(22, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTypeHpBoost(LeaderSkill):
    skill_type = 23

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.types = [data[0]]
        hp = mult(data[1])
        super().__init__(23, ms, hp=hp)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTypeRcvBoost(LeaderSkill):
    skill_type = 24

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.types = [data[0]]
        rcv = mult(data[1])
        super().__init__(24, ms, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSStaticAtkBoost(LeaderSkill):
    skill_type = 26

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100])
        atk = mult(data[0])
        super().__init__(26, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSAttrAtkRcvBoost(LeaderSkill):
    skill_type = 28

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.attributes = [data[0]]
        boost = mult(data[1])
        super().__init__(28, ms, atk=boost, rcv=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSAllStatBoost(LeaderSkill):
    skill_type = 29

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.attributes = [data[0]]
        boost = mult(data[1])
        super().__init__(29, ms, hp=boost, atk=boost, rcv=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTwoTypeHpBoost(LeaderSkill):
    skill_type = 30

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100])
        self.types = data[0:2]
        hp = mult(data[2])
        super().__init__(30, ms, hp=hp)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTwoTypeAtkBoost(LeaderSkill):
    skill_type = 31

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100])
        self.types = data[0:2]
        atk = mult(data[2])
        super().__init__(31, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTaikoDrum(LeaderSkill):
    skill_type = 33

    def __init__(self, ms: MonsterSkill):
        super().__init__(33, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.taiko_convert(converter)


class LSTwoAttrDamageReduction(LeaderSkill):
    skill_type = 36

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.reduction_attributes = data[0:2]
        shield = mult(ms.data[2])
        super().__init__(36, ms, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSLowHpShield(LeaderSkill):
    skill_type = 38

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.threshold = mult(data[0])
        self.threshold_type = ThresholdType.BELOW
        shield = mult(data[2])
        super().__init__(38, ms, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LSLowHpAtkOrRcvBoost(LeaderSkill):
    skill_type = 39

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.threshold = mult(data[0])
        self.threshold_type = ThresholdType.BELOW
        atk = atk_from_slice(data[1:4])
        rcv = rcv_from_slice(data[1:4])
        super().__init__(39, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LSTwoAttrAtkBoost(LeaderSkill):
    skill_type = 40

    def __init__(self, ms: MonsterSkill):
        self.attributes = ms.data[0:2]
        atk = mult(ms.data[2])
        super().__init__(40, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSCounterattack(LeaderSkill):
    skill_type = 41

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.chance = mult(data[0])
        self.multiplier = mult(data[1])
        self.attributes = [data[2]]
        super().__init__(41, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.counter_attack_convert(self)


class LSHighHpShield(LeaderSkill):
    skill_type = 43

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.threshold = mult(data[0])
        self.threshold_type = ThresholdType.ABOVE
        self.chance = mult(data[1])
        shield = mult(data[2])
        super().__init__(43, ms, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.random_shield_threshold_stats(self)


class LSHighHpAtkBoost(LeaderSkill):
    skill_type = 44

    def __init__(self, ms: MonsterSkill):
        self.threshold = mult(ms.data[0])
        self.threshold_type = ThresholdType.ABOVE
        atk = atk_from_slice(ms.data[1:4])
        rcv = rcv_from_slice(ms.data[1:4])
        super().__init__(44, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LSAttrAtkHpBoost(LeaderSkill):
    skill_type = 45

    def __init__(self, ms: MonsterSkill):
        self.attributes = [ms.data[0]]
        boost = mult(ms.data[1])
        hp = boost
        atk = boost
        super().__init__(45, ms, hp=hp, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTwoAttrHpBoost(LeaderSkill):
    skill_type = 46

    def __init__(self, ms: MonsterSkill):
        self.attributes = ms.data[0:2]
        hp = mult(ms.data[2])
        super().__init__(46, ms, hp=hp)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSAttrHpBoost(LeaderSkill):
    skill_type = 48

    def __init__(self, ms: MonsterSkill):
        self.attributes = [ms.data[0]]
        hp = mult(ms.data[1])
        super().__init__(48, ms, hp=hp)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSAttrRcvBoost(LeaderSkill):
    skill_type = 49

    def __init__(self, ms: MonsterSkill):
        self.attributes = [ms.data[0]]
        rcv = mult(ms.data[1])
        super().__init__(49, ms, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSEggDropRateBoost(LeaderSkill):
    skill_type = 53

    def __init__(self, ms: MonsterSkill):
        self.multiplier = mult(ms.data[0])
        super().__init__(53, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.egg_drop_convert(self)


class LSCoinDropBoost(LeaderSkill):
    skill_type = 54

    def __init__(self, ms: MonsterSkill):
        self.multiplier = mult(ms.data[0])
        super().__init__(54, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.coin_drop_convert(self)


class LSRainbow(LeaderSkill):
    skill_type = 61

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0, 0])
        self.match_attributes = binary_con(data[0])
        self.min_attr = data[1]
        self.min_atk = mult(data[2])
        self.atk_step = mult(data[3])
        self.max_attr = data[4] or len(self.match_attributes)

        if self.atk_step == 0:
            self.max_attr = self.min_attr
        elif self.max_attr < self.min_attr:
            self.max_attr = self.min_attr + self.max_attr
        elif (self.max_attr + self.min_attr) <= len(self.match_attributes):
            self.max_attr = self.min_attr + self.max_attr

        self.max_atk = self.min_atk + self.atk_step * (self.max_attr - self.min_attr)

        super().__init__(61, ms, atk=self.max_atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.attribute_match_convert(self)


class LSTypeHpAtkBoost(LeaderSkill):
    skill_type = 62

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[0]]
        boost = mult(data[1])
        super().__init__(62, ms, hp=boost, atk=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTypeHpRcvBoost(LeaderSkill):
    skill_type = 63

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[0]]
        boost = mult(data[1])
        super().__init__(63, ms, hp=boost, rcv=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTypeAtkRcvBoost(LeaderSkill):
    skill_type = 64

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[0]]
        boost = mult(data[1])
        super().__init__(64, ms, atk=boost, rcv=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTypeAllStatBoost(LeaderSkill):
    skill_type = 65

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[0]]
        boost = mult(data[1])
        super().__init__(65, ms, hp=boost, atk=boost, rcv=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSComboFlatMultiplier(LeaderSkill):
    skill_type = 66

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.min_combos = data[0]
        atk = mult(data[1])
        super().__init__(66, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.combo_match_convert(self)


class LSAttrHpRcvBoost(LeaderSkill):
    skill_type = 67

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        boost = mult(data[1])
        super().__init__(67, ms, hp=boost, rcv=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSAttrTypeAtkBoost(LeaderSkill):
    skill_type = 69

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        self.types = [data[1]]
        atk = mult(data[2])
        super().__init__(69, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSAttrTypeHpAtkBoost(LeaderSkill):
    skill_type = 73

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        self.types = [data[1]]
        boost = mult(data[2])
        super().__init__(73, ms, hp=boost, atk=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSAttrTypeAtkRcvBoost(LeaderSkill):
    skill_type = 75

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        self.types = [data[1]]
        boost = mult(data[2])
        super().__init__(75, ms, atk=boost, rcv=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSAttrTypeAllStatBoost(LeaderSkill):
    skill_type = 76

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        self.types = [data[1]]
        boost = mult(data[2])
        super().__init__(76, ms, hp=boost, atk=boost, rcv=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTwoTypeHpAtkBoost(LeaderSkill):
    skill_type = 77

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = data[0:2]
        boost = mult(data[2])
        super().__init__(77, ms, hp=boost, atk=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTwoTypeAtkRcvBoost(LeaderSkill):
    skill_type = 79

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = data[0:2]
        boost = mult(data[2])
        super().__init__(79, ms, atk=boost, rcv=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSLowHpConditionalAttrAtkBoost(LeaderSkill):
    skill_type = 94

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.threshold_type = ThresholdType.BELOW
        self.threshold = mult(data[0])
        self.attributes = [data[1]]
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(94, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LSLowHpConditionalTypeAtkBoost(LeaderSkill):
    skill_type = 95

    def __init__(self, ms: MonsterSkill):
        self.threshold_type = ThresholdType.BELOW
        data = ms.data
        self.threshold = mult(data[0])
        self.types = [data[1]]
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(95, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LSHighHpConditionalAttrAtkBoost(LeaderSkill):
    skill_type = 96

    def __init__(self, ms: MonsterSkill):
        self.threshold_type = ThresholdType.ABOVE
        data = ms.data
        self.threshold = mult(data[0])
        self.attributes = [data[1]]
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(96, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LSHighHpConditionalTypeAtkBoost(LeaderSkill):
    skill_type = 97

    def __init__(self, ms: MonsterSkill):
        self.threshold_type = ThresholdType.ABOVE
        data = ms.data
        self.threshold = mult(data[0])
        self.types = [data[1]]
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(97, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LSComboScaledMultiplier(LeaderSkill):
    skill_type = 98

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 0, 0])
        self.min_combos = data[0]
        self.min_atk = mult(data[1])
        self.atk_step = mult(data[2])
        self.max_combos = data[3] or self.min_combos
        self.max_atk = self.min_atk + self.atk_step * (self.max_combos - self.min_combos)
        super().__init__(98, ms, atk=self.max_atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.combo_match_convert(self)


class LSSkillActivationAtkRcvBoost(LeaderSkill):
    skill_type = 100

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        atk = atk_from_slice(data[0:4])
        rcv = rcv_from_slice(data[0:4])
        super().__init__(100, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.skill_used_convert(self)


class LSAtkBoostWithExactCombos(LeaderSkill):
    skill_type = 101

    def __init__(self, ms: MonsterSkill):
        self.combos = ms.data[0]
        atk = mult(ms.data[1])
        super().__init__(101, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.exact_combo_convert(self)


class LSComboFlatAtkRcvBoost(LeaderSkill):
    skill_type = 103

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.min_combos = data[0]
        atk = atk_from_slice(data[1:4])
        rcv = rcv_from_slice(data[1:4])
        super().__init__(103, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.combo_match_convert(self)


class LSComboFlatMultiplierAttrAtkBoost(LeaderSkill):
    skill_type = 104

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.min_combos = data[0]
        self.attributes = binary_con(data[1])
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(104, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.combo_match_convert(self)


class LSReducedRcvAtkBoost(LeaderSkill):
    skill_type = 105

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        rcv = mult(data[0])
        atk = mult(data[1])
        super().__init__(105, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSReducedHpAtkBoost(LeaderSkill):
    skill_type = 106

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        hp = mult(data[0])
        atk = mult(data[1])
        super().__init__(106, ms, hp=hp, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSHpReduction(LeaderSkill):
    skill_type = 107

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        hp = mult(data[0])
        super().__init__(107, ms, hp=hp)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSReducedHpTypeAtkBoost(LeaderSkill):
    skill_type = 108

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[1]]
        hp = mult(data[0])
        atk = mult(data[2])
        super().__init__(108, ms, hp=hp, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_type_atk_all_hp_convert(self)


class LSBlobFlatAtkBoost(LeaderSkill):
    skill_type = 109

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.match_attributes = binary_con(data[0])
        self.min_count = data[1]
        atk = mult(data[2])
        super().__init__(109, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.mass_match_convert(self)


class LSTwoAttrHpAtkBoost(LeaderSkill):
    skill_type = 111

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = data[0:2]
        boost = mult(data[2])
        super().__init__(111, ms, hp=boost, atk=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSTwoAttrAllStatBoost(LeaderSkill):
    skill_type = 114

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = data[0:2]
        boost = mult(data[2])
        super().__init__(114, ms, hp=boost, atk=boost, rcv=boost)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSBlobScalingAtkBoost(LeaderSkill):
    skill_type = 119

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0, 0])
        self.match_attributes = binary_con(data[0])
        self.min_count = data[1]
        self.min_atk = mult(data[2])
        self.atk_step = mult(data[3])
        self.max_count = data[4]
        self.max_atk = self.min_atk + self.atk_step * (self.max_count - self.min_count)
        super().__init__(119, ms, atk=self.max_atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.mass_match_convert(self)


class LSAttrOrTypeStatBoost(LeaderSkill):
    skill_type = 121

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 100])
        self.attributes = binary_con(data[0])
        self.types = binary_con((data[1]))
        hp = multi_floor(data[2])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        super().__init__(121, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSLowHpConditionalAttrTypeAtkRcvBoost(LeaderSkill):
    skill_type = 122

    def __init__(self, ms: MonsterSkill):
        self.threshold_type = ThresholdType.BELOW
        data = ms.data
        self.threshold = mult(data[0])
        self.attributes = binary_con((data[1]))
        self.types = binary_con((data[2]))
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4]) if len(data) > 4 else 1
        super().__init__(122, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LSHighHpConditionalAttrTypeAtkRcvBoost(LeaderSkill):
    skill_type = 123

    def __init__(self, ms: MonsterSkill):
        self.threshold_type = ThresholdType.ABOVE
        data = ms.data
        self.threshold = mult(data[0])
        self.attributes = binary_con((data[1]))
        self.types = binary_con((data[2]))
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4]) if len(data) > 4 else 1
        super().__init__(123, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LSAttrComboScalingAtkBoost(LeaderSkill):
    skill_type = 124

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 0, 100, 0])
        self.match_attributes = list_binary_con(data[0:5])
        self.min_combo = data[5]
        self.max_combo = len(self.match_attributes)
        self.min_atk = mult(data[6])
        self.atk_step = mult(data[7])
        self.max_atk = self.min_atk + self.atk_step * (self.max_combo - self.min_combo)
        super().__init__(124, ms, atk=self.max_atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.multi_attribute_match_convert(self)


class LSTeamUnitConditionalStatBoost(LeaderSkill):
    skill_type = 125

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 100, 100, 100])
        self.monster_ids = list_con_pos(data[0:5])
        hp = multi_floor(data[5])
        atk = multi_floor(data[6])
        rcv = multi_floor(data[7])
        super().__init__(125, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.team_build_bonus_convert(self)


class LSMultiAttrTypeStatBoost(LeaderSkill):
    skill_type = 129

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 100, 0, 0])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])
        self.reduction_attributes = binary_con(data[5])
        hp = multi_floor(data[2])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        shield = mult(data[6]) if len(data) > 6 else 0
        super().__init__(129, ms, hp=hp, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSLowHpAttrAtkStatBoost(LeaderSkill):
    skill_type = 130

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 100, 0, 0])
        self.threshold = mult(data[0])
        self.threshold_type = ThresholdType.BELOW
        self.attributes = binary_con(data[1])
        self.types = binary_con(data[2])
        self.reduction_attr = binary_con(data[5])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        shield = mult(data[6])
        super().__init__(130, ms, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LSHighHpAttrTypeStatBoost(LeaderSkill):
    skill_type = 131

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 100, 0, 0])
        self.threshold = mult(data[0])
        self.threshold_type = ThresholdType.ABOVE
        self.attributes = binary_con(data[1])
        self.types = binary_con(data[2])
        self.reduction_attr = binary_con(data[5])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        shield = mult(data[6])
        super().__init__(131, ms, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LSSkillUsedAttrTypeAtkRcvBoost(LeaderSkill):
    skill_type = 133

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])
        atk = multi_floor(data[2])
        rcv = multi_floor(data[3])
        super().__init__(133, ms, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.skill_used_convert(self)


class LSMultiAttrConditionalStatBoost(LeaderSkill):
    skill_type = 136

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 100, 100, 0, 100, 100, 100])
        self.attributes_1 = binary_con(data[0])
        self.hp_1 = multi_floor(data[1])
        self.atk_1 = multi_floor(data[2])
        self.rcv_1 = multi_floor(data[3])
        self.attributes_2 = binary_con(data[4])
        self.hp_2 = multi_floor(data[5])
        self.atk_2 = multi_floor(data[6])
        self.rcv_2 = multi_floor(data[7])
        hp = max(self.hp_1, 1) * max(self.hp_2, 1)
        atk = max(self.atk_1, 1) * max(self.atk_2, 1)
        rcv = max(self.rcv_1, 1) * max(self.rcv_2, 1)
        super().__init__(136, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.dual_passive_stat_convert(self)


class LSMultiTypeConditionalStatBoost(LeaderSkill):
    skill_type = 137

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 100, 100, 0, 100, 100, 100])
        self.types_1 = binary_con(data[0])
        self.hp_1 = multi_floor(data[1])
        self.atk_1 = multi_floor(data[2])
        self.rcv_1 = multi_floor(data[3])
        self.types_2 = binary_con(data[4])
        self.hp_2 = multi_floor(data[5])
        self.atk_2 = multi_floor(data[6])
        self.rcv_2 = multi_floor(data[7])
        hp = self.hp_1 * self.hp_2
        atk = self.atk_1 * self.atk_2
        rcv = self.rcv_1 * self.rcv_2
        super().__init__(137, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.dual_passive_stat_convert(self)


class LSTwoPartLeaderSkill(LeaderSkill):
    skill_type = 138

    def __init__(self, ms: MonsterSkill):
        self.child_ids = ms.data
        self.child_skills = []
        super().__init__(138, ms)

    @property
    def hp(self):
        v = 1
        for x in self.child_skills:
            v = v * x.hp
        return round(v, 2)

    @property
    def atk(self):
        v = 1
        for x in self.child_skills:
            v = v * x.atk
        return round(v, 2)

    @property
    def rcv(self):
        v = 1
        for x in self.child_skills:
            v = v * x.rcv
        return round(v, 2)

    @property
    def shield(self):
        v = 0
        for x in self.child_skills:
            v = 1 - (1 - v) * (1 - x.shield)
        return round(v, 2)

    @property
    def parts(self):
        return self.child_skills

    def text(self, converter: LSTextConverter) -> str:
        parts = map(lambda x: x.text(converter), self.parts)
        return converter.concat_list_semicolons(parts)

    def full_text(self, converter: LSTextConverter):
        tags = set(reduce(lambda agg, cs: agg + cs.tags, self.parts, []))
        parts = list(filter(None, [p.text(converter) for p in self.parts if p]))
        return converter.full_text(parts, tags)


class LSHpMultiConditionalAtkBoost(LeaderSkill):
    skill_type = 139

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 0, 0, 100, 100])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])

        self.threshold_1 = mult(data[2])
        self.threshold_type_1 = ThresholdType.BELOW if data[3] else ThresholdType.ABOVE
        self.atk_1 = mult(data[4])

        self.threshold_2 = mult(data[5])
        self.threshold_type_2 = ThresholdType.BELOW if data[6] else ThresholdType.ABOVE
        self.atk_2 = mult(data[7])

        atk = max(self.atk_1, self.atk_2)
        super().__init__(139, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.dual_threshold_stats_convert(self)


class LSRankXpBoost(LeaderSkill):
    skill_type = 148

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.multiplier = mult(data[0])
        super().__init__(148, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.rank_exp_rate_convert(self)


class LSHealMatchRcvBoost(LeaderSkill):
    skill_type = 149

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100])
        rcv = mult(data[0])
        super().__init__(149, ms, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.heart_tpa_stats_convert(self)


class LSEnhanceOrbMatch5(LeaderSkill):
    skill_type = 150

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100])
        atk = mult(data[1])
        super().__init__(150, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.five_orb_one_enhance_convert(self)


class LSHeartCross(LeaderSkill):
    skill_type = 151

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100, 100, 0])
        atk = multi_floor(data[0])
        rcv = multi_floor(data[1])
        shield = multi_floor(data[2])
        super().__init__(151, ms, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.heart_cross_convert(self)


class LSMultiboost(LeaderSkill):
    skill_type = 155

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 100])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])
        hp = multi_floor(data[2])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        super().__init__(155, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.multi_play_convert(self)


class CrossMultiplier(object):
    def __init__(self, attribute: str, atk: float):
        self.attribute = attribute
        self.atk = atk


class LSAttrCross(LeaderSkill):
    skill_type = 157

    def __init__(self, ms: MonsterSkill):
        x = ms.data
        self.crosses = [CrossMultiplier(a, mult(d)) for a, d in zip(x[::2], x[1::2])]
        super().__init__(157, ms)

    @property
    def atk(self):
        atks = sorted([x.atk for x in self.crosses])
        if len(atks) > 2:
            atks = atks[:2]

        v = atks[0]
        v = v * atks[0]
        if len(atks) > 1:
            v = v * atks[1]

        return round(v, 2)

    def text(self, converter: LSTextConverter) -> str:
        return converter.color_cross_convert(self)


class LSMatchXOrMoreOrbs(LeaderSkill):
    skill_type = 158

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 100, 100])
        self.min_match = data[0]
        self.attributes = binary_con(data[1])
        self.types = binary_con(data[2])
        self.tags = []
        hp = multi_floor(data[4])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[5])

        if self.min_match not in [4, 5]:
            human_fix_logger.warning('Unexpected orb match amount:' + str(self.min_match))
        self.tags.append((Tag.ERASE_P, (self.min_match - 1)))

        super().__init__(158, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.minimum_orb_convert(self)


class LSAdvancedBlobMatch(LeaderSkill):
    skill_type = 159

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0, 0])
        self.match_attributes = binary_con(data[0])
        self.min_count = data[1]
        self.min_atk = mult(data[2])
        self.atk_step = mult(data[3])
        self.max_count = data[4]
        self.max_atk = self.min_atk + self.atk_step * (self.max_count - self.min_count)
        super().__init__(159, ms, atk=self.max_atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.mass_match_convert(self)


class LSSevenBySix(LeaderSkill):
    skill_type = 162

    def __init__(self, ms: MonsterSkill):
        self.tags = [(Tag.BOARD_7X6, ())]
        super().__init__(162, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.tag_only_convert(self)


class LSNoSkyfallBoost(LeaderSkill):
    skill_type = 163

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 100, 0, 0])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])
        self.reduction_attributes = binary_con(data[5])
        self.tags = [(Tag.NO_SKYFALL, ())]
        hp = multi_floor(data[2])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        shield = mult(data[6])
        super().__init__(163, ms, hp=hp, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSAttrComboConditionalAtkRcvBoost(LeaderSkill):
    skill_type = 164

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 100, 100, 0])
        self.match_attributes = list_binary_con(data[0:4])
        self.min_attr = data[4]
        self.min_atk = mult(data[5])
        self.min_rcv = mult(data[6])
        self.atk_step = mult(data[7])
        self.rcv_step = self.atk_step
        self.max_attr = len(self.match_attributes)
        self.max_atk = self.min_atk + self.atk_step * (self.max_attr - self.min_attr)
        self.max_rcv = self.min_rcv + self.rcv_step * (self.max_attr - self.min_attr)
        super().__init__(164, ms, atk=self.max_atk, rcv=self.max_rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.multi_attribute_match_convert(self)


class LSRainbowAtkRcv(LeaderSkill):
    skill_type = 165

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 0, 0, 0])
        self.match_attributes = binary_con(data[0])
        self.min_attr = data[1]
        self.min_atk = mult(data[2])
        self.min_rcv = mult(data[3])
        self.atk_step = mult(data[4])
        self.rcv_step = mult(data[5])
        self.max_attr = data[6] or len(self.match_attributes)

        if self.atk_step == 0:
            self.max_attr = self.min_attr
        elif self.max_attr < self.min_attr:
            self.max_attr = self.min_attr + self.max_attr
        elif (self.max_attr + self.min_attr) <= len(self.match_attributes):
            self.max_attr = self.min_attr + self.max_attr

        self.max_atk = self.min_atk + self.atk_step * (self.max_attr - self.min_attr)
        self.max_rcv = self.min_rcv + self.rcv_step * (self.max_attr - self.min_attr)
        super().__init__(165, ms, atk=self.max_atk, rcv=self.max_rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.attribute_match_convert(self)


class LSAtkRcvComboScale(LeaderSkill):
    skill_type = 166

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.min_combos = data[0]
        self.min_atk = mult(data[1])
        self.min_rcv = mult(data[2])
        self.atk_step = mult(data[3])
        self.rcv_step = mult(data[4])
        self.max_combos = data[5]
        self.max_atk = self.min_atk + self.atk_step * (self.max_combos - self.min_combos)
        self.max_rcv = self.min_rcv + self.rcv_step * (self.max_combos - self.min_combos)
        super().__init__(166, ms, atk=self.max_atk, rcv=self.max_rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.combo_match_convert(self)


class LSBlobAtkRcvBoost(LeaderSkill):
    skill_type = 167

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 0, 0, 0])
        self.match_attributes = binary_con(data[0])
        self.min_count = data[1]
        self.min_atk = mult(data[2])
        self.min_rcv = mult(data[3])
        self.atk_step = mult(data[4])
        self.rcv_step = mult(data[5])
        self.max_count = data[6]
        self.max_atk = self.min_atk + self.atk_step * (self.max_count - self.min_count)
        self.max_rcv = self.min_rcv + self.rcv_step * (self.max_count - self.min_count)
        super().__init__(167, ms, atk=self.max_atk, rcv=self.max_rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.mass_match_convert(self)


class LSComboMultPlusShield(LeaderSkill):
    skill_type = 169

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 0])
        self.min_combos = data[0]
        atk = mult(data[1])
        shield = mult(data[2])
        super().__init__(169, ms, atk=atk, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.combo_match_convert(self)


class LSRainbowMultPlusShield(LeaderSkill):
    skill_type = 170

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0])
        self.match_attributes = binary_con(data[0])
        self.min_attr = data[1]
        atk = mult(data[2])
        shield = mult(data[3])
        super().__init__(170, ms, atk=atk, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.attribute_match_convert(self)


class LSMatchAttrPlusShield(LeaderSkill):
    skill_type = 171

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.match_attributes = list_binary_con(data[0:4])
        self.min_attr = data[4]
        atk = mult(data[5])
        shield = mult(data[6])
        super().__init__(171, ms, atk=atk, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.multi_attribute_match_convert(self)


class LSCollabConditionalBoost(LeaderSkill):
    skill_type = 175

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, None, None, 100, 100, 100])
        self.collab_id = data[0]
        hp = multi_floor(data[3])
        atk = multi_floor(data[4])
        rcv = multi_floor(data[5])
        super().__init__(175, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.collab_bonus_convert(self)


class LSOrbRemainingMultiplier(LeaderSkill):
    skill_type = 177

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 100, 0, 100, 0])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])
        self.orb_count = data[5]
        self.min_atk = multi_floor(data[3])
        self.base_atk = mult(data[6])
        self.bonus_atk = mult(data[7])
        self.tags = [(Tag.NO_SKYFALL, ())]
        hp = multi_floor(data[2])
        rcv = multi_floor(data[4])
        atk = self.min_atk * (self.base_atk + (self.bonus_atk * self.orb_count))
        super().__init__(177, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.orb_remain_convert(self)


class LSFixedMovementTime(LeaderSkill):
    skill_type = 178

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 100, 100])
        self.time = data[0]
        self.tags = []
        self.attributes = binary_con(data[1])
        self.types = binary_con(data[2])

        # TODO: this needs to be overhauled, just accept the value here if it != 0.
        if self.time == 0:
            # Ignore this case; bad skill
            pass
        elif self.time in [3, 4, 5, 6]:
            self.tags.append((Tag.FIXED_TIME, self.time))
        else:
            human_fix_logger.warning('Unexpected fixed time:' + str(self.time))
            self.tags.append((Tag.FIXED_TIME, self.time))

        hp = multi_floor(data[3])
        atk = multi_floor(data[4])
        rcv = multi_floor(data[5])
        super().__init__(178, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSRowMatcHPlusDamageReduction(LeaderSkill):
    skill_type = 182

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0])
        self.match_attributes = binary_con(data[0])
        self.min_count = data[1]
        atk = multi_floor(data[2])
        shield = mult(data[3])
        super().__init__(182, ms, atk=atk, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.mass_match_convert(self)


class LSDualThresholdBoost(LeaderSkill):
    skill_type = 183

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 0, 0, 100, 100])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])

        self.threshold_1 = mult(data[2])
        self.threshold_type_1 = ThresholdType.ABOVE
        self.atk_1 = mult(data[3])
        self.rcv_1 = 1.0
        self.shield_1 = mult(data[4])

        self.threshold_2 = mult(data[5])
        self.threshold_type_2 = ThresholdType.BELOW
        self.atk_2 = mult(data[6])
        self.rcv_2 = mult(data[7])
        self.shield_2 = 0.0

        atk = max(self.atk_1, self.atk_2)
        rcv = max(self.rcv_1, self.rcv_2)
        shield = max(self.shield_1, self.shield_2)
        super().__init__(183, ms, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.dual_threshold_stats_convert(self)


class LSBonusTimeStatBoost(LeaderSkill):
    skill_type = 185

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 100, 100])
        self.time = mult(data[0])
        self.attributes = binary_con(data[1])
        self.types = binary_con(data[2])
        hp = multi_floor(data[3])
        atk = multi_floor(data[4])
        rcv = multi_floor(data[5])
        super().__init__(185, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.bonus_time_convert(self)


class LSSevenBySixStatBoost(LeaderSkill):
    skill_type = 186

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 100])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])
        self.tags = [(Tag.BOARD_7X6, ())]
        hp = multi_floor(data[2])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        super().__init__(186, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LSBlobMatchBonusCombo(LeaderSkill):
    skill_type = 192

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0])
        self.attributes = binary_con(data[0])
        self.min_match = data[1]
        self.bonus_combo = data[3]
        atk = multi_floor(data[2])
        super().__init__(192, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.multi_mass_match_convert(self)


class LSLMatchBoost(LeaderSkill):
    skill_type = 193

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 100, 0])
        self.attributes = binary_con(data[0])
        atk = multi_floor(data[1])
        rcv = multi_floor(data[2])
        shield = mult(data[3])
        super().__init__(193, ms, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.l_match_convert(self)


class LSAttrMatchBonusCombo(LeaderSkill):
    skill_type = 194

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = binary_con(data[0])
        self.min_attr = data[1]
        self.bonus_combo = data[3]
        atk = multi_floor(data[2])
        super().__init__(194, ms, atk=atk)

    def text(self, converter: LSTextConverter) -> str:
        return converter.add_combo_att_convert(self)


class LSDisablePoisonEffects(LeaderSkill):
    skill_type = 197

    def __init__(self, ms: MonsterSkill):
        self.tags = [(Tag.DISABLE_POISON, ())]
        super().__init__(197, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.tag_only_convert(self)


class LSHealMatchBoostUnbind(LeaderSkill):
    skill_type = 198

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 0, 0])
        self.heal_amt = data[0]
        self.unbind_amt = data[3]
        atk = multi_floor(data[1])
        shield = mult(data[2])
        super().__init__(198, ms, atk=atk, shield=shield)

    def text(self, converter: LSTextConverter) -> str:
        return converter.orb_heal_convert(self)


class LSRainbowBonusDamage(LeaderSkill):
    skill_type = 199

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = binary_con(data[0])
        self.min_attr = data[1]
        self.bonus_damage = data[2]
        super().__init__(199, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.rainbow_bonus_damage_convert(self)


class LSBlobBonusDamage(LeaderSkill):
    skill_type = 200

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = binary_con(data[0])
        self.min_match = data[1]
        self.bonus_damage = data[2]
        super().__init__(200, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.mass_match_bonus_damage_convert(self)


class LSColorComboBonusDamage(LeaderSkill):
    skill_type = 201

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 0])
        self.attributes = list_binary_con(data[:4])
        self.min_combo = data[4]
        self.bonus_damage = data[5]
        super().__init__(201, ms)

    def text(self, converter: LSTextConverter) -> str:
        return converter.color_combo_bonus_damage_convert(self)


class LSGroupConditionalBoost(LeaderSkill):
    skill_type = 203

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 100, 100])
        self.group_id = data[0]
        hp = multi_floor(data[1])
        atk = multi_floor(data[2])
        rcv = multi_floor(data[3])
        super().__init__(203, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LSTextConverter) -> str:
        return converter.group_bonus_convert(self)


def convert(skill_list: List[MonsterSkill]):
    results = {}
    for s in skill_list:
        try:
            ns = convert_skill(s)
            if ns:
                results[ns.skill_id] = ns
        except Exception as ex:
            human_fix_logger.warning('Failed to convert {} {}'.format(s.skill_type, ex))

    # Fills in LSTwoPartLeaderSkills
    for s in results.values():
        if not isinstance(s, LSTwoPartLeaderSkill):
            continue
        for p_id in s.child_ids:
            if p_id not in results:
                human_fix_logger.warning('failed to look up skill id:' + str(p_id))
                continue
            p_skill = results[p_id]
            s.child_skills.append(p_skill)

    return list(results.values())


# TODO: These ended up being 1:1, convert skill type to a class value, then
# load this mapping dynamically via list of skill classes
def convert_skill(s) -> Optional[LeaderSkill]:
    d = {}
    for skill in ALL_LEADER_SKILLS:
        if skill.skill_type in d:
            raise ValueError('Unexpected duplicate skill_type: ' + str(skill.skill_type))
        d[skill.skill_type] = skill
    return d.get(s.skill_type, lambda s: None)(s)


ALL_LEADER_SKILLS = [
    LeaderSkill,
    LSAttrAtkBoost,
    LSBonusAttack,
    LSAutoheal,
    LSResolve,
    LSMovementTimeIncrease,
    LSDamageReduction,
    LSAttrDamageReduction,
    LSTypeAtkBoost,
    LSTypeHpBoost,
    LSTypeRcvBoost,
    LSStaticAtkBoost,
    LSAttrAtkRcvBoost,
    LSAllStatBoost,
    LSTwoTypeHpBoost,
    LSTwoTypeAtkBoost,
    LSTaikoDrum,
    LSTwoAttrDamageReduction,
    LSLowHpShield,
    LSLowHpAtkOrRcvBoost,
    LSTwoAttrAtkBoost,
    LSCounterattack,
    LSHighHpShield,
    LSHighHpAtkBoost,
    LSAttrAtkHpBoost,
    LSTwoAttrHpBoost,
    LSAttrHpBoost,
    LSAttrRcvBoost,
    LSEggDropRateBoost,
    LSCoinDropBoost,
    LSRainbow,
    LSTypeHpAtkBoost,
    LSTypeHpRcvBoost,
    LSTypeAtkRcvBoost,
    LSTypeAllStatBoost,
    LSComboFlatMultiplier,
    LSAttrHpRcvBoost,
    LSAttrTypeAtkBoost,
    LSAttrTypeHpAtkBoost,
    LSAttrTypeAtkRcvBoost,
    LSAttrTypeAllStatBoost,
    LSTwoTypeHpAtkBoost,
    LSTwoTypeAtkRcvBoost,
    LSLowHpConditionalAttrAtkBoost,
    LSLowHpConditionalTypeAtkBoost,
    LSHighHpConditionalAttrAtkBoost,
    LSHighHpConditionalTypeAtkBoost,
    LSComboScaledMultiplier,
    LSSkillActivationAtkRcvBoost,
    LSAtkBoostWithExactCombos,
    LSComboFlatAtkRcvBoost,
    LSComboFlatMultiplierAttrAtkBoost,
    LSReducedRcvAtkBoost,
    LSReducedHpAtkBoost,
    LSHpReduction,
    LSReducedHpTypeAtkBoost,
    LSBlobFlatAtkBoost,
    LSTwoAttrHpAtkBoost,
    LSTwoAttrAllStatBoost,
    LSBlobScalingAtkBoost,
    LSAttrOrTypeStatBoost,
    LSLowHpConditionalAttrTypeAtkRcvBoost,
    LSHighHpConditionalAttrTypeAtkRcvBoost,
    LSAttrComboScalingAtkBoost,
    LSTeamUnitConditionalStatBoost,
    LSMultiAttrTypeStatBoost,
    LSLowHpAttrAtkStatBoost,
    LSHighHpAttrTypeStatBoost,
    LSSkillUsedAttrTypeAtkRcvBoost,
    LSMultiAttrConditionalStatBoost,
    LSMultiTypeConditionalStatBoost,
    LSTwoPartLeaderSkill,
    LSHpMultiConditionalAtkBoost,
    LSRankXpBoost,
    LSHealMatchRcvBoost,
    LSEnhanceOrbMatch5,
    LSHeartCross,
    LSMultiboost,
    LSAttrCross,
    LSMatchXOrMoreOrbs,
    LSAdvancedBlobMatch,
    LSSevenBySix,
    LSNoSkyfallBoost,
    LSGroupConditionalBoost,
    LSAttrComboConditionalAtkRcvBoost,
    LSRainbowAtkRcv,
    LSAtkRcvComboScale,
    LSBlobAtkRcvBoost,
    LSComboMultPlusShield,
    LSRainbowMultPlusShield,
    LSMatchAttrPlusShield,
    LSCollabConditionalBoost,
    LSOrbRemainingMultiplier,
    LSFixedMovementTime,
    LSRowMatcHPlusDamageReduction,
    LSDualThresholdBoost,
    LSBonusTimeStatBoost,
    LSSevenBySixStatBoost,
    LSBlobMatchBonusCombo,
    LSLMatchBoost,
    LSAttrMatchBonusCombo,
    LSDisablePoisonEffects,
    LSHealMatchBoostUnbind,
    LSRainbowBonusDamage,
    LSBlobBonusDamage,
    LSColorComboBonusDamage,
]
