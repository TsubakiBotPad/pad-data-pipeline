# Pad NA/JP don't have the exact same monster IDs for the same monster.
# We use JP ids as the monster number; NA-only cards are adjusted to a new range.


def between(n: int, bottom: int, top: int):
    return bottom <= n <= top


def adjust(n: int, local_bottom: int, remote_bottom: int):
    return n - local_bottom + remote_bottom


def jp_id_to_monster_no(jp_id: int):
    jp_id = int(jp_id)

    # We use JP IDs as the monster_no; no need to adjust.
    return jp_id


# Fixes for early collabs, and adjusting voltron to a new range.
def na_id_to_monster_no(na_id: int):
    na_id = int(na_id)

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

    return na_id
