from pad.common import monster_id_mapping
from pad.common.monster_id_mapping import server_monster_id_fn
from pad.common.shared_types import Server
from pad.db.sql_item import SqlItem
from pad.raw import wave as wave_data


class WaveItem(SqlItem):
    DROP_MONSTER_ID_GOLD = 9900
    TABLE = 'wave_data'
    KEY_COL = 'id'
    LIST_COL = 'dungeon_id'

    def __init__(self,
                 id: int = None,
                 pull_id: int = None,
                 entry_id: int = None,
                 server: str = None,
                 dungeon_id: int = None,
                 floor_id: int = None,
                 stage: int = None,
                 slot: int = None,
                 spawn_type: int = None,
                 monster_id: int = None,
                 monster_level: int = None,
                 drop_monster_id: int = None,
                 drop_monster_level: int = None,
                 plus_amount: int = None,
                 monster: wave_data.WaveMonster = None,
                 pull_time=None,  # Ignored
                 leader_id: int = None,
                 friend_id: int = None):
        self.id = id
        self.server = server
        self.dungeon_id = dungeon_id
        self.floor_id = floor_id  # ID starts at 1 for lowest
        self.stage = stage  # 0-indexed
        self.slot = slot  # 0-indexed

        self.spawn_type = spawn_type
        self.monster_id = monster_id
        self.monster_level = monster_level

        # If drop_monster_id == 9900, then drop_monster_level is the bonus gold amount
        self.drop_monster_id = drop_monster_id
        self.drop_monster_level = drop_monster_level
        self.plus_amount = plus_amount

        if monster:
            self.spawn_type = monster.spawn_type
            # Need to correct the drop/spawn IDs for NA vs JP
            mapping_fn = server_monster_id_fn(Server.from_str(self.server))
            self.monster_id = mapping_fn(monster.monster_id)
            self.monster_level = monster.monster_level
            self.drop_monster_id = mapping_fn(monster.drop_monster_id)
            self.drop_monster_level = monster.drop_monster_level
            self.plus_amount = monster.plus_amount

        self.pull_id = pull_id
        self.entry_id = entry_id

        self.leader_id = leader_id
        self.friend_id = friend_id

    def is_invade(self):
        return self.spawn_type == 2

    def get_drop(self):
        return self.drop_monster_id if self.drop_monster_id > 0 and self.get_coins() == 0 else None

    def get_coins(self):
        return self.drop_monster_level if self.drop_monster_id == WaveItem.DROP_MONSTER_ID_GOLD else 0

    def _table(self):
        return WaveItem.TABLE

    def _key(self):
        return WaveItem.KEY_COL

    def _insert_columns(self):
        return self.__dict__.keys()
