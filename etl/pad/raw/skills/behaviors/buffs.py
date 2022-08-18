from typing import List, Literal, Tuple, TypedDict, Union


class TeamTarget(dict):
    attributes: List[int]
    types: List[int]
    target_bitmap: int


class Per(TypedDict):
    attributes: List[int]
    types: List[int]
    awakenings: List[int]


class Shield(TypedDict):
    strength: float
    attribute: List[int]


class StatMult(TypedDict):
    stats: Tuple[float, float, float]
    per: Per
    target: TeamTarget


class Counterattack(TypedDict):
    mult: float


class MassAttack(TypedDict):
    pass


class SkyfallChance(TypedDict):
    attributes: List[int]
    percentage: float


class OrbMovement(TypedDict):
    unit: Literal['flat', 'multiplier']
    amount: float


class AttributeChange(TypedDict):
    atribute: int
    target: TeamTarget


class EnemyAttributeChange(TypedDict):
    atribute: int


class IncreaseComb(TypedDict):
    additional_combos: int


class Void(TypedDict):
    damage_void: bool
    attribute_absorb: bool
    damage_absorb: bool


class IncreaseSkyfall(TypedDict):
    percentage: float
    attributes: List[int]
    type: Literal['enhanced', 'locked', 'nail']


class DisableSkills(TypedDict):
    pass


class Unmatchable(TypedDict):
    attributes: List[int]


class Autoheal(TypedDict):
    percentage: float


class NoSkyfall(TypedDict):
    pass


class Spinner(TypedDict):
    speed: float
    shape: List[List[int]]
    random_count: int


Buff = Union[Shield, StatMult, Counterattack, MassAttack, SkyfallChance, OrbMovement, AttributeChange,
             EnemyAttributeChange, IncreaseComb, Void, IncreaseSkyfall, DisableSkills, Unmatchable,
             Autoheal, NoSkyfall, Spinner]


class Delay(TypedDict):
    turns: int


class GuardBreak(TypedDict):
    percent: float


class Poison(TypedDict):
    mult: float


Debuff = Union[Delay, GuardBreak, Poison]
