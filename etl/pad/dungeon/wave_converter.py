from collections import defaultdict
from statistics import mean
from typing import List, Set, Optional

from pad.common import monster_id_mapping
from pad.common.shared_types import Server, MonsterId
from pad.raw import Card
from pad.raw_processor.crossed_data import CrossServerDatabase
from pad.storage.wave import WaveItem


class WaveCard(object):
    def __init__(self,
                 monster_id: MonsterId,
                 card: Card,
                 wave_item: WaveItem,
                 drop_card: Card):
        self.monster_id = monster_id
        self.card = card
        self.wave_item = wave_item
        self.drop_card = drop_card


class ProcessedFloor(object):
    def __init__(self):
        self.invades = None
        self.stages = []

        self.entry_count = 0
        self.coins = []
        self.exp = []
        self.mp = []

    def add_entry(self, entry_waves: List[WaveCard]):
        """Computes stats across an individual dungeon entry."""
        entry_coins = 0
        xp = 0
        entry_mp = 0

        for wave_card in entry_waves:
            enemy_data = wave_card.card.enemy()
            enemy_level = wave_card.wave_item.monster_level

            entry_coins += wave_card.wave_item.get_coins()
            entry_coins += enemy_data.coin.value_at(enemy_level)
            xp += enemy_data.xp.value_at(enemy_level)

            if wave_card.drop_card:
                entry_mp += wave_card.drop_card.sell_mp

        self.entry_count += 1
        self.coins.append(entry_coins)
        self.exp.append(xp)
        self.mp.append(entry_mp)


class ProcessedStage(object):
    def __init__(self, stage_idx):
        self.stage_idx = stage_idx
        self.count = 0

        # TODO: drop rates

        self.spawn_to_drop = defaultdict(set)
        self.spawn_to_level = {}
        self.spawn_to_slot = defaultdict(set)
        self.spawn_to_count_list = defaultdict(list)
        self.spawns_per_wave = []

    def add_wave_group(self, entry_waves: List[WaveCard]):
        """Update stage info with a single entry-wave set of data."""
        self.count += 1
        self.spawns_per_wave.append(len(entry_waves))

        count_map = defaultdict(int)
        for wave_card in entry_waves:
            monster_id = wave_card.monster_id
            wave_item = wave_card.wave_item
            drop = wave_card.drop_card
            if drop:
                self.spawn_to_drop[monster_id].add(drop)

            self.spawn_to_level[monster_id] = wave_item.monster_level
            self.spawn_to_slot[monster_id].add(wave_item.slot)
            count_map[monster_id] += 1

        for monster_id, count in count_map.items():
            self.spawn_to_count_list[monster_id].append(count)


class ResultFloor(object):
    def __init__(self, floor: ProcessedFloor):
        self.stages = []
        if floor.invades:
            self.stages.append(ResultStage(floor.invades))
        self.stages.extend([ResultStage(s) for s in floor.stages])

        self.coins_min = min(floor.coins) if floor.coins else 0
        self.coins_max = max(floor.coins) if floor.coins else 0
        self.coins_avg = mean(floor.coins) if floor.coins else 0
        self.exp_min = min(floor.exp) if floor.exp else 0
        self.exp_max = max(floor.exp) if floor.exp else 0
        self.exp_avg = mean(floor.exp) if floor.exp else 0
        self.mp_avg = mean(floor.mp) if floor.mp else 0

    def boss_monster_id(self) -> Optional[MonsterId]:
        if not self.stages:
            return None
        final_stage = self.stages[-1]
        if not final_stage.slots:
            return None
        return max(final_stage.slots, key=lambda m: m.monster_id).visible_monster_id()


