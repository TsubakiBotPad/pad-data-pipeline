import logging
from collections import namedtuple
from functools import reduce
from typing import Optional

from pad.raw.skill import MonsterSkill
from pad.raw.skills.en.skill_common import *

human_fix_logger = logging.getLogger('human_fix')


class LeaderSkill(object):
    skill_type = -1

    def __init__(self, skill_type: int, ms: MonsterSkill,
                 hp: float = 1,
                 atk: float = 1,
                 rcv: float = 1,
                 shield: float = 0,
                 extra_combos: int = 0,
                 bonus_damage: int = 0,
                 mult_bonus_damage: int = 0,
                 extra_time: int = 0):
        if skill_type != ms.skill_type:
            raise ValueError('Expected {} but got {}'.format(skill_type, ms.skill_type))
        self.skill_id = ms.skill_id
        self.skill_type = ms.skill_type
        if not hasattr(self, 'tags'): self.tags = []
        self.name = ms.name
        self.raw_description = ms.clean_description
        self.raw_data = ms.data
        self._hp = round(hp, 2)
        self._atk = round(atk, 2)
        self._rcv = round(rcv, 2)
        self._shield = round(shield, 4)
        self._extra_combos = extra_combos
        self._bonus_damage = bonus_damage
        self._mult_bonus_damage = mult_bonus_damage
        self._extra_time = extra_time

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
    def extra_combos(self):
        return self._extra_combos

    @property
    def bonus_damage(self):
        return self._bonus_damage

    @property
    def mult_bonus_damage(self):
        return self._mult_bonus_damage

    @property
    def extra_time(self):
        return self._extra_time

    @property
    def parts(self):
        return [self]

    def text(self, converter) -> str:
        return '<unsupported>: {}'.format(self.raw_description)

    def full_text(self, converter) -> str:
        text = self.text(converter) or ''
        return converter.full_text(text, self.tags)


class LSAttrAtkBoost(LeaderSkill):
    skill_type = 11

    def __init__(self, ms: MonsterSkill):
        self.attributes = [ms.data[0]]
        atk = mult(ms.data[1])
        super().__init__(11, ms, atk=atk)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSBonusAttack(LeaderSkill):
    skill_type = 12

    def __init__(self, ms: MonsterSkill):
        self.multiplier = mult(ms.data[0])
        super().__init__(12, ms, mult_bonus_damage=self.multiplier)

    def text(self, converter) -> str:
        return converter.after_attack_text(self)


class LSAutoheal(LeaderSkill):
    skill_type = 13

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.multiplier = mult(data[0])
        super().__init__(13, ms)

    def text(self, converter) -> str:
        return converter.heal_on_text(self)


class LSResolve(LeaderSkill):
    skill_type = 14

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.threshold = mult(data[0])
        super().__init__(14, ms)

    def text(self, converter) -> str:
        return converter.resolve_text(self)


class LSMovementTimeIncrease(LeaderSkill):
    skill_type = 15

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.time = mult(data[0])
        super().__init__(15, ms, extra_time=self.time)

    def text(self, converter) -> str:
        return converter.bonus_time_text(self)


class LSDamageReduction(LeaderSkill):
    skill_type = 16

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        shield = mult(data[0])
        super().__init__(16, ms, shield=shield)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSAttrDamageReduction(LeaderSkill):
    skill_type = 17

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.reduction_attributes = [data[0]]
        shield = mult(data[1])
        super().__init__(17, ms, shield=shield)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTypeAtkBoost(LeaderSkill):
    skill_type = 22

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.types = [data[0]]
        atk = mult(data[1])
        super().__init__(22, ms, atk=atk)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTypeHpBoost(LeaderSkill):
    skill_type = 23

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.types = [data[0]]
        hp = mult(data[1])
        super().__init__(23, ms, hp=hp)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTypeRcvBoost(LeaderSkill):
    skill_type = 24

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.types = [data[0]]
        rcv = mult(data[1])
        super().__init__(24, ms, rcv=rcv)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSStaticAtkBoost(LeaderSkill):
    skill_type = 26

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100])
        atk = mult(data[0])
        super().__init__(26, ms, atk=atk)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSAttrAtkRcvBoost(LeaderSkill):
    skill_type = 28

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.attributes = [data[0]]
        boost = mult(data[1])
        super().__init__(28, ms, atk=boost, rcv=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSAllStatBoost(LeaderSkill):
    skill_type = 29

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.attributes = [data[0]]
        boost = mult(data[1])
        super().__init__(29, ms, hp=boost, atk=boost, rcv=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTwoTypeHpBoost(LeaderSkill):
    skill_type = 30

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100])
        self.types = data[0:2]
        hp = mult(data[2])
        super().__init__(30, ms, hp=hp)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTwoTypeAtkBoost(LeaderSkill):
    skill_type = 31

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100])
        self.types = data[0:2]
        atk = mult(data[2])
        super().__init__(31, ms, atk=atk)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTaikoDrum(LeaderSkill):
    skill_type = 33

    def __init__(self, ms: MonsterSkill):
        super().__init__(33, ms)

    def text(self, converter) -> str:
        return converter.taiko_text(self)


