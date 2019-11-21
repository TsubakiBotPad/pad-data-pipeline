# Pad NA/JP don't have the exact same monster IDs for the same monster.
# We use JP ids as the monster number; NA-only cards are adjusted to a new range.
from pad.common.shared_types import MonsterId, MonsterNo


def between(n: int, bottom: int, top: int):
    return bottom <= n <= top


def adjust(n: MonsterNo, local_bottom: int, remote_bottom: int) -> MonsterId:
    return MonsterId(n - local_bottom + remote_bottom)


def jp_no_to_monster_id(jp_id: MonsterNo) -> MonsterId:
    # We use JP IDs as the monster_no; no need to adjust.
    return MonsterId(jp_id)


# Fixes for early collabs, and adjusting voltron to a new range.
def nakr_no_to_monster_id(na_id: MonsterNo) -> MonsterId:
    if na_id > 99_999:
        sub_id = MonsterNo(na_id % 100_000)
        na_id -= sub_id
        na_id += _nakr_no_to_monster_id(sub_id)
    else:
        na_id = _nakr_no_to_monster_id(na_id)

    return MonsterId(na_id)


def _nakr_no_to_monster_id(na_id: MonsterNo) -> MonsterId:
    # Shinra Bansho 1
    if between(na_id, 934, 935):
        return adjust(na_id, 934, 669)

    # Shinra Bansho 2
    if between(na_id, 1049, 1058):
        return adjust(na_id, 1049, 671)

    # Batman 1
    if between(na_id, 669, 680):
        return adjust(na_id, 669, 924)

    # Batman 2
    if between(na_id, 924, 933):
        return adjust(na_id, 924, 1049)

    # Voltron
    if between(na_id, 2601, 2631):
        return adjust(na_id, 2601, 2601 + 10000)

    # Power Rangers
    if between(na_id, 4949, 4987):
        return adjust(na_id, 4949, 4949 + 10000)

    return MonsterId(na_id)
