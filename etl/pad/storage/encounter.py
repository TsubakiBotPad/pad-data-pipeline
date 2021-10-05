from typing import List

from pad.common.shared_types import MonsterId
from pad.db.sql_item import SimpleSqlItem, ExistsStrategy
from pad.dungeon.wave_converter import ResultSlot


class Encounter(SimpleSqlItem):
    """A monster that appears in a dungeon."""
    TABLE = 'encounters'
    KEY_COL = 'encounter_id'

    def __init__(self,
                 encounter_id: int = None,
                 dungeon_id: int = None,
                 sub_dungeon_id: int = None,
                 enemy_id: int = None,
                 monster_id: int = None,
                 stage: int = None,
                 amount: int = None,
                 order_idx: int = None,
                 turns: int = None,
                 level: int = None,
                 hp: int = None,
                 atk: int = None,
                 defence: int = None,
                 exp: int = None,
                 tstamp: int = None):
        self.encounter_id = encounter_id
        self.dungeon_id = dungeon_id
        self.sub_dungeon_id = sub_dungeon_id
        self.enemy_id = enemy_id
        self.monster_id = monster_id
        self.stage = stage
        self.amount = amount
        self.order_idx = order_idx
        self.turns = turns
        self.level = level
        self.hp = hp
        self.atk = atk
        self.defence = defence
        self.exp = exp
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_KEY_IF_SET

    def __str__(self):
        return 'Encounter({}): {} -> {} [{}, {}, {}]'.format(self.key_value(), self.sub_dungeon_id, self.enemy_id,
                                                             self.stage, self.monster_id, self.level)


class Drop(SimpleSqlItem):
    """Dungeon monster drop."""
    TABLE = 'drops'
    KEY_COL = 'drop_id'

    @staticmethod
    def from_slot(o: ResultSlot, e: Encounter) -> List['Drop']:
        results = []
        for drop_card in o.drops:
            results.append(Drop(encounter_id=e.encounter_id,
                                monster_id=drop_card.monster_id))
        return results

    def __init__(self,
                 drop_id: int = None,
                 encounter_id: int = None,
                 monster_id: MonsterId = None,
                 tstamp: int = None):
        self.drop_id = drop_id
        self.encounter_id = encounter_id
        self.monster_id = monster_id
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]

    def __str__(self):
        return 'Drop({}): {} -> {}'.format(self.key_value(), self.encounter_id, self.monster_id)
