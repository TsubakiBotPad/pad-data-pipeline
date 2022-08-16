from typing import Any, Dict, List, NamedTuple, Optional, TYPE_CHECKING, Union

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
    unit: str
    amount: Union[int, float]
    min_damage: Optional[Union[int, float]] = None
    attribute: Optional[int] = None
    recover: float = 0.0

    mass_attack: bool = True
    laser: bool = False
    grudge: bool = False
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
    buff_type: str
    turns: int
    details: Dict[str, Any] = {}

    behavior_type = 'buff'


class ASBInflictDebuff(NamedTuple):
    buff_type: str
    details: Dict[str, Any] = {}

    behavior_type = 'inflict_debuff'


class ASBSuperSkill(NamedTuple):
    multi_type: str
    _subskills: List["ActiveSkill"]

    def _asdict(self):
        return {'multi_type': self.multi_type, 'subskills': self.subskills}

    @property
    def subskills(self) -> List[List[Dict[str, Any]]]:
        return [behavior_to_json(ss.behavior) for ss in self._subskills]

    behavior_type = 'multi_part'


def ASBCustom(_behavior_type: str, fields=None, **kwargs) -> NamedTuple:
    if fields is None:
        fields = {}
    fields.update(kwargs)

    class _ASBCustom(NamedTuple):
        behavior_type = _behavior_type

        def _asdict(self):
            return fields

    return _ASBCustom()


ASBehavior = NamedTuple


def behavior_to_json(behavior: List[Any]) -> List[Dict[str, Any]]:
    return [{'behavior_type': asb.behavior_type, 'properties': asb._asdict()} for asb in behavior]