class LSTwoAttrDamageReduction(LeaderSkill):
    skill_type = 36

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.reduction_attributes = data[0:2]
        shield = mult(ms.data[2])
        super().__init__(36, ms, shield=shield)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSLowHpShield(LeaderSkill):
    skill_type = 38

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.threshold = mult(data[0])
        self.above = False
        if self.threshold == 1:
            # This really only triggers for one specific odin, which seems to
            # have this behavior hard-coded somehow.
            self.above = True
        shield = mult(data[2])
        super().__init__(38, ms, shield=shield)

    def text(self, converter) -> str:
        return converter.threshold_stats_text(self)


class LSLowHpAtkOrRcvBoost(LeaderSkill):
    skill_type = 39

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.threshold = mult(data[0])
        self.above = False
        atk = atk_from_slice(data[1:4])
        rcv = rcv_from_slice(data[1:4])
        super().__init__(39, ms, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.threshold_stats_text(self)


class LSTwoAttrAtkBoost(LeaderSkill):
    skill_type = 40

    def __init__(self, ms: MonsterSkill):
        self.attributes = ms.data[0:2]
        atk = mult(ms.data[2])
        super().__init__(40, ms, atk=atk)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSCounterattack(LeaderSkill):
    skill_type = 41

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.chance = mult(data[0])
        self.multiplier = mult(data[1])
        self.attributes = [data[2]]
        super().__init__(41, ms)

    def text(self, converter) -> str:
        return converter.counter_attack_text(self)


class LSHighHpShield(LeaderSkill):
    skill_type = 43

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.threshold = mult(data[0])
        self.above = True
        self.chance = mult(data[1])
        shield = mult(data[2])
        super().__init__(43, ms, shield=shield)

    def text(self, converter) -> str:
        return converter.random_shield_threshold_text(self)


class LSHighHpAtkBoost(LeaderSkill):
    skill_type = 44

    def __init__(self, ms: MonsterSkill):
        self.threshold = mult(ms.data[0])
        self.above = True
        atk = atk_from_slice(ms.data[1:4])
        rcv = rcv_from_slice(ms.data[1:4])
        super().__init__(44, ms, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.threshold_stats_text(self)


class LSAttrAtkHpBoost(LeaderSkill):
    skill_type = 45

    def __init__(self, ms: MonsterSkill):
        self.attributes = [ms.data[0]]
        boost = mult(ms.data[1])
        hp = boost
        atk = boost
        super().__init__(45, ms, hp=hp, atk=atk)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTwoAttrHpBoost(LeaderSkill):
    skill_type = 46

    def __init__(self, ms: MonsterSkill):
        self.attributes = ms.data[0:2]
        hp = mult(ms.data[2])
        super().__init__(46, ms, hp=hp)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSAttrHpBoost(LeaderSkill):
    skill_type = 48

    def __init__(self, ms: MonsterSkill):
        self.attributes = [ms.data[0]]
        hp = mult(ms.data[1])
        super().__init__(48, ms, hp=hp)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSAttrRcvBoost(LeaderSkill):
    skill_type = 49

    def __init__(self, ms: MonsterSkill):
        self.attributes = [ms.data[0]]
        rcv = mult(ms.data[1])
        super().__init__(49, ms, rcv=rcv)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSEggDropRateBoost(LeaderSkill):
    skill_type = 53

    def __init__(self, ms: MonsterSkill):
        self.multiplier = mult(ms.data[0])
        super().__init__(53, ms)

    def text(self, converter) -> str:
        return converter.egg_drop_text(self)


class LSCoinDropBoost(LeaderSkill):
    skill_type = 54

    def __init__(self, ms: MonsterSkill):
        self.multiplier = mult(ms.data[0])
        super().__init__(54, ms)

    def text(self, converter) -> str:
        return converter.coin_drop_text(self)


class LSRainbow(LeaderSkill):
    skill_type = 61

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0, 0])
        self.match_attributes = binary_con(data[0])
        self.min_attr = data[1]
        self.min_atk = mult(data[2])
        self.atk_step = mult(data[3])
        self.max_attr = data[4] or len(self.match_attributes)
        self.min_rcv = 1
        self.max_rcv = 1

        if self.atk_step == 0:
            self.max_attr = self.min_attr
        elif self.max_attr < self.min_attr:
            self.max_attr = self.min_attr + self.max_attr
        elif (self.max_attr + self.min_attr) <= len(self.match_attributes):
            self.max_attr = self.min_attr + self.max_attr

        self.max_atk = self.min_atk + self.atk_step * (self.max_attr - self.min_attr)

        super().__init__(61, ms, atk=self.max_atk)

    def text(self, converter) -> str:
        return converter.attribute_match_text(self)


