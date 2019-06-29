import time
from collections import defaultdict
from typing import Dict, Any, List

from pad.common import dungeon_types
from pad.raw_processor.crossed_data import CrossServerDatabase


def extract_active_dungeons(csd: CrossServerDatabase):
    active_dungeons = []
    # Extract normals/techs.
    values_5 = defaultdict(list)
    values_6 = defaultdict(list)
    for dungeon in csd.dungeons:

        # Skip the tutorial normals.
        if dungeon.jp_dungeon.one_time:
            continue
        if dungeon.jp_dungeon.full_dungeon_type in [dungeon_types.RawDungeonType.NORMAL,
                                                    dungeon_types.RawDungeonType.TECHNICAL]:
            active_dungeons.append(dungeon)
    return active_dungeons

# TODO: logic needs review / updates to used typed fields

# def filter_current_bonuses(
#     merged_bonuses:  Dict[str, Any],
#     filter_group: str,
#     include_normals: bool=False,
#     include_multiplayer: bool=False) -> [Dict[str, Any]]:
#     """Filters the processed/merged bonus list for active items.
#     merged_bonuses is the json representation of MergedBonus.
#     Output is a list of json representations of data/Dungeon.
#     filter_group is used to exclude guerrillas not applicable to the account
#     include_normals (not supported) adds normal/technical dungeons
#     include_multiplayer adds multiplayer dungeons (not sure if we can access those)
#     """
#     dungeon_list = []
#
#     current_time = int(time.time())
#     for merged_bonus in merged_bonuses:
#         start_time = int(merged_bonus['start_timestamp'])
#         end_time = int(merged_bonus['end_timestamp'])
#         if current_time < start_time or current_time > end_time:
#             # Bonus not currently live
#             continue
#
#         group = merged_bonus['group']
#         if group and group.lower() != filter_group.lower():
#             # Ignore guerrillas for other groups, or if filter not specified
#             continue
#
#         bonus = merged_bonus['bonus']
#         bonus_name = bonus['bonus_name']
#         #if bonus_name not in ['dungeon', 'daily_dragons']:
#         # TODO: fix daily dragons, probably need to check week day
#         if bonus_name not in ['dungeon']:
#             # These are the only events with dungeons that we're interested in
#             continue
#
#         dungeon = merged_bonus['dungeon']
#         if not dungeon:
#             # Shouldn't happen, but skip bonuses here without dungeons
#             print('error, expected a dungeon for:', bonus)
#             continue
#
#         if not include_multiplayer:
#             dungeon_comment_value  = int(dungeon['dungeon_comment_value'])
#             if dungeon_comment_value in range(600000, 700000):
#                 # Skip multiplayer dungeons
#                 continue
#
#         dungeon_list.append(dungeon)
#
#         # TODO: implement include_normals
#
#     return dungeon_list
