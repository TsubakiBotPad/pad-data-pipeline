from typing import Any, Dict, List, Literal, NamedTuple, Optional, TYPE_CHECKING, Union

from pad.raw.skills.behaviors.buffs import Buff, Debuff

if TYPE_CHECKING:
    from pad.raw.skills.active_skill_info import ActiveSkill


class ASBOrbChange(NamedTuple):
    from_orbs: List[int]
    to_orbs: List[int]
    amount: int = 999
    from_invert: bool = False

    behavior_type = 'orb_change'


class ASBBoardChange(NamedTuple):
    board_shape: List[List[int]]

    behavior_type = 'board_change'


class ASBDamage(NamedTuple):
    unit: Literal['flat',
                  'multiplier', 'team_multiplier', 'hp_multiplier', 'grudge_multiplier',
                  'gravity', 'true_gravity']
    amount: Union[int, float]
    min_damage: Optional[Union[int, float]] = None
    attribute: Optional[int] = None
    recover: float = 0.0

    mass_attack: bool = True
    laser: bool = False
    team_mult_attr: Optional[List[int]] = None

    target_attribute: Optional[int] = None

    behavior_type = 'damage'


class ASBRecover(NamedTuple):
    unit: str
    amount: Union[int, float]

    skill_bind: int = 0
    awoken_bind: int = 0
    match_bind: int = 0

    behavior_type = 'recover'


class ASBBuff(NamedTuple):
    buff_type: Literal['shield', 'stat_mult', 'counterattack', 'mass_attack', 'skyfall_chance',
                       'orb_movement', 'attribute_change', 'enemy_attribute_change', 'increase_combo',
                       'void', 'increase_skyfall', 'disable_skills', 'unmachable', 'autoheal',
                       'no_skyfall', 'spinner']
    turns: int
    details: Buff = {}

    behavior_type = 'buff'


class ASBInflictDebuff(NamedTuple):
    debuff_type: Literal['delay', 'guard_break', 'poison']
    details: Debuff = {}

    behavior_type = 'inflict_debuff'


class ASBSuperSkill:
    multi_type: str
    raw_subskills: List["ActiveSkill"]

    def __init__(self, multi_type, raw_subskills):
        self.multi_type = multi_type
        self.raw_subskills = raw_subskills

    def _asdict(self):
        return {'multi_type': self.multi_type, 'subskills': self.subskills}

    @property
    def subskills(self) -> List[List[Dict[str, Any]]]:
        return [behavior_to_json(ss.behavior) for ss in self.raw_subskills]

    behavior_type = 'multi_part'


def ASBCustom(_behavior_type: Literal['free_movement', 'orb_refresh', 'enhance', 'suicide',
                                      'leader_swap', 'skill_charge', 'lock', 'board_unlock',
                                      'show_path', 'transform', 'conditional', 'inflict_es'],
              fields=None, **kwargs):
    if fields is None:
        fields = {}
    fields.update(kwargs)

    class _ASBCustom:
        behavior_type = _behavior_type

        def _asdict(self):
            return fields

    return _ASBCustom()


ASBehavior = Any


def behavior_to_json(behavior: List[Any]) -> List[Dict[str, Any]]:
    return [{'behavior_type': asb.behavior_type, 'properties': asb._asdict()} for asb in behavior]
