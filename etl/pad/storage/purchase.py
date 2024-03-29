from datetime import timedelta

from pad.common.monster_id_mapping import server_monster_id_fn
from pad.db.sql_item import SimpleSqlItem


class Purchase(SimpleSqlItem):
    """MP Purchases."""
    TABLE = 'purchases'
    KEY_COL = {'server_id', 'target_monster_id', 'start_timestamp', 'end_timestamp'}

    @staticmethod
    def from_raw_purchase(o: "Purchase"):
        id_mapper = server_monster_id_fn(o.server)
        target_monster_id = id_mapper(o.monster_id)
        permanent = int(timedelta(seconds=(o.end_timestamp - o.start_timestamp)) > timedelta(days=60))
        return Purchase(server_id=o.server.value,
                        target_monster_id=target_monster_id,
                        mp_cost=o.cost,
                        amount=o.amount,
                        start_timestamp=o.start_timestamp,
                        end_timestamp=o.end_timestamp,
                        permanent=permanent)

    def __init__(self,
                 server_id: int = None,
                 target_monster_id: int = None,
                 mp_cost: int = None,
                 amount: int = None,
                 start_timestamp: int = None,
                 end_timestamp: int = None,
                 permanent: int = None,
                 tstamp: int = None):
        self.server_id = server_id
        self.target_monster_id = target_monster_id
        self.mp_cost = mp_cost
        self.amount = amount
        self.start_timestamp = start_timestamp
        self.end_timestamp = end_timestamp
        self.permanent = permanent
        self.tstamp = tstamp

    def __str__(self):
        return 'Purchase ({}): {} - {:,d}MP'.format(self.server_id, self.target_monster_id, self.mp_cost)
