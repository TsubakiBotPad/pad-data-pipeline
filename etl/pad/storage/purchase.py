from datetime import timedelta

from pad.db.sql_item import SimpleSqlItem, ExistsStrategy
from pad.common.monster_id_mapping import jp_no_to_monster_id, nakr_no_to_monster_id
from pad.common.shared_types import Server

class Purchase(SimpleSqlItem):
    """MP Purchases."""
    TABLE = 'purchases'
    KEY_COL = 'purchase_id'

    @staticmethod
    def from_raw_purchase(o: "Purchase"):
        if o.server == Server.jp:
            id_mapper = jp_no_to_monster_id
        else:
            id_mapper = nakr_no_to_monster_id
        target_monster_id = id_mapper(o.monster_id)
        permanent = int(timedelta(seconds=(o.end_timestamp-o.start_timestamp)) > timedelta(days=60))
        return Purchase(server_id=o.server.value,
                        target_monster_id=target_monster_id,
                        mp_cost=o.cost,
                        amount=o.amount,
                        start_timestamp=o.start_timestamp,
                        end_timestamp=o.end_timestamp,
                        permanent=permanent)

    def __init__(self,
                 purchase_id: int = None,
                 server_id: int = None,
                 target_monster_id: int = None,
                 mp_cost: int = None,
                 amount: int = None,
                 start_timestamp: int = None,
                 end_timestamp: int = None,
                 permanent: int = None,
                 tstamp: int = None):
        self.purchase_id = purchase_id
        self.server_id = server_id
        self.target_monster_id = target_monster_id
        self.mp_cost = mp_cost
        self.amount = amount
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.permanent = permanent
        self.tstamp = tstamp

    def exists_strategy(self):
        return ExistsStrategy.BY_VALUE

    def _non_auto_insert_cols(self):
        return [self._key()]

    def _non_auto_update_cols(self):
        return [self._key()]

    def _lookup_columns(self):
        return ['server_id', 'target_monster_id']

    def __str__(self):
        return 'Purchase ({}): {} - {:,d}MP'.format(self.server_id, self.target_monster_id, self.mp_cost)