class LSTypeHpAtkBoost(LeaderSkill):
    skill_type = 62

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[0]]
        boost = mult(data[1])
        super().__init__(62, ms, hp=boost, atk=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTypeHpRcvBoost(LeaderSkill):
    skill_type = 63

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[0]]
        boost = mult(data[1])
        super().__init__(63, ms, hp=boost, rcv=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTypeAtkRcvBoost(LeaderSkill):
    skill_type = 64

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[0]]
        boost = mult(data[1])
        super().__init__(64, ms, atk=boost, rcv=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTypeAllStatBoost(LeaderSkill):
    skill_type = 65

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[0]]
        boost = mult(data[1])
        super().__init__(65, ms, hp=boost, atk=boost, rcv=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSComboFlatMultiplier(LeaderSkill):
    skill_type = 66

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.min_combos = data[0]
        self.min_atk = mult(data[1])
        self.max_combos = self.min_combos
        self.min_rcv = 1
        super().__init__(66, ms, atk=self.min_atk)

    def text(self, converter) -> str:
        return converter.combo_match_text(self)


class LSAttrHpRcvBoost(LeaderSkill):
    skill_type = 67

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        boost = mult(data[1])
        super().__init__(67, ms, hp=boost, rcv=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSAttrTypeAtkBoost(LeaderSkill):
    skill_type = 69

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        self.types = [data[1]]
        atk = mult(data[2])
        super().__init__(69, ms, atk=atk)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSAttrTypeHpAtkBoost(LeaderSkill):
    skill_type = 73

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        self.types = [data[1]]
        boost = mult(data[2])
        super().__init__(73, ms, hp=boost, atk=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSAttrTypeAtkRcvBoost(LeaderSkill):
    skill_type = 75

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        self.types = [data[1]]
        boost = mult(data[2])
        super().__init__(75, ms, atk=boost, rcv=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSAttrTypeAllStatBoost(LeaderSkill):
    skill_type = 76

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        self.types = [data[1]]
        boost = mult(data[2])
        super().__init__(76, ms, hp=boost, atk=boost, rcv=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTwoTypeHpAtkBoost(LeaderSkill):
    skill_type = 77

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = data[0:2]
        boost = mult(data[2])
        super().__init__(77, ms, hp=boost, atk=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTwoTypeAtkRcvBoost(LeaderSkill):
    skill_type = 79

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = data[0:2]
        boost = mult(data[2])
        super().__init__(79, ms, atk=boost, rcv=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSLowHpConditionalAttrAtkBoost(LeaderSkill):
    skill_type = 94

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.above = False
        self.threshold = mult(data[0])
        self.attributes = [data[1]]
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(94, ms, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.threshold_stats_text(self)


class LSLowHpConditionalTypeAtkBoost(LeaderSkill):
    skill_type = 95

    def __init__(self, ms: MonsterSkill):
        self.above = False
        data = ms.data
        self.threshold = mult(data[0])
        self.types = [data[1]]
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(95, ms, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.threshold_stats_text(self)


class LSHighHpConditionalAttrAtkBoost(LeaderSkill):
    skill_type = 96

    def __init__(self, ms: MonsterSkill):
        self.above = True
        data = ms.data
        self.threshold = mult(data[0])
        self.attributes = [data[1]]
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(96, ms, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.threshold_stats_text(self)


class LSHighHpConditionalTypeAtkBoost(LeaderSkill):
    skill_type = 97

    def __init__(self, ms: MonsterSkill):
        self.above = True
        data = ms.data
        self.threshold = mult(data[0])
        self.types = [data[1]]
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(97, ms, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.threshold_stats_text(self)


class LSComboScaledMultiplier(LeaderSkill):
    skill_type = 98

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 0, 0])
        self.min_combos = data[0]
        self.min_atk = mult(data[1])
        self.min_rcv = 1
        self.atk_step = mult(data[2])
        self.max_combos = data[3] or self.min_combos
        self.max_atk = self.min_atk + self.atk_step * (self.max_combos - self.min_combos)
        super().__init__(98, ms, atk=self.max_atk)

    def text(self, converter) -> str:
        return converter.combo_match_text(self)


class LSSkillActivationAtkRcvBoost(LeaderSkill):
    skill_type = 100

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        atk = atk_from_slice(data[0:4])
        rcv = rcv_from_slice(data[0:4])
        super().__init__(100, ms, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.skill_used_text(self)


class LSAtkBoostWithExactCombos(LeaderSkill):
    skill_type = 101

    def __init__(self, ms: MonsterSkill):
        self.combos = ms.data[0]
        atk = mult(ms.data[1])
        super().__init__(101, ms, atk=atk)

    def text(self, converter) -> str:
        return converter.exact_combo_text(self)


class LSComboFlatAtkRcvBoost(LeaderSkill):
    skill_type = 103

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.min_combos = data[0]
        self.min_atk = atk_from_slice(data[1:4])
        self.min_rcv = rcv_from_slice(data[1:4])
        self.max_combos = self.min_combos
        super().__init__(103, ms, atk=self.min_atk, rcv=self.min_rcv)

    def text(self, converter) -> str:
        return converter.combo_match_text(self)


class LSComboFlatMultiplierAttrAtkBoost(LeaderSkill):
    skill_type = 104

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.min_combos = data[0]
        self.max_combos = self.min_combos
        self.attributes = binary_con(data[1])
        self.min_atk = atk_from_slice(data[2:5])
        self.min_rcv = rcv_from_slice(data[2:5])
        super().__init__(104, ms, atk=self.min_atk, rcv=self.min_rcv)

    def text(self, converter) -> str:
        return converter.combo_match_text(self)


class LSReducedRcvAtkBoost(LeaderSkill):
    skill_type = 105

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        rcv = mult(data[0])
        atk = mult(data[1])
        super().__init__(105, ms, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSReducedHpAtkBoost(LeaderSkill):
    skill_type = 106

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        hp = mult(data[0])
        atk = mult(data[1])
        super().__init__(106, ms, hp=hp, atk=atk)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSHpReduction(LeaderSkill):
    skill_type = 107

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100, 0, 100])
        hp = mult(data[0])
        self.atk_attributes = binary_con(data[1])
        self.atk_for_attributes = mult(data[2])
        super().__init__(107, ms, hp=hp, atk=self.atk_for_attributes)

    def text(self, converter) -> str:
        return converter.hp_reduction_optional_atk(self.hp, self.atk_attributes, self.atk_for_attributes)


class LSReducedHpTypeAtkBoost(LeaderSkill):
    skill_type = 108

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[1]]
        hp = mult(data[0])
        atk = mult(data[2])
        super().__init__(108, ms, hp=hp, atk=atk)

    def text(self, converter) -> str:
        return converter.passive_stats_type_atk_all_hp_text(self)


class LSBlobFlatAtkBoost(LeaderSkill):
    skill_type = 109

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.match_attributes = binary_con(data[0])
        self.min_count = data[1]
        self.max_count = 0
        self.min_atk = mult(data[2])
        self.min_rcv = 1
        super().__init__(109, ms, atk=self.min_atk)

    def text(self, converter) -> str:
        return converter.mass_match_text(self)


class LSTwoAttrHpAtkBoost(LeaderSkill):
    skill_type = 111

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = data[0:2]
        boost = mult(data[2])
        super().__init__(111, ms, hp=boost, atk=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSTwoAttrAllStatBoost(LeaderSkill):
    skill_type = 114

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = data[0:2]
        boost = mult(data[2])
        super().__init__(114, ms, hp=boost, atk=boost, rcv=boost)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


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
        self.min_rcv = 1
        super().__init__(119, ms, atk=self.max_atk)

    def text(self, converter) -> str:
        return converter.mass_match_text(self)


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

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSLowHpConditionalAttrTypeAtkRcvBoost(LeaderSkill):
    skill_type = 122

    def __init__(self, ms: MonsterSkill):
        self.above = False
        data = ms.data
        self.threshold = mult(data[0])
        self.attributes = binary_con((data[1]))
        self.types = binary_con((data[2]))
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4]) if len(data) > 4 else 1
        super().__init__(122, ms, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.threshold_stats_text(self)


class LSHighHpConditionalAttrTypeAtkRcvBoost(LeaderSkill):
    skill_type = 123

    def __init__(self, ms: MonsterSkill):
        self.above = True
        data = ms.data
        self.threshold = mult(data[0])
        self.attributes = binary_con((data[1]))
        self.types = binary_con((data[2]))
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4]) if len(data) > 4 else 1
        super().__init__(123, ms, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.threshold_stats_text(self)


class LSAttrComboScalingAtkBoost(LeaderSkill):
    skill_type = 124

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 0, 100, 0])
        self.match_attributes = list_binary_con(data[0:5])
        self.min_match = data[5]
        self.max_match = len(self.match_attributes)
        self.min_atk = mult(data[6])
        self.min_rcv = 1
        self.atk_step = mult(data[7])
        self.max_atk = self.min_atk + self.atk_step * (self.max_match - self.min_match)
        super().__init__(124, ms, atk=self.max_atk)

    def text(self, converter) -> str:
        return converter.multi_attribute_match_text(self)


class LSTeamUnitConditionalStatBoost(LeaderSkill):
    skill_type = 125

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 100, 100, 100])
        self.monster_ids = list_con_pos(data[0:5])
        hp = multi_floor(data[5])
        atk = multi_floor(data[6])
        rcv = multi_floor(data[7])
        super().__init__(125, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.team_build_bonus_text(self)


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

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSLowHpAttrAtkStatBoost(LeaderSkill):
    skill_type = 130

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 100, 0, 0])
        self.threshold = mult(data[0])
        self.above = False
        self.attributes = binary_con(data[1])
        self.types = binary_con(data[2])
        self.reduction_attr = binary_con(data[5])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        shield = mult(data[6])
        super().__init__(130, ms, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter) -> str:
        return converter.threshold_stats_text(self)


class LSHighHpAttrTypeStatBoost(LeaderSkill):
    skill_type = 131

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 100, 0, 0])
        self.threshold = mult(data[0])
        self.above = True
        self.attributes = binary_con(data[1])
        self.types = binary_con(data[2])
        self.reduction_attr = binary_con(data[5])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        shield = mult(data[6])
        super().__init__(131, ms, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter) -> str:
        return converter.threshold_stats_text(self)


