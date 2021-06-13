from pad.db import sql_item
from pad.db.sql_item import SimpleSqlItem, ExistsStrategy


class EggMachinesMonster(SimpleSqlItem):
    "Monsters that appear in each egg_machine"
    TABLE = 'egg_machines_monsters'
    KEY_COL = 'egg_machine_monster_id'

    def __init__(self,
                 egg_machine_monster_id: int = None,
                 monster_id: int = None,
                 roll_chance: float = None,
                 egg_machine_id: int = None):
        self.egg_machine_monster_id = egg_machine_monster_id
        self.monster_id = monster_id
        self.roll_chance = roll_chance
        self.egg_machine_id = egg_machine_id

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def value_exists_sql(self):
        sql = """
        SELECT egg_machine_monster_id FROM {table}
        WHERE monster_id = {monster_id} AND egg_machine_id = {egg_machine_id}
        """.format(table=self._table(), **sql_item.object_to_sql_params(self))
        return sql

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]

    def __str__(self):
        return 'EggMachineMonster ({}-{}-{}-{})'.format(self.egg_machine_monster_id, self.monster_id, self.roll_chance,
                                                        self.egg_machine_id)
