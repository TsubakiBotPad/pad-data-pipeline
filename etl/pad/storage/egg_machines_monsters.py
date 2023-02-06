from pad.db.sql_item import SimpleSqlItem


class EggMachinesMonster(SimpleSqlItem):
    """Monsters that appear in each egg_machine"""
    TABLE = 'egg_machines_monsters'
    KEY_COL = {'monster_id', 'server_id', 'machine_row', 'machine_type'}

    def __init__(self,
                 monster_id: int = None,
                 roll_chance: float = None,
                 server_id: int = None,
                 machine_row: int = None,
                 machine_type: int = None,
                 ):
        self.monster_id = monster_id
        self.roll_chance = roll_chance
        self.server_id = server_id
        self.machine_row = machine_row
        self.machine_type = machine_type

    def __str__(self):
        return 'EggMachineMonster ({}-{}-{})'.format(self.monster_id, self.roll_chance, self.egg_machine_id)