class LSSkillUsedAttrTypeAtkRcvBoost(LeaderSkill):
    skill_type = 133

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])
        atk = multi_floor(data[2])
        rcv = multi_floor(data[3])
        super().__init__(133, ms, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.skill_used_text(self)


class LSMultiAttrConditionalStatBoost(LeaderSkill):
    skill_type = 136

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 100, 100, 0, 100, 100, 100])
        self.attributes_1 = binary_con(data[0])
        self.types_1 = []
        self.hp_1 = multi_floor(data[1])
        self.atk_1 = multi_floor(data[2])
        self.rcv_1 = multi_floor(data[3])
        self.attributes_2 = binary_con(data[4])
        self.types_2 = []
        self.hp_2 = multi_floor(data[5])
        self.atk_2 = multi_floor(data[6])
        self.rcv_2 = multi_floor(data[7])

        def min_1_if_set(settable, value):
            """Only constrain the value to 1 if it is optional."""
            return max(value, 1.0) if len(settable) < 5 else value

        hp = min_1_if_set(self.attributes_1, self.hp_1) * min_1_if_set(self.attributes_2, self.hp_2)
        atk = min_1_if_set(self.attributes_1, self.atk_1) * min_1_if_set(self.attributes_2, self.atk_2)
        rcv = min_1_if_set(self.attributes_1, self.rcv_1) * min_1_if_set(self.attributes_2, self.rcv_2)
        super().__init__(136, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.dual_passive_stat_text(self)


class LSMultiTypeConditionalStatBoost(LeaderSkill):
    skill_type = 137

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 100, 100, 0, 100, 100, 100])
        self.attributes_1 = []
        self.types_1 = binary_con(data[0])
        self.hp_1 = multi_floor(data[1])
        self.atk_1 = multi_floor(data[2])
        self.rcv_1 = multi_floor(data[3])
        self.attributes_2 = []
        self.types_2 = binary_con(data[4])
        self.hp_2 = multi_floor(data[5])
        self.atk_2 = multi_floor(data[6])
        self.rcv_2 = multi_floor(data[7])
        hp = self.hp_1 * self.hp_2
        atk = self.atk_1 * self.atk_2
        rcv = self.rcv_1 * self.rcv_2
        super().__init__(137, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.dual_passive_stat_text(self)


class LSMultiPartSkill(LeaderSkill):
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
        return round(v, 4)

    @property
    def extra_combos(self):
        return sum([x.extra_combos for x in self.child_skills])

    @property
    def bonus_damage(self):
        return sum([x.bonus_damage for x in self.child_skills])

    @property
    def mult_bonus_damage(self):
        return sum([x.mult_bonus_damage for x in self.child_skills])

    @property
    def extra_time(self):
        return sum([x.extra_time for x in self.child_skills])

    @property
    def parts(self):
        return self.child_skills

    def text(self, converter) -> str:
        parts = map(lambda x: x.text(converter), self.parts)
        return converter.concat_list_semicolons(parts)

    def full_text(self, converter):
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
        self.above_1 = not data[3]
        self.atk_1 = mult(data[4]) or 1
        self.rcv_1 = 1
        self.shield_1 = 0

        self.threshold_2 = mult(data[5])
        self.above_2 = not data[6]
        self.atk_2 = mult(data[7])
        self.rcv_2 = 1
        self.shield_2 = 0

        atk = max(self.atk_1, self.atk_2)
        super().__init__(139, ms, atk=atk)

    def text(self, converter) -> str:
        return converter.dual_threshold_stats_text(self)


class LSRankXpBoost(LeaderSkill):
    skill_type = 148

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.multiplier = mult(data[0])
        super().__init__(148, ms)

    def text(self, converter) -> str:
        return converter.rank_exp_rate_text(self)


class LSHealMatchRcvBoost(LeaderSkill):
    skill_type = 149

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100])
        rcv = mult(data[0])
        super().__init__(149, ms, rcv=rcv)

    def text(self, converter) -> str:
        return converter.heart_tpa_stats_text(self)


