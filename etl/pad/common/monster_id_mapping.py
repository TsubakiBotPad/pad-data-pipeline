# Pad NA/JP don't have the exact same monster IDs for the same monster.
# We use JP ids as the monster number; NA-only cards are adjusted to a new range.
from typing import Callable

from pad.common.shared_types import MonsterId, MonsterNo, Server


def between(n: int, bottom: int, top: int):
    return bottom <= n <= top


def adjust(n: MonsterNo, local_bottom: int, remote_bottom: int) -> MonsterId:
    return MonsterId(n - local_bottom + remote_bottom)


def server_monster_id_fn(server: Server) -> Callable[[MonsterNo], MonsterId]:
    if server == Server.jp:
        return jp_no_to_monster_id
    if server == Server.na:
        return na_no_to_monster_id
    if server == Server.kr:
        return kr_no_to_monster_id


def jp_no_to_monster_id(jp_id: MonsterNo) -> MonsterId:
    # We use JP IDs as the monster_no; no need to adjust.
    return MonsterId(jp_id)


# Fixes for early collabs, and adjusting voltron to a new range.
def na_no_to_monster_id(na_id: MonsterNo) -> MonsterId:
    if na_id > 99999:
        sub_id = MonsterNo(na_id % 100000)
        na_id -= sub_id
        na_id += _na_no_to_monster_id(sub_id)
    else:
        na_id = _na_no_to_monster_id(na_id)

    return MonsterId(na_id)


# Fixes for early collabs, and adjusting voltron to a new range.
def kr_no_to_monster_id(kr_id: MonsterNo) -> MonsterId:
    if kr_id > 99999:
        sub_id = MonsterNo(kr_id % 100000)
        kr_id -= sub_id
        kr_id += _kr_no_to_monster_id(sub_id)
    else:
        kr_id = _kr_no_to_monster_id(kr_id)

    return MonsterId(kr_id)


def _na_no_to_monster_id(na_id: MonsterNo) -> MonsterId:
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


def _kr_no_to_monster_id(kr_id: MonsterNo) -> MonsterId:
    # Shinra Bansho 1
    if between(kr_id, 934, 935):
        return adjust(kr_id, 934, 669)

    # Shinra Bansho 2
    if between(kr_id, 1049, 1058):
        return adjust(kr_id, 1049, 671)

    # Batman 1
    if between(kr_id, 669, 680):
        return adjust(kr_id, 669, 924)

    # Batman 2
    if between(kr_id, 924, 933):
        return adjust(kr_id, 924, 1049)

    # Voltron
    if between(kr_id, 2601, 2631):
        return adjust(kr_id, 2601, 2601 + 10000)

    return MonsterId(kr_id)
