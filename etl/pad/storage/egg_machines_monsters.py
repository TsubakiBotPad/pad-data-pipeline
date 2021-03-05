from pad.db.sql_item import SimpleSqlItem


class EggMachinesMonster(SimpleSqlItem):
    "Monsters that appear in each egg_machine"
    TABLE = 'egg_machines_monsters'
    KEY_COL = 'emm_id'

    def __init__(self,
                 emm_id: int = None,
                 monster_id: int = None,
                 roll_chance: float = None,
                 egg_machine_id: int = None):
        self.emm_id = emm_id
        self.monster_id = monster_id
        self.roll_chance = roll_chance
        self.egg_machine_id = egg_machine_id

    def __str__(self):
        return 'EggMachineMonster ({}-{}-{}-{})'.format(self.emm_id, self.monster_id, self.roll_chance,
                                                        self.egg_machine_id)