class LSEnhanceOrbMatch5(LeaderSkill):
    skill_type = 150

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100])
        atk = mult(data[1])
        super().__init__(150, ms, atk=atk)

    def text(self, converter) -> str:
        return converter.five_orb_one_enhance_text(self)


class LSHeartCrossShield(LeaderSkill):
    skill_type = 151

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100, 100, 0])
        atk = multi_floor(data[0])
        rcv = multi_floor(data[1])
        shield = multi_floor(data[2])
        super().__init__(151, ms, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter) -> str:
        return converter.heart_cross_shield_text(self)


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

    def text(self, converter) -> str:
        return converter.multi_play_text(self)


CrossMultiplier = namedtuple("CrossMultiplier", ['attribute', 'atk'])


class LSAttrCross(LeaderSkill):
    skill_type = 157

    def __init__(self, ms: MonsterSkill):
        self.atks = sorted(ms.data[1::2])
        if len(set(self.atks)) > 1:
            human_fix_logger.error('Bad assumption; cross LS has multiple attack values: %s', ms.skill_id)

        self.multiplier = mult(ms.data[1])
        self.attributes = ms.data[::2]

        self.crossmults = [CrossMultiplier(ms.data[i], ms.data[i + 1]) for i in range(0, len(ms.data), 2)]

        atk = self.multiplier ** (2 if len(self.attributes) == 1 else 3)
        super().__init__(157, ms, atk=round(atk, 2))

    def text(self, converter) -> str:
        return converter.color_cross_text(self)


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

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


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
        self.min_rcv = 1
        super().__init__(159, ms, atk=self.max_atk)

    def text(self, converter) -> str:
        return converter.mass_match_text(self)


