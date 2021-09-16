import json

from pad.common.monster_id_mapping import server_monster_id_fn
from pad.common.shared_types import Server
from pad.db.sql_item import SimpleSqlItem, ExistsStrategy
from pad.raw.extra_egg_machine import ExtraEggMachine


class EggMachine(SimpleSqlItem):
    """A per-server egg machine."""
    TABLE = 'egg_machines'
    KEY_COL = 'egg_machine_id'

    @staticmethod
    def from_eem(eem: ExtraEggMachine, server: Server) -> 'EggMachine':
        if eem.egg_machine_type == 1:  # REM
            egg_machine_type_id = 2
        elif eem.egg_machine_type == 2:  # PEM
            egg_machine_type_id = 1
        elif eem.egg_machine_type == 9:  # VEM
            egg_machine_type_id = 3
        else:  # Special (collab or other)
            egg_machine_type_id = 0

        id_mapper = server_monster_id_fn(server)
        content_map = {'({})'.format(id_mapper(k)): v for k, v in eem.contents.items()}
        contents = json.dumps(content_map, sort_keys=True)

        return EggMachine(
            egg_machine_id=None,  # Key that is looked up or inserted
            server_id=server.value,
            egg_machine_type_id=egg_machine_type_id,
            start_timestamp=eem.start_timestamp,
            end_timestamp=eem.end_timestamp,
            machine_row=eem.egg_machine_row,
            machine_type=eem.egg_machine_type,
            name=eem.clean_name,
            cost=eem.cost,
            contents=contents
        )

    def __init__(self,
                 egg_machine_id: int = None,
                 server_id: int = None,
                 egg_machine_type_id: int = None,
                 start_timestamp: int = None,
                 end_timestamp: int = None,
                 machine_row: int = None,
                 machine_type: int = None,
                 name: str = None,
                 cost: int = None,
                 contents: str = None,
                 tstamp: int = None):
        self.egg_machine_id = egg_machine_id
        self.server_id = server_id
        self.egg_machine_type_id = egg_machine_type_id
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.machine_row = machine_row
        self.machine_type = machine_type
        self.name = name
        self.cost = cost
        self.contents = contents
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]

    def _lookup_columns(self):
        return ['server_id', 'machine_row', 'machine_type']

    def __str__(self):
        return 'EggMachine ({}-{}-{}): {} [{}]'.format(self.server_id, self.machine_row, self.machine_type,
                                                       self.name, len(self.contents))