class ResultStage(object):
    def __init__(self, processed_stage: ProcessedStage):
        self.stage_idx = processed_stage.stage_idx
        self.slots = []

        # Chunk the spawns into fixed (always a specific number on the floor) or
        # random (varying number on the floor).
        fixed_spawns = []
        random_spawns = []
        for spawn, count_list in processed_stage.spawn_to_count_list.items():
            always_present = len(count_list) == processed_stage.count
            always_equal = max(count_list) == min(count_list)
            if always_present and always_equal:
                fixed_spawns.append(spawn)
            else:
                random_spawns.append(spawn)

        # Fixed spawns can be more than one too.
        for spawn in fixed_spawns:
            level = processed_stage.spawn_to_level[spawn]
            drops = processed_stage.spawn_to_drop[spawn]
            order = min(processed_stage.spawn_to_slot[spawn])
            count = processed_stage.spawn_to_count_list[spawn][0]
            self.slots.append(ResultSlot(spawn, level, order, drops,
                                         True, count, count))

        # Random spawns guess the amount based on the min/max wave size diff'ed
        # against the fixed spawn count.
        if random_spawns:
            wave_sizes = processed_stage.spawns_per_wave
            fixed_spawn_count = sum(s.min_spawn for s in self.slots)
            min_random_spawns = min(wave_sizes) - fixed_spawn_count
            max_random_spawns = max(wave_sizes) - fixed_spawn_count
            for spawn in random_spawns:
                level = processed_stage.spawn_to_level[spawn]
                drops = processed_stage.spawn_to_drop[spawn]
                order = min(processed_stage.spawn_to_slot[spawn])
                self.slots.append(ResultSlot(spawn, level, order, drops,
                                             False, min_random_spawns, max_random_spawns))


class ResultSlot(object):
    def __init__(self,
                 monster_id: MonsterId,
                 monster_level: int,
                 order: int,
                 drops: Set[int],
                 always_spawns: bool,
                 min_spawn: int,
                 max_spawn: int):
        self.monster_id = monster_id
        self.monster_level = monster_level
        self.order = order
        self.drops = drops
        self.always_spawns = always_spawns
        self.min_spawn = min_spawn
        self.max_spawn = max_spawn

    def visible_monster_id(self) -> MonsterId:
        return MonsterId(self.monster_id % 100000)


class WaveConverter(object):
    def __init__(self, data: CrossServerDatabase):
        self.data = data

    def convert(self, wave_items: List[WaveItem]) -> ResultFloor:
        result = ProcessedFloor()

        waves_by_entry = defaultdict(list)
        waves_by_stage_and_entry = defaultdict(lambda: defaultdict(list))
        for wave_item in wave_items:
            # Correct for NA server mappings if necessary
            monster_id = wave_item.monster_id
            drop_id = wave_item.get_drop()
            if wave_item.server != Server.jp:
                monster_id = monster_id_mapping.nakr_no_to_monster_id(monster_id)
                if drop_id:
                    drop_id = monster_id_mapping.nakr_no_to_monster_id(drop_id)

            # Build a structure that merges DB info with wave data.
            card = self.data.card_by_monster_id(monster_id).jp_card
            drop = self.data.card_by_monster_id(drop_id).jp_card if drop_id else None
            wave_card = WaveCard(monster_id, card, wave_item, drop)

            # Store data for an individual dungeon entry.
            waves_by_entry[wave_item.entry_id].append(wave_card)

            # Store data for each stage, separated by dungeon entry.
            waves_by_stage_and_entry[wave_item.stage][wave_item.entry_id].append(wave_card)

        # Calculate stuff that should be done per-entry instead of per-floor. This more
        # correctly handles invades and alternate spawns.
        for entry_waves in waves_by_entry.values():
            result.add_entry(entry_waves)

        # Calculate stuff at a per-stage level, like spawns and drops.
        invades = ProcessedStage(0)
        stages = [ProcessedStage(i + 1) for i in sorted(waves_by_stage_and_entry.keys())]
        last_stage_idx = stages[-1].stage_idx
        for stage in stages:
            waves_for_stage = waves_by_stage_and_entry[stage.stage_idx]

            for entry_waves in waves_for_stage:
                if stage.stage_idx != last_stage_idx and entry_waves[0].is_invade():
                    # Invades happen only on non-boss floors
                    invades.add_wave_group(entry_waves)
                else:
                    stage.add_wave_group(entry_waves)

        if invades.count:
            result.invades = invades

        result.stages.extend(stages)

        return ResultFloor(result)