class LSSevenBySix(LeaderSkill):
    skill_type = 162

    def __init__(self, ms: MonsterSkill):
        self.tags = [(Tag.BOARD_7X6, ())]
        super().__init__(162, ms)

    def text(self, converter) -> str:
        return converter.tag_only_text(self)


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

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSAttrComboConditionalAtkRcvBoost(LeaderSkill):
    skill_type = 164

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 100, 100, 0])
        self.match_attributes = list_binary_con(data[0:4])
        self.min_match = data[4]
        self.min_atk = mult(data[5])
        self.min_rcv = mult(data[6])
        self.atk_step = mult(data[7])
        self.rcv_step = self.atk_step
        self.max_match = len(self.match_attributes)
        self.max_atk = self.min_atk + self.atk_step * (self.max_match - self.min_match)
        self.max_rcv = self.min_rcv + self.rcv_step * (self.max_match - self.min_match)
        super().__init__(164, ms, atk=self.max_atk, rcv=self.max_rcv)

    def text(self, converter) -> str:
        return converter.multi_attribute_match_text(self)


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

    def text(self, converter) -> str:
        return converter.attribute_match_text(self)


class LSAtkRcvComboScale(LeaderSkill):
    skill_type = 166

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [1, 100, 100, 0, 0, 0])
        self.min_combos = data[0]
        self.min_atk = mult(data[1])
        self.min_rcv = mult(data[2])
        self.atk_step = mult(data[3])
        self.rcv_step = mult(data[4])
        self.max_combos = data[5]
        self.max_atk = self.min_atk + self.atk_step * (self.max_combos - self.min_combos)
        self.max_rcv = self.min_rcv + self.rcv_step * (self.max_combos - self.min_combos)
        super().__init__(166, ms, atk=self.max_atk, rcv=self.max_rcv)

    def text(self, converter) -> str:
        return converter.combo_match_text(self)


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

        # Overrides for optional atk/rcv
        if self.min_atk == 0 and self.max_atk == 0:
            self.min_atk = 1.0
            self.max_atk = 1.0
        if self.min_rcv == 0 and self.max_rcv == 0:
            self.min_rcv = 1.0
            self.max_rcv = 1.0

        super().__init__(167, ms, atk=self.max_atk, rcv=self.max_rcv)

    def text(self, converter) -> str:
        return converter.mass_match_text(self)


class LSComboMultPlusShield(LeaderSkill):
    skill_type = 169

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 0])
        self.min_combos = data[0]
        self.max_combos = self.min_combos
        self.min_atk = mult(data[1])
        self.min_rcv = 1
        shield = mult(data[2])
        super().__init__(169, ms, atk=self.min_atk, shield=shield)

    def text(self, converter) -> str:
        return converter.combo_match_text(self)


class LSRainbowMultPlusShield(LeaderSkill):
    skill_type = 170

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0, 0, 5])
        self.match_attributes = binary_con(data[0])
        self.min_attr = data[1]
        self.max_attr = 5
        self.min_atk = mult(data[2])
        self.atk_step = mult(data[4])
        self.max_atk = self.min_atk + self.atk_step * (5 - data[5])
        self.min_rcv = 1
        self.max_rcv = 1
        shield = mult(data[3])
        super().__init__(170, ms, atk=self.max_atk, shield=shield)

    def text(self, converter) -> str:
        return converter.scaling_attribute_match_text(self)


