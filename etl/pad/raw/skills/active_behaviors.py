import json
from typing import Any, List, NamedTuple, TYPE_CHECKING


class ASBehavior(NamedTuple):
    # This doesn't actually work bc of the way namedtuples are created.
    # TODO: Fix this so we can have a nice superclass
    _root = True
    behavior_type = 'undefined'


class ASBOrbChange(ASBehavior):
    behavior_type = 'orb_change'

    from_orbs: List[int]
    to_orbs: List[int]
    amount: int = 999
    from_invert: bool = False


# Temporary fix
ASBehavior = Any


def behavior_to_json(behavior: List[ASBehavior]) -> List[dict]:
    return [{'behavior_type': asb.behavior_type, 'properties': asb._asdict()} for asb in behavior]
