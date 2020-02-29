import logging
import os
from datetime import timedelta, datetime

from pad.db.db_util import DbWrapper
from pad.common.shared_types import Server
from pad.raw_processor import crossed_data

logger = logging.getLogger('processor')

def date2tstamp(date):
    return int(date.timestamp())

class PurgeDataProcessor(object):
    def __init__(self):
        pass

    def process(self, db: DbWrapper):
        db.fetch_data("DELETE FROM `schedule` WHERE end_timestamp < {}" \
                      .format(date2tstamp(datetime.now()-timedelta(weeks=4))))
        schedule = db.fetch_data("SELECT ROW_COUNT()")[0]['ROW_COUNT()']
        db.fetch_data("DELETE FROM `deleted_rows` WHERE tstamp < {}" \
                      .format(date2tstamp(datetime.now()-timedelta(weeks=4))))
        del_rows = db.fetch_data("SELECT ROW_COUNT()")[0]['ROW_COUNT()']
        logger.info("purged {} old schedules and {} old deleted_rows".format(schedule, del_rows))
