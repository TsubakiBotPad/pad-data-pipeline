import logging
import os

from pad.db.db_util import DbWrapper
from pad.common.shared_types import Server
from pad.storage.exchange import Exchange
from pad.raw_processor import crossed_data

logger = logging.getLogger('processor')


class ExchangeProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.exchange_data = {
            Server.jp: data.jp_exchange,
            Server.na: data.na_exchange,
            Server.kr: data.kr_exchange,
        }

    def process(self, db: DbWrapper):
        for server, exchange_map in self.exchange_data.items():
            logger.debug('Process {} exchanges'.format(server.name.upper()))
            for raw in exchange_map:
                logger.debug('Creating exchange: %s', raw)
                item = Exchange.from_raw_exchange(raw)
                db.insert_or_update(item)
