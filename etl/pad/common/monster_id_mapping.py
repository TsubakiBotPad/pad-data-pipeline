# Pad NA/JP don't have the exact same monster IDs for the same monster.
# We use JP ids as the monster number; NA-only cards are adjusted to a new range.
from pad.common.shared_types import MonsterNo, CardId


def between(n: int, bottom: int, top: int):
    return bottom <= n <= top


def adjust(n: CardId, local_bottom: int, remote_bottom: int) -> MonsterNo:
    return MonsterNo(n - local_bottom + remote_bottom)


def jp_id_to_monster_no(jp_id: CardId) -> MonsterNo:
    # We use JP IDs as the monster_no; no need to adjust.
    return MonsterNo(jp_id)


# Fixes for early collabs, and adjusting voltron to a new range.
def nakr_id_to_monster_no(na_id: CardId) -> MonsterNo:
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

    return MonsterNo(na_id)
