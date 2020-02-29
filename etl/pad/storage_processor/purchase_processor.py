import logging
import os
from typing import List

from pad.db.db_util import DbWrapper
from pad.common.shared_types import Server
from pad.storage.purchase import Purchase
from pad.storage.monster import MonsterWithMPValue
from pad.raw_processor import crossed_data

logger = logging.getLogger('processor')


class PurchaseProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.purchase_data = {
            Server.jp: data.jp_purchase,
            Server.na: data.na_purchase,
            Server.kr: data.kr_purchase,
        }

    def process(self, db: DbWrapper):
        for server, purchase_map in self.purchase_data.items():
            logger.debug('Process {} purchases'.format(server.name.upper()))
            for raw in purchase_map:
                logger.debug('Creating purchase: %s', raw)
                p_item = Purchase.from_raw_purchase(raw)
                db.insert_or_update(p_item)

        def purchases_to_map(purchases: List[Purchase]):
            return {x.monster_id: x.cost for x in purchases}

        monster_id_to_mp = purchases_to_map(self.purchase_data[Server.kr])
        monster_id_to_mp.update(purchases_to_map(self.purchase_data[Server.na]))
        monster_id_to_mp.update(purchases_to_map(self.purchase_data[Server.jp]))

        for monster_id, mp_cost in monster_id_to_mp.items():
            m_item = MonsterWithMPValue(monster_id=monster_id, buy_mp=mp_cost)
            db.insert_or_update(m_item)
