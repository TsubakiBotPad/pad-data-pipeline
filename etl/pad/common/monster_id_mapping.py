# Pad NA/JP don't have the exact same monster IDs for the same monster.
# We use JP ids as the monster number; NA-only cards are adjusted to a new range.
from functools import wraps
from typing import Callable

from pad.common.shared_types import MonsterId, MonsterNo, Server

NA_ONLY_OFFSET = 50_000


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


def alt_no_to_monster_id(no_converter: Callable[[MonsterNo], MonsterId]) \
        -> Callable[[MonsterNo], MonsterId]:
    @wraps(no_converter)
    def convert_alt_no(mno: MonsterNo):
        if mno > 99999:
            sub_id = MonsterNo(mno % 100_000)
            mno -= sub_id
            mno += no_converter(sub_id)
        else:
            mno = no_converter(mno)

        return MonsterId(mno)
    return convert_alt_no


@alt_no_to_monster_id
def jp_no_to_monster_id(jp_no: MonsterNo) -> MonsterId:
    # Ghost numbers for coins and other special drops
    if jp_no > 10_000:
        jp_no -= 100
    return MonsterId(jp_no)


@alt_no_to_monster_id
def na_no_to_monster_id(na_no: MonsterNo) -> MonsterId:
    # Ghost numbers for coins and other special drops
    if na_no > 10_000:
        na_no -= 100

    # Shinra Bansho 1
    if between(na_no, 934, 935):
        return adjust(na_no, 934, 669)

    # Shinra Bansho 2
    if between(na_no, 1049, 1058):
        return adjust(na_no, 1049, 671)

    # Batman 1
    if between(na_no, 669, 680):
        return adjust(na_no, 669, 924)

    # Batman 2
    if between(na_no, 924, 933):
        return adjust(na_no, 924, 1049)

    # Voltron
    if between(na_no, 2601, 2631):
        return adjust(na_no, 2601, 2601 + NA_ONLY_OFFSET)

    # Power Rangers
    if between(na_no, 4949, 4987):
        return adjust(na_no, 4949, 4949 + NA_ONLY_OFFSET)

    # GungHo: Another Story
    if between(na_no, 6905, 6992):
        return adjust(na_no, 6905, 6905 + NA_ONLY_OFFSET)

    # GungHo: Another Story 2
    if between(na_no, 9090, 9130):
        return adjust(na_no, 9090, 9090 + NA_ONLY_OFFSET)

    return MonsterId(na_no)


@alt_no_to_monster_id
def kr_no_to_monster_id(kr_no: MonsterNo) -> MonsterId:
    # Ghost numbers for coins and other special drops
    if kr_no > 10_000:
        kr_no -= 100

    # Shinra Bansho 1
    if between(kr_no, 934, 935):
        return adjust(kr_no, 934, 669)

    # Shinra Bansho 2
    if between(kr_no, 1049, 1058):
        return adjust(kr_no, 1049, 671)

    # Batman 1
    if between(kr_no, 669, 680):
        return adjust(kr_no, 669, 924)

    # Batman 2
    if between(kr_no, 924, 933):
        return adjust(kr_no, 924, 1049)

    # Voltron
    if between(kr_no, 2601, 2631):
        return adjust(kr_no, 2601, 2601 + NA_ONLY_OFFSET)

    # GungHo: Another Story
    if between(kr_no, 6905, 6992):
        return adjust(kr_no, 6905, 6905 + NA_ONLY_OFFSET)

    # GungHo: Another Story 2
    if between(kr_no, 9090, 9130):
        return adjust(kr_no, 9090, 9090 + NA_ONLY_OFFSET)

    return MonsterId(kr_no)
