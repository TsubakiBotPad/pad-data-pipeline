from datetime import timedelta

from pad.common.monster_id_mapping import server_monster_id_fn
from pad.db.sql_item import SimpleSqlItem, ExistsStrategy


class Exchange(SimpleSqlItem):
    """Monster exchanges."""
    TABLE = 'exchanges'
    KEY_COL = 'exchange_id'

    @staticmethod
    def from_raw_exchange(o):
        id_mapper = server_monster_id_fn(o.server)
        target_monster_id = id_mapper(o.monster_id)
        req_monster_csv_str = ','.join(['({})'.format(id_mapper(idx)) for idx in o.required_monsters])
        permanent = int(timedelta(seconds=(o.end_timestamp - o.start_timestamp)) > timedelta(days=60))
        return Exchange(trade_id=o.trade_id,
                        server_id=o.server.value,
                        target_monster_id=target_monster_id,
                        target_monster_amount=o.monster_amount,
                        required_monster_ids=req_monster_csv_str,
                        required_count=o.required_count,
                        start_timestamp=o.start_timestamp,
                        end_timestamp=o.end_timestamp,
                        permanent=permanent,
                        menu_idx=o.menu_idx,
                        order_idx=o.display_order,
                        flags=o.flag_type)

    def __init__(self,
                 exchange_id: int = None,
                 trade_id: int = None,
                 server_id: int = None,
                 target_monster_id: int = None,
                 target_monster_amount: int = None,
                 required_monster_ids: str = None,
                 required_count: int = None,
                 start_timestamp: int = None,
                 end_timestamp: int = None,
                 permanent: int = None,
                 menu_idx: int = None,
                 order_idx: int = None,
                 flags: int = None,
                 tstamp: int = None):
        self.exchange_id = exchange_id
        self.trade_id = trade_id
        self.server_id = server_id
        self.target_monster_id = target_monster_id
        self.target_monster_amount = target_monster_amount
        self.required_monster_ids = required_monster_ids
        self.required_count = required_count
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.permanent = permanent
        self.menu_idx = menu_idx
        self.order_idx = order_idx
        self.flags = flags
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]

    def _lookup_columns(self):
        return ['trade_id', 'server_id']

    def __str__(self):
        return 'Exchange ({}-{}): {} [{}]'.format(self.trade_id, self.server_id, self.target_monster_id,
                                                  self.required_count)
