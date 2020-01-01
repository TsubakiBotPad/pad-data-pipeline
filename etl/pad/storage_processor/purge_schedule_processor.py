import logging
import os
from datetime import timedelta, datetime

from pad.db.db_util import DbWrapper
from pad.common.shared_types import Server
from pad.storage.exchange import Exchange
from pad.raw_processor import crossed_data
 
logger = logging.getLogger('processor')

def date2tstamp(date):
    return int(date.timestamp())

class PurgeScheduleProcessor(object):
    def __init__(self):
        pass

    def process(self, db: DbWrapper):
        db.fetch_data("DELETE FROM `schedule` WHERE end_timestamp < {}" \
                      .format(date2tstamp(datetime.now()-timedelta(weeks=4))))