class LSMatchAttrPlusShield(LeaderSkill):
    skill_type = 171

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 100, 0])
        self.match_attributes = list_binary_con(data[0:4])
        self.min_match = data[4]
        self.min_atk = mult(data[5])
        self.max_atk = self.min_atk
        self.min_rcv = 1
        shield = mult(data[6])
        super().__init__(171, ms, atk=self.min_atk, shield=shield)

    def text(self, converter) -> str:
        return converter.multi_attribute_match_text(self)


class LSCollabConditionalBoost(LeaderSkill):
    skill_type = 175

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, None, None, 100, 100, 100])
        self.collab_id = data[0]
        hp = multi_floor(data[3])
        atk = multi_floor(data[4])
        rcv = multi_floor(data[5])
        super().__init__(175, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.collab_bonus_text(self)


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
        self.max_bonus_atk = self.base_atk + (self.bonus_atk * self.orb_count)
        self.tags = [(Tag.NO_SKYFALL, ())]
        hp = multi_floor(data[2])
        rcv = multi_floor(data[4])
        atk = self.min_atk * self.max_bonus_atk
        super().__init__(177, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.orb_remain_text(self)


class LSFixedMovementTime(LeaderSkill):
    skill_type = 178

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 100, 100, 0, 0])
        self.time = data[0]
        self.tags = [(Tag.FIXED_TIME, self.time)]
        self.attributes = binary_con(data[1])
        self.types = binary_con(data[2])

        hp = multi_floor(data[3])
        atk = multi_floor(data[4])
        rcv = multi_floor(data[5])
        self.reduction_attributes = binary_con(data[6])
        shield = mult(data[7])

        super().__init__(178, ms, hp=hp, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSRowMatcHPlusDamageReduction(LeaderSkill):
    skill_type = 182

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0])
        self.match_attributes = binary_con(data[0])
        self.min_count = data[1]
        self.max_count = 0
        self.min_atk = multi_floor(data[2])
        self.min_rcv = 1
        shield = mult(data[3])
        super().__init__(182, ms, atk=self.min_atk, shield=shield)

    def text(self, converter) -> str:
        return converter.mass_match_text(self)


class LSDualThresholdBoost(LeaderSkill):
    skill_type = 183

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 0, 0, 100, 100])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])

        self.threshold_1 = mult(data[2])
        self.above_1 = True
        self.atk_1 = mult(data[3]) or 1
        self.rcv_1 = 1.0
        self.shield_1 = mult(data[4])

        self.threshold_2 = mult(data[5])
        self.above_2 = False
        self.atk_2 = mult(data[6])
        self.rcv_2 = mult(data[7])
        self.shield_2 = 0.0

        atk = max(self.atk_1, self.atk_2)
        rcv = max(self.rcv_1, self.rcv_2)
        shield = max(self.shield_1, self.shield_2)
        super().__init__(183, ms, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter) -> str:
        return converter.dual_threshold_stats_text(self)


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
        super().__init__(185, ms, hp=hp, atk=atk, rcv=rcv, extra_time=self.time)

    def text(self, converter) -> str:
        return converter.bonus_time_text(self)


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

    def text(self, converter) -> str:
        return converter.passive_stats_text(self)


class LSBlobMatchBonusCombo(LeaderSkill):
    skill_type = 192

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0])
        self.attributes = binary_con(data[0])
        self.min_match = data[1]
        self.bonus_combo = data[3]
        atk = multi_floor(data[2])
        self.conj_and = True
        super().__init__(192, ms, atk=atk, extra_combos=self.bonus_combo)

    def text(self, converter) -> str:
        return converter.multi_mass_match_text(self)


class LSLMatchBoost(LeaderSkill):
    skill_type = 193

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 100, 0])
        self.attributes = binary_con(data[0])
        atk = multi_floor(data[1])
        rcv = multi_floor(data[2])
        shield = mult(data[3])
        super().__init__(193, ms, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter) -> str:
        return converter.l_match_text(self)


class LSAttrMatchBonusCombo(LeaderSkill):
    skill_type = 194

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0])
        self.attributes = binary_con(data[0])
        self.min_attr = data[1]
        atk = multi_floor(data[2])
        self.bonus_combo = data[3]
        super().__init__(194, ms, atk=atk, extra_combos=self.bonus_combo)

    def text(self, converter) -> str:
        return converter.add_combo_att_text(self)


class LSDisablePoisonEffects(LeaderSkill):
    skill_type = 197

    def __init__(self, ms: MonsterSkill):
        self.tags = [(Tag.DISABLE_POISON, ())]
        super().__init__(197, ms)

    def text(self, converter) -> str:
        return converter.tag_only_text(self)


