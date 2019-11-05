from typing import List, Optional

from pad.raw.skill import MonsterSkill
from pad.raw.skills.leader_skill_common import ThresholdType, Tag, sort_tags
from pad.raw.skills.leader_skill_text import LsTextConverter


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
    def __init__(self, skill_type: int, ms: MonsterSkill,
                 hp: float = 1, atk: float = 1, rcv: float = 1, shield: float = 0):
        if skill_type != ms.skill_type:
            raise ValueError('Expected {} but got {}'.format(skill_type, ms.skill_type))
        self.skill_id = ms.skill_id
        self.skill_type = ms.skill_type

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

    def text(self, converter: LsTextConverter) -> str:
        return '<unsupported>: {}'.format(self.raw_description)

    def tag_text(self, converter: LsTextConverter) -> str:
        tags = getattr(self, 'tags', [])
        return ''.join([converter.TAGS[x] for x in sort_tags(tags)])

    def full_text(self, converter: LsTextConverter) -> str:
        text = self.text(converter) or ''
        tag_text = self.tag_text(converter) or ''
        if tag_text:
            if text:
                return '{} {}'.format(tag_text, text)
            else:
                return tag_text
        return text


class AttrAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.attributes = [ms.data[0]]
        atk = mult(ms.data[1])
        super().__init__(11, ms, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class BonusAttack(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.multiplier = mult(ms.data[0])
        super().__init__(12, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.after_attack_convert(self)


class Autoheal(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.multiplier = mult(data[0])
        super().__init__(13, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.heal_on_convert(self)


class Resolve(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.threshold = mult(data[0])
        super().__init__(14, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.resolve_convert(self)


class MovementTimeIncrease(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.time = mult(data[0])
        super().__init__(15, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.bonus_time_convert(self)


class DamageReduction(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        shield = mult(data[0])
        super().__init__(16, ms, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class AttrDamageReduction(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0])
        self.reduction_attributes = [data[0]]
        shield = mult(data[1])
        super().__init__(17, ms, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TypeAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.types = [data[0]]
        atk = mult(data[1])
        super().__init__(22, ms, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TypeHpBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.types = [data[0]]
        hp = mult(data[1])
        super().__init__(23, ms, hp=hp)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TypeRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.types = [data[0]]
        rcv = mult(data[1])
        super().__init__(24, ms, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class StaticAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100])
        atk = mult(data[0])
        super().__init__(26, ms, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class AttrAtkRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.attributes = [data[0]]
        boost = mult(data[1])
        super().__init__(28, ms, atk=boost, rcv=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class AllStatBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.attributes = [data[0]]
        boost = mult(data[1])
        super().__init__(29, ms, hp=boost, atk=boost, rcv=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TwoTypeHpBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100])
        self.types = data[0:2]
        hp = mult(data[2])
        super().__init__(30, ms, hp=hp)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TwoTypeAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100])
        self.types = data[0:2]
        atk = mult(data[2])
        super().__init__(31, ms, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TaikoDrum(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        super().__init__(33, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.taiko_convert(converter)


class TwoAttrDamageReduction(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.reduction_attributes = data[0:2]
        shield = mult(ms.data[2])
        super().__init__(36, ms, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LowHpShield(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.threshold = mult(data[0])
        self.threshold_type = ThresholdType.BELOW
        shield = mult(data[2])
        super().__init__(38, ms, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LowHpAtkOrRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0])
        self.threshold = mult(data[0])
        self.threshold_type = ThresholdType.BELOW
        atk = atk_from_slice(data[1:4])
        rcv = rcv_from_slice(data[1:4])
        super().__init__(39, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class TwoAttrAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.attributes = ms.data[0:2]
        atk = mult(ms.data[2])
        super().__init__(40, ms, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class Counterattack(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0])
        self.chance = mult(data[0])
        self.multiplier = mult(data[1])
        self.attributes = [data[2]]
        super().__init__(41, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.counter_attack_convert(self)


class HighHpShield(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.threshold = mult(ms.data[0])
        self.threshold_type = ThresholdType.ABOVE
        shield = mult(ms.data[2])
        super().__init__(43, ms, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class HighHpAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.threshold = mult(ms.data[0])
        self.threshold_type = ThresholdType.ABOVE
        atk = atk_from_slice(ms.data[1:4])
        rcv = rcv_from_slice(ms.data[1:4])
        super().__init__(44, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class AttrAtkHpBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.attributes = [ms.data[0]]
        boost = mult(ms.data[1])
        hp = boost
        atk = boost
        super().__init__(45, ms, hp=hp, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TwoAttrHpBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.attributes = ms.data[0:2]
        hp = mult(ms.data[2])
        super().__init__(46, ms, hp=hp)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class AttrHpBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.attributes = [ms.data[0]]
        hp = mult(ms.data[1])
        super().__init__(48, ms, hp=hp)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class AttrRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.attributes = [ms.data[0]]
        rcv = mult(ms.data[1])
        super().__init__(49, ms, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class EggDropRateBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.multiplier = mult(ms.data[0])
        super().__init__(53, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.egg_drop_convert(self)


class CoinDropBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.multiplier = mult(ms.data[0])
        super().__init__(54, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.coin_drop_convert(self)


class Rainbow(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.attribute_match_convert(self)


class TypeHpAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[0]]
        boost = mult(data[1])
        super().__init__(62, ms, hp=boost, atk=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TypeHpRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[0]]
        boost = mult(data[1])
        super().__init__(63, ms, hp=boost, rcv=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TypeAtkRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[0]]
        boost = mult(data[1])
        super().__init__(64, ms, atk=boost, rcv=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TypeAllStatBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[0]]
        boost = mult(data[1])
        super().__init__(65, ms, hp=boost, atk=boost, rcv=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class ComboFlatMultiplier(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100])
        self.min_combos = data[0]
        atk = mult(data[1])
        super().__init__(66, ms, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.combo_match_convert(self)


class AttrHpRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        boost = mult(data[1])
        super().__init__(67, ms, hp=boost, rcv=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class AttrTypeAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        self.types = [data[1]]
        atk = mult(data[2])
        super().__init__(69, ms, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class AttrTypeHpAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        self.types = [data[1]]
        boost = mult(data[2])
        super().__init__(73, ms, hp=boost, atk=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class AttrTypeAtkRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        self.types = [data[1]]
        boost = mult(data[2])
        super().__init__(75, ms, atk=boost, rcv=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class AttrTypeAllStatBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = [data[0]]
        self.types = [data[1]]
        boost = mult(data[2])
        super().__init__(76, ms, hp=boost, atk=boost, rcv=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TwoTypeHpAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = data[0:2]
        boost = mult(data[2])
        super().__init__(77, ms, hp=boost, atk=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TwoTypeAtkRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = data[0:2]
        boost = mult(data[2])
        super().__init__(79, ms, atk=boost, rcv=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LowHpConditionalAttrAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.threshold_type = ThresholdType.BELOW
        self.threshold = mult(data[0])
        self.attributes = [data[1]]
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(94, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class LowHpConditionalTypeAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.threshold_type = ThresholdType.BELOW
        data = ms.data
        self.threshold = mult(data[0])
        self.types = [data[1]]
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(95, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class HighHpConditionalAttrAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.threshold_type = ThresholdType.ABOVE
        data = ms.data
        self.threshold = mult(data[0])
        self.attributes = [data[1]]
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(96, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class HighHpConditionalTypeAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.threshold_type = ThresholdType.ABOVE
        data = ms.data
        self.threshold = mult(data[0])
        self.types = [data[1]]
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(97, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class ComboScaledMultiplier(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 0, 0])
        self.min_combos = data[0]
        self.min_atk = mult(data[1])
        self.atk_step = mult(data[2])
        self.max_combos = data[3] or self.min_combos
        self.max_atk = self.min_atk + self.atk_step * (self.max_combos - self.min_combos)
        super().__init__(98, ms, atk=self.max_atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.combo_match_convert(self)


class SkillActivationAtkRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        atk = atk_from_slice(data[0:4])
        rcv = rcv_from_slice(data[0:4])
        super().__init__(100, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.skill_used_convert(self)


class AtkBoostWithExactCombos(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.combos = ms.data[0]
        atk = mult(ms.data[1])
        super().__init__(101, ms, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.exact_combo_convert(self)


class ComboFlatAtkRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.min_combos = data[0]
        atk = atk_from_slice(data[1:4])
        rcv = rcv_from_slice(data[1:4])
        super().__init__(103, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.combo_match_convert(self)


class ComboFlatMultiplierAttrAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.min_combos = data[0]
        self.attributes = binary_con(data[1])
        atk = atk_from_slice(data[2:5])
        rcv = rcv_from_slice(data[2:5])
        super().__init__(104, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.combo_match_convert(self)


class ReducedRcvAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        rcv = mult(data[0])
        atk = mult(data[1])
        super().__init__(105, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class ReducedHpAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        hp = mult(data[0])
        atk = mult(data[1])
        super().__init__(106, ms, hp=hp, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class HpReduction(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        hp = mult(data[0])
        super().__init__(107, ms, hp=hp)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class ReducedHpTypeAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.types = [data[1]]
        hp = mult(data[0])
        atk = mult(data[2])
        super().__init__(108, ms, hp=hp, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_type_atk_all_hp_convert(self)


class BlobFlatAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.match_attributes = binary_con(data[0])
        self.min_count = data[1]
        atk = mult(data[2])
        super().__init__(109, ms, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.mass_match_convert(self)


class TwoAttrHpAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = data[0:2]
        boost = mult(data[2])
        super().__init__(111, ms, hp=boost, atk=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class TwoAttrAllStatBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = data[0:2]
        boost = mult(data[2])
        super().__init__(114, ms, hp=boost, atk=boost, rcv=boost)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class BlobScalingAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0, 0])
        self.match_attributes = binary_con(data[0])
        self.min_count = data[1]
        self.min_atk = mult(data[2])
        self.atk_step = mult(data[3])
        self.max_count = data[4]
        self.max_atk = self.min_atk + self.atk_step * (self.max_count - self.min_count)
        super().__init__(119, ms, atk=self.max_atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.mass_match_convert(self)


class AttrOrTypeStatBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 100])
        self.attributes = binary_con(data[0])
        self.types = binary_con((data[1]))
        hp = multi_floor(data[2])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        super().__init__(121, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LowHpConditionalAttrTypeAtkRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.threshold_type = ThresholdType.BELOW
        data = ms.data
        self.threshold = mult(data[0])
        self.attributes = binary_con((data[1]))
        self.types = binary_con((data[2]))
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4]) if len(data) > 4 else 1
        super().__init__(122, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class HighHpConditionalAttrTypeAtkRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.threshold_type = ThresholdType.ABOVE
        data = ms.data
        self.threshold = mult(data[0])
        self.attributes = binary_con((data[1]))
        self.types = binary_con((data[2]))
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4]) if len(data) > 4 else 1
        super().__init__(123, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class AttrComboScalingAtkBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 0, 100, 0])
        self.match_attributes = list_binary_con(data[0:5])
        self.min_combo = data[5]
        self.max_combo = len(self.match_attributes)
        self.min_atk = mult(data[6])
        self.atk_step = mult(data[7])
        self.max_atk = self.min_atk + self.atk_step * (self.max_combo - self.min_combo)
        super().__init__(124, ms, atk=self.max_atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.multi_attribute_match_convert(self)


class TeamUnitConditionalStatBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 0, 0, 100, 100, 100])
        self.monster_ids = list_con_pos(data[0:5])
        hp = multi_floor(data[5])
        atk = multi_floor(data[6])
        rcv = multi_floor(data[7])
        super().__init__(125, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.team_build_bonus_convert(self)


class MultiAttrTypeStatBoost(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class LowHpAttrAtkStatBoost(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class HighHpAttrTypeStatBoost(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.threshold_stats_convert(self)


class SkillUsedAttrTypeAtkRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])
        atk = multi_floor(data[2])
        rcv = multi_floor(data[3])
        super().__init__(133, ms, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.skill_used_convert(self)


class MultiAttrConditionalStatBoost(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.dual_passive_stat_convert(self)


class MultiTypeConditionalStatBoost(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.dual_passive_stat_convert(self)


class TwoPartLeaderSkill(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        parts = map(lambda x: x.text(converter), self.parts)
        return '; '.join([p for p in parts if p])

    def tag_text(self, converter: LsTextConverter) -> str:
        tags = set()
        for cs in self.parts:
            tags.update(getattr(cs, 'tags', []))

        return ''.join([converter.TAGS[x] for x in sort_tags(tags)])


class HpMultiConditionalAtkBoost(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.dual_threshold_stats_convert(self)


class RankXpBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0])
        self.multiplier = mult(data[0])
        super().__init__(148, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.rank_exp_rate_convert(self)


class HealMatchRcvBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100])
        rcv = mult(data[0])
        super().__init__(149, ms, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.heart_tpa_stats_convert(self)


class EnhanceOrbMatch5(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100])
        atk = mult(data[1])
        super().__init__(150, ms, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.five_orb_one_enhance_convert(self)


class HeartCross(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [100, 100, 0])
        atk = multi_floor(data[0])
        rcv = multi_floor(data[1])
        shield = multi_floor(data[2])
        super().__init__(151, ms, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.heart_cross_convert(self)


class Multiboost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 100])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])
        hp = multi_floor(data[2])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        super().__init__(155, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.multi_play_convert(self)


class CrossMultiplier(object):
    def __init__(self, attribute: str, atk: float):
        self.attribute = attribute
        self.atk = atk


class AttrCross(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.color_cross_convert(self)


class MatchXOrMoreOrbs(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 100, 100])
        self.min_match = data[0]
        self.attributes = binary_con(data[1])
        self.types = binary_con(data[2])
        self.tags = []
        hp = multi_floor(data[4])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[5])

        if self.min_match == 4:
            self.tags.append(Tag.ERASE_4P)
        elif self.min_match == 5:
            self.tags.append(Tag.ERASE_5P)
        else:
            raise ValueError('Unexpected orb match amount:' + self.min_match)

        super().__init__(158, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.minimum_orb_convert(self)


class AdvancedBlobMatch(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0, 0])
        self.match_attributes = binary_con(data[0])
        self.min_count = data[1]
        self.min_atk = mult(data[2])
        self.atk_step = mult(data[3])
        self.max_count = data[4]
        self.max_atk = self.min_atk + self.atk_step * (self.max_count - self.min_count)
        super().__init__(159, ms, atk=self.max_atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.mass_match_convert(self)


class SevenBySix(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.tags = [Tag.BOARD_7X6]
        super().__init__(162, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.tag_only_convert(self)


class NoSkyfallBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 100, 0, 0])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])
        self.reduction_attributes = binary_con(data[5])
        self.tags = [Tag.NO_SKYFALL]
        hp = multi_floor(data[2])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        shield = mult(data[6])
        super().__init__(163, ms, hp=hp, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class AttrComboConditionalAtkRcvBoost(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.multi_attribute_match_convert(self)


class RainbowAtkRcv(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.attribute_match_convert(self)


class AtkRcvComboScale(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.combo_match_convert(self)


class BlobAtkRcvBoost(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.mass_match_convert(self)


class ComboMultPlusShield(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 0])
        self.min_combos = data[0]
        atk = mult(data[1])
        shield = mult(data[2])
        super().__init__(169, ms, atk=atk, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.combo_match_convert(self)


class RainbowMultPlusShield(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0])
        self.match_attributes = binary_con(data[0])
        self.min_attr = data[1]
        atk = mult(data[2])
        shield = mult(data[3])
        super().__init__(170, ms, atk=atk, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.attribute_match_convert(self)


class MatchAttrPlusShield(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.match_attributes = list_binary_con(data[0:4])
        self.min_attr = data[4]
        atk = mult(data[5])
        shield = mult(data[6])
        super().__init__(171, ms, atk=atk, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.multi_attribute_match_convert(self)


class CollabConditionalBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, None, None, 100, 100, 100])
        self.collab_id = data[0]
        hp = multi_floor(data[3])
        atk = multi_floor(data[4])
        rcv = multi_floor(data[5])
        super().__init__(175, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.collab_bonus_convert(self)


class OrbRemainingMultiplier(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 100, 0, 100, 0])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])
        self.orb_count = data[5]
        self.min_atk = multi_floor(data[3])
        self.base_atk = mult(data[6])
        self.bonus_atk = mult(data[7])
        self.tags = [Tag.NO_SKYFALL]
        hp = multi_floor(data[2])
        rcv = multi_floor(data[4])
        atk = self.min_atk * (self.base_atk + (self.bonus_atk * self.orb_count))
        super().__init__(177, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.orb_remain_convert(self)


class FixedMovementTime(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 100, 100])
        self.time = data[0]
        self.tags = []
        self.attributes = binary_con(data[1])
        self.types = binary_con(data[2])

        if self.time == 4:
            self.tags.append(Tag.FIXED_4S)
        elif self.time == 5:
            self.tags.append(Tag.FIXED_5S)
        else:
            raise ValueError('Unexpected fixed time:' + str(self.time))

        hp = multi_floor(data[3])
        atk = multi_floor(data[4])
        rcv = multi_floor(data[5])
        super().__init__(178, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class RowMatcHPlusDamageReduction(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0])
        self.match_attributes = binary_con(data[0])
        self.min_count = data[1]
        atk = multi_floor(data[2])
        shield = mult(data[3])
        super().__init__(182, ms, atk=atk, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.mass_match_convert(self)


class DualThresholdBoost(LeaderSkill):
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

    def text(self, converter: LsTextConverter) -> str:
        return converter.dual_threshold_stats_convert(self)


class BonusTimeStatBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 0, 100, 100, 100])
        self.time = mult(data[0])
        self.attributes = binary_con(data[1])
        self.types = binary_con(data[2])
        hp = multi_floor(data[3])
        atk = multi_floor(data[4])
        rcv = multi_floor(data[5])
        super().__init__(185, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.bonus_time_convert(self)


class SevenBySixStatBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 100, 100])
        self.attributes = binary_con(data[0])
        self.types = binary_con(data[1])
        self.tags = [Tag.BOARD_7X6]
        hp = multi_floor(data[2])
        atk = multi_floor(data[3])
        rcv = multi_floor(data[4])
        super().__init__(186, ms, hp=hp, atk=atk, rcv=rcv)

    def text(self, converter: LsTextConverter) -> str:
        return converter.passive_stats_convert(self)


class BlobMatchBonusCombo(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 0, 100, 0])
        self.attributes = binary_con(data[0])
        self.min_match = data[1]
        self.bonus_combo = data[3]
        atk = multi_floor(data[2])
        super().__init__(192, ms, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.multi_mass_match_convert(self)


class LMatchBoost(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 100, 0])
        self.attributes = binary_con(data[0])
        atk = multi_floor(data[1])
        rcv = multi_floor(data[2])
        shield = mult(data[3])
        super().__init__(193, ms, atk=atk, rcv=rcv, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.l_match_convert(self)


class AttrMatchBonusCombo(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = binary_con(data[0])
        self.min_attr = data[1]
        self.bonus_combo = data[3]
        atk = multi_floor(data[2])
        super().__init__(194, ms, atk=atk)

    def text(self, converter: LsTextConverter) -> str:
        return converter.add_combo_att_convert(self)


class DisablePoisonEffects(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        self.tags = [Tag.DISABLE_POISON]
        super().__init__(197, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.tag_only_convert(self)


class HealMatchBoostUnbind(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = merge_defaults(ms.data, [0, 100, 0, 0])
        self.heal_amt = data[0]
        self.unbind_amt = data[3]
        atk = multi_floor(data[1])
        shield = mult(data[2])
        super().__init__(198, ms, atk=atk, shield=shield)

    def text(self, converter: LsTextConverter) -> str:
        return converter.orb_heal_convert(self)


class RainbowBonusDamage(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = binary_con(data[0])
        self.min_attr = data[1]
        self.bonus_damage = data[2]
        super().__init__(199, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.rainbow_bonus_damage_convert(self)


class BlobBonusDamage(LeaderSkill):
    def __init__(self, ms: MonsterSkill):
        data = ms.data
        self.attributes = binary_con(data[0])
        self.min_match = data[1]
        self.bonus_damage = data[2]
        super().__init__(200, ms)

    def text(self, converter: LsTextConverter) -> str:
        return converter.mass_match_bonus_damage_convert(self)


def convert(skill_list: List[MonsterSkill]):
    results = {}
    for s in skill_list:
        try:
            ns = convert_skill(s)
            if ns:
                results[ns.skill_id] = ns
        except Exception as ex:
            print('Failed to convert', s.skill_type, ex)

    # Fills in TwoPartLeaderSkills
    for s in results.values():
        if not isinstance(s, TwoPartLeaderSkill):
            continue
        for p_id in s.child_ids:
            if p_id not in results:
                print('failed to look up skill id:', p_id)
                continue
            p_skill = results[p_id]
            s.child_skills.append(p_skill)

    return list(results.values())


# TODO: These ended up being 1:1, convert skill type to a class value, then
# load this mapping dynamically via list of skill classes
def convert_skill(s) -> Optional[LeaderSkill]:
    if s.skill_type == 11:
        return AttrAtkBoost(s)
    if s.skill_type == 12:
        return BonusAttack(s)
    if s.skill_type == 13:
        return Autoheal(s)
    if s.skill_type == 14:
        return Resolve(s)
    if s.skill_type == 15:
        return MovementTimeIncrease(s)
    if s.skill_type == 16:
        return DamageReduction(s)
    if s.skill_type == 17:
        return AttrDamageReduction(s)
    if s.skill_type == 22:
        return TypeAtkBoost(s)
    if s.skill_type == 23:
        return TypeHpBoost(s)
    if s.skill_type == 24:
        return TypeRcvBoost(s)
    if s.skill_type == 26:
        return StaticAtkBoost(s)
    if s.skill_type == 28:
        return AttrAtkRcvBoost(s)
    if s.skill_type == 29:
        return AllStatBoost(s)
    if s.skill_type == 30:
        return TwoTypeHpBoost(s)
    if s.skill_type == 31:
        return TwoTypeAtkBoost(s)
    if s.skill_type == 33:
        return TaikoDrum(s)
    if s.skill_type == 36:
        return TwoAttrDamageReduction(s)
    if s.skill_type == 38:
        return LowHpShield(s)
    if s.skill_type == 39:
        return LowHpAtkOrRcvBoost(s)
    if s.skill_type == 40:
        return TwoAttrAtkBoost(s)
    if s.skill_type == 41:
        return Counterattack(s)
    if s.skill_type == 43:
        return HighHpShield(s)
    if s.skill_type == 44:
        return HighHpAtkBoost(s)
    if s.skill_type == 45:
        return AttrAtkHpBoost(s)
    if s.skill_type == 46:
        return TwoAttrHpBoost(s)
    if s.skill_type == 48:
        return AttrHpBoost(s)
    if s.skill_type == 49:
        return AttrRcvBoost(s)
    if s.skill_type == 53:
        return EggDropRateBoost(s)
    if s.skill_type == 54:
        return CoinDropBoost(s)
    if s.skill_type == 61:
        return Rainbow(s)
    if s.skill_type == 62:
        return TypeHpAtkBoost(s)
    if s.skill_type == 63:
        return TypeHpRcvBoost(s)
    if s.skill_type == 64:
        return TypeAtkRcvBoost(s)
    if s.skill_type == 65:
        return TypeAllStatBoost(s)
    if s.skill_type == 66:
        return ComboFlatMultiplier(s)
    if s.skill_type == 67:
        return AttrHpRcvBoost(s)
    if s.skill_type == 69:
        return AttrTypeAtkBoost(s)
    if s.skill_type == 73:
        return AttrTypeHpAtkBoost(s)
    if s.skill_type == 75:
        return AttrTypeAtkRcvBoost(s)
    if s.skill_type == 76:
        return AttrTypeAllStatBoost(s)
    if s.skill_type == 77:
        return TwoTypeHpAtkBoost(s)
    if s.skill_type == 79:
        return TwoTypeAtkRcvBoost(s)
    if s.skill_type == 94:
        return LowHpConditionalAttrAtkBoost(s)
    if s.skill_type == 95:
        return LowHpConditionalTypeAtkBoost(s)
    if s.skill_type == 96:
        return HighHpConditionalAttrAtkBoost(s)
    if s.skill_type == 97:
        return HighHpConditionalTypeAtkBoost(s)
    if s.skill_type == 98:
        return ComboScaledMultiplier(s)
    if s.skill_type == 100:
        return SkillActivationAtkRcvBoost(s)
    if s.skill_type == 101:
        return AtkBoostWithExactCombos(s)
    if s.skill_type == 103:
        return ComboFlatAtkRcvBoost(s)
    if s.skill_type == 104:
        return ComboFlatMultiplierAttrAtkBoost(s)
    if s.skill_type == 105:
        return ReducedRcvAtkBoost(s)
    if s.skill_type == 106:
        return ReducedHpAtkBoost(s)
    if s.skill_type == 107:
        return HpReduction(s)
    if s.skill_type == 108:
        return ReducedHpTypeAtkBoost(s)
    if s.skill_type == 109:
        return BlobFlatAtkBoost(s)
    if s.skill_type == 111:
        return TwoAttrHpAtkBoost(s)
    if s.skill_type == 114:
        return TwoAttrAllStatBoost(s)
    if s.skill_type == 119:
        return BlobScalingAtkBoost(s)
    if s.skill_type == 121:
        return AttrOrTypeStatBoost(s)
    if s.skill_type == 122:
        return LowHpConditionalAttrTypeAtkRcvBoost(s)
    if s.skill_type == 123:
        return HighHpConditionalAttrTypeAtkRcvBoost(s)
    if s.skill_type == 124:
        return AttrComboScalingAtkBoost(s)
    if s.skill_type == 125:
        return TeamUnitConditionalStatBoost(s)
    if s.skill_type == 129:
        return MultiAttrTypeStatBoost(s)
    if s.skill_type == 130:
        return LowHpAttrAtkStatBoost(s)
    if s.skill_type == 131:
        return HighHpAttrTypeStatBoost(s)
    if s.skill_type == 133:
        return SkillUsedAttrTypeAtkRcvBoost(s)
    if s.skill_type == 136:
        return MultiAttrConditionalStatBoost(s)
    if s.skill_type == 137:
        return MultiTypeConditionalStatBoost(s)
    if s.skill_type == 138:
        return TwoPartLeaderSkill(s)
    if s.skill_type == 139:
        return HpMultiConditionalAtkBoost(s)
    if s.skill_type == 148:
        return RankXpBoost(s)
    if s.skill_type == 149:
        return HealMatchRcvBoost(s)
    if s.skill_type == 150:
        return EnhanceOrbMatch5(s)
    if s.skill_type == 151:
        return HeartCross(s)
    if s.skill_type == 155:
        return Multiboost(s)
    if s.skill_type == 157:
        return AttrCross(s)
    if s.skill_type == 158:
        return MatchXOrMoreOrbs(s)
    if s.skill_type == 159:
        return AdvancedBlobMatch(s)
    if s.skill_type == 162:
        return SevenBySix(s)
    if s.skill_type == 163:
        return NoSkyfallBoost(s)
    if s.skill_type == 164:
        return AttrComboConditionalAtkRcvBoost(s)
    if s.skill_type == 165:
        return RainbowAtkRcv(s)
    if s.skill_type == 166:
        return AtkRcvComboScale(s)
    if s.skill_type == 167:
        return BlobAtkRcvBoost(s)
    if s.skill_type == 169:
        return ComboMultPlusShield(s)
    if s.skill_type == 170:
        return RainbowMultPlusShield(s)
    if s.skill_type == 171:
        return MatchAttrPlusShield(s)
    if s.skill_type == 175:
        return CollabConditionalBoost(s)
    if s.skill_type == 177:
        return OrbRemainingMultiplier(s)
    if s.skill_type == 178:
        return FixedMovementTime(s)
    if s.skill_type == 182:
        return RowMatcHPlusDamageReduction(s)
    if s.skill_type == 183:
        return DualThresholdBoost(s)
    if s.skill_type == 185:
        return BonusTimeStatBoost(s)
    if s.skill_type == 186:
        return SevenBySixStatBoost(s)
    if s.skill_type == 192:
        return BlobMatchBonusCombo(s)
    if s.skill_type == 193:
        return LMatchBoost(s)
    if s.skill_type == 194:
        return AttrMatchBonusCombo(s)
    if s.skill_type == 197:
        return DisablePoisonEffects(s)
    if s.skill_type == 198:
        return HealMatchBoostUnbind(s)
    if s.skill_type == 199:
        return RainbowBonusDamage(s)
    if s.skill_type == 200:
        return BlobBonusDamage(s)

    return None
