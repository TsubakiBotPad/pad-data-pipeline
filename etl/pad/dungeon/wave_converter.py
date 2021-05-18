from collections import defaultdict
from statistics import mean
from typing import List, Set, Optional, Dict

from pad.common.shared_types import MonsterId
from pad.raw_processor.crossed_data import CrossServerDatabase, CrossServerCard
from pad.storage.wave import WaveItem


class WaveCard(object):
    def __init__(self,
                 monster_id: MonsterId,
                 card: CrossServerCard,
                 wave_item: WaveItem,
                 drop_card: CrossServerCard):
        self.monster_id = monster_id
        self.card = card
        self.wave_item = wave_item
        self.drop_card = drop_card


class ProcessedFloor(object):
    def __init__(self):
        self.invades = None  # Type: Optional[ProcessedStage]
        self.common_monsters = None  # Type: Optional[ProcessedStage]
        self.stages = []  # Type: List[ProcessedStage]

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
            enemy_data = wave_card.card.cur_card.card.enemy()
            enemy_level = wave_card.wave_item.monster_level

            entry_coins += wave_card.wave_item.get_coins()
            entry_coins += enemy_data.coin.value_at(enemy_level)
            xp += enemy_data.xp.value_at(enemy_level)

            if wave_card.drop_card:
                entry_mp += wave_card.drop_card.cur_card.card.sell_mp

        self.entry_count += 1
        self.coins.append(entry_coins)
        self.exp.append(xp)
        self.mp.append(entry_mp)


class ProcessedStage(object):
    INVADE_IDX = -1
    COMMON_IDX = 0

    def __init__(self, stage_idx):
        self.stage_idx = stage_idx
        self.count = 0

        # TODO: drop rates

        self.spawn_to_drop = defaultdict(set)
        # Typically monsters spawn at a fixed level, but in rare cases (some newer superhard descends)
        # floors spawn the same monster with multiple levels to proc different movesets.
        self.spawn_to_level = defaultdict(set)  # type: Dict[MonsterId, Set[int]]
        self.spawn_to_slot = defaultdict(set)  # type: Dict[MonsterId, Set[int]]
        self.spawn_to_count_list = defaultdict(list)  # type: Dict[MonsterId, List[WaveItem]]
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

            self.spawn_to_level[monster_id].add(wave_item.monster_level)
            self.spawn_to_slot[monster_id].add(wave_item.slot)
            count_map[monster_id] += 1

        for monster_id, count in count_map.items():
            self.spawn_to_count_list[monster_id].append(count)


class ResultFloor(object):
    def __init__(self, floor: ProcessedFloor, try_common_monsters):
        self.stages = []
        if floor.invades:
            self.stages.append(ResultStage(floor.invades))

        result_stages = [ResultStage(s) for s in floor.stages]

        if try_common_monsters:
            # For Normal and Technical dungeons, minimize the stages we output by sticking a
            # 'common monsters' floor at the start.
            common_slots = []  # type List[ResultSlot]

            # Find the stages that seem to have common slots vs the ones that are fixed
            for stage in result_stages:
                if not any([s.always_spawns for s in stage.slots]):
                    common_slots.extend(stage.slots)
                else:
                    self.stages.append(stage)

            if common_slots:
                # If we found any common slots, insert a fake record for it.
                monster_id_to_adjusted_slot = {}
                for slot in common_slots:
                    if slot.monster_id not in monster_id_to_adjusted_slot:
                        slot.max_spawn = None
                        slot.min_spawn = None
                        slot.order = slot.visible_monster_id()
                        slot.always_spawns = False
                        monster_id_to_adjusted_slot[slot.monster_id] = slot
                    # Always update drops
                    monster_id_to_adjusted_slot[slot.monster_id].drops.update(slot.drops)

                common_result_stage = ResultStage(ProcessedStage(ProcessedStage.COMMON_IDX))
                common_result_stage.slots = list(monster_id_to_adjusted_slot.values())
                self.stages.insert(0, common_result_stage)
        else:
            self.stages.extend(result_stages)

        def fix(i):
            return int(round(i))

        self.coins_min = fix(min(floor.coins)) if floor.coins else 0
        self.coins_max = fix(max(floor.coins)) if floor.coins else 0
        self.coins_avg = fix(mean(floor.coins)) if floor.coins else 0
        self.exp_min = fix(min(floor.exp)) if floor.exp else 0
        self.exp_max = fix(max(floor.exp)) if floor.exp else 0
        self.exp_avg = fix(mean(floor.exp)) if floor.exp else 0
        self.mp_avg = fix(mean(floor.mp)) if floor.mp else 0

    def boss_monster_id(self) -> Optional[MonsterId]:
        if not self.stages:
            return None
        final_stage = self.stages[-1]
        if not final_stage.slots:
            return None
        return max(map(lambda m: m.visible_monster_id(), final_stage.slots))


class ResultStage(object):
    def __init__(self, processed_stage: ProcessedStage):
        self.stage_idx = processed_stage.stage_idx
        self.slots = []  # type: List[ResultSlot]

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
            for level in processed_stage.spawn_to_level[spawn]:
                # Typically this loop only executes once
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
                for level in processed_stage.spawn_to_level[spawn]:
                    # Typically this loop only executes once
                    drops = processed_stage.spawn_to_drop[spawn]
                    order = min(processed_stage.spawn_to_slot[spawn])
                    self.slots.append(ResultSlot(spawn, level, order, drops,
                                                 False, min_random_spawns, max_random_spawns))


class ResultSlot(object):
    def __init__(self,
                 monster_id: MonsterId,
                 monster_level: int,
                 order: int,
                 drops: Set[CrossServerCard],
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

    def convert(self, wave_items: List[WaveItem], try_common_monsters: bool) -> ResultFloor:
        result = ProcessedFloor()

        waves_by_entry = defaultdict(list)
        waves_by_stage_and_entry = defaultdict(lambda: defaultdict(list))
        for wave_item in wave_items:
            monster_id = wave_item.monster_id
            drop_id = wave_item.get_drop()

            # Stuff in this range is supposedly:
            # 9900: coins
            # 9901: stones
            # 9902: pal points
            # 9911: gift dungeon
            # 9912: monster points
            # 9916: permanent dungeon
            # 9917: badge
            # 9999: announcement
            if drop_id and (9000 < drop_id < 10000):
                raise ValueError('Special drop detected (not handled yet)')

            # Build a structure that merges DB info with wave data.
            card = self.data.card_by_monster_id(monster_id)
            drop = self.data.card_by_monster_id(drop_id) if drop_id else None
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
        invades = ProcessedStage(ProcessedStage.INVADE_IDX)
        stages = [ProcessedStage(i + 1) for i in sorted(waves_by_stage_and_entry.keys())]
        last_stage_idx = stages[-1].stage_idx
        for stage in stages:
            waves_for_stage = waves_by_stage_and_entry[stage.stage_idx - 1]

            for entry_waves in waves_for_stage.values():
                if stage.stage_idx != last_stage_idx and entry_waves[0].wave_item.is_invade():
                    # Invades happen only on non-boss floors; some bosses represent as invades though.
                    invades.add_wave_group(entry_waves)
                else:
                    stage.add_wave_group(entry_waves)

        if invades.count:
            result.invades = invades

        result.stages.extend(stages)

        return ResultFloor(result, try_common_monsters)