class LSHealMatchBoostUnbind(LeaderSkill):
    skill_type = 198

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 0, 0])
        self.heal_amt = data[0]
        self.unbind_amt = data[3]
        atk = multi_floor(data[1])
        shield = mult(data[2])
        super().__init__(198, ms, atk=atk, shield=shield)

    def text(self, converter) -> str:
        return converter.orb_heal_text(self)


class LSRainbowBonusDamage(LeaderSkill):
    skill_type = 199

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = binary_con(data[0])
        self.min_attr = data[1]
        super().__init__(199, ms, bonus_damage=data[2])

    def text(self, converter) -> str:
        return converter.rainbow_bonus_damage_text(self)


class LSBlobBonusDamage(LeaderSkill):
    skill_type = 200

    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = binary_con(data[0])
        self.min_match = data[1]
        super().__init__(200, ms, bonus_damage=data[2])

    def text(self, converter) -> str:
        return converter.mass_match_bonus_damage_text(self)


class LSColorComboBonusDamage(LeaderSkill):
    skill_type = 201

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 0])
        self.attributes = list_binary_con(data[:4])
        self.min_combo = data[4]
        super().__init__(201, ms, bonus_damage=data[5])

    def text(self, converter) -> str:
        return converter.color_combo_bonus_damage_text(self)


class LSGroupConditionalBoost(LeaderSkill):
    skill_type = 203

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 100, 100])
        self.group_id = data[0]
        hp = multi_floor(data[1])
        atk = multi_floor(data[2])
        rcv = multi_floor(data[3])
        super().__init__(203, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter) -> str:
        return converter.group_bonus_text(self)


class LSColorComboBonusCombo(LeaderSkill):
    skill_type = 206

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 0, 0])
        self.attributes = list_binary_con(data[:4])
        self.min_combo = data[5]
        self.bonus_combos = data[6]
        super().__init__(206, ms, extra_combos=self.bonus_combos)

    def text(self, converter) -> str:
        return converter.color_combo_bonus_combo_text(self)


class LSHeartCrossCombo(LeaderSkill):
    skill_type = 209

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.bonus_combos = data[0]
        super().__init__(209, ms, extra_combos=self.bonus_combos)

    def text(self, converter) -> str:
        return converter.heart_cross_combo_text(self)


class LSColorCrossCombo(LeaderSkill):
    skill_type = 210

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 1])
        self.bonus_combos = data[2]
        self.attributes = binary_con(data[0])
        super().__init__(210, ms, extra_combos=self.bonus_combos)

    def text(self, converter) -> str:
        return converter.color_cross_combo_text(self)


class LSBlobMatchMultiAttrBonusCombo(LeaderSkill):
    skill_type = 219

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.attributes = binary_con(data[0])
        self.min_match = data[1]
        self.bonus_combo = data[2]
        self.conj_and = False
        super().__init__(219, ms, extra_combos=self.bonus_combo)

    def text(self, converter) -> str:
        return converter.multi_mass_match_text(self)


class LSLMatchComboBoost(LeaderSkill):
    skill_type = 220

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.attributes = binary_con(data[0])
        super().__init__(220, ms, extra_combos=data[1])

    def text(self, converter) -> str:
        return converter.l_match_combo_text(self)


class LSComboBonusDamage(LeaderSkill):
    skill_type = 223

    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.min_combos = data[0]
        super().__init__(223, ms, bonus_damage=data[1])

    def text(self, converter) -> str:
        return converter.combo_bonus_damage_text(self)


def convert(skill_list: List[MonsterSkill]):
    results = {}
    for s in skill_list:
        try:
            ns = convert_skill(s)
            if ns:
                results[ns.skill_id] = ns
        except Exception as ex:
            human_fix_logger.warning('Failed to convert {} {}'.format(s.skill_type, ex))

    # Fills in LSMultiPartSkills
    for s in results.values():
        if not isinstance(s, LSMultiPartSkill):
            continue
        for p_id in s.child_ids:
            if p_id not in results:
                human_fix_logger.warning('failed to look up leader skill id:' + str(p_id))
                continue
            p_skill = results[p_id]
            s.child_skills.append(p_skill)
    return list(results.values())


# TODO: These ended up being 1:1, convert skill type to a class value, then
# load this mapping dynamically via list of skill classes
def convert_skill(s) -> Optional[LeaderSkill]:
    if s.skill_id == 1538:
        # This works around a bug in gungho's code for this specific skill.
        # Currently the skill data for 1538 is ['無し', '', 0, 0, 0, ''] but it's in use.
        return LeaderSkill(0, s)

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
    LSMultiPartSkill,
    LSHpMultiConditionalAtkBoost,
    LSRankXpBoost,
    LSHealMatchRcvBoost,
    LSEnhanceOrbMatch5,
    LSHeartCrossShield,
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
    LSColorComboBonusCombo,
    LSHeartCrossCombo,
    LSColorCrossCombo,
    LSBlobMatchMultiAttrBonusCombo,
    LSLMatchComboBoost,
    LSComboBonusDamage,
]
