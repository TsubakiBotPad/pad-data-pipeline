import logging
from datetime import datetime, timedelta

from pad.db.db_util import DbWrapper

logger = logging.getLogger('processor')


def date2tstamp(date):
    return int(date.timestamp())


class PurgeDataProcessor(object):
    def __init__(self):
        pass

    def process(self, db: DbWrapper):
        print('Starting deletion of old records')
        print('schedule size:', db.get_single_value('select count(*) from schedule'))
        print('deleted_rows size', db.get_single_value('select count(*) from deleted_rows'))

        # This is a hint to mysql that we shouldn't insert into deleted_rows
        # while purging. The client should handle deleting old events in bulk.
        db.fetch_data('set @TRIGGER_DISABLED=true')

        delete_timestamp = date2tstamp(datetime.now() - timedelta(weeks=4))
        print('deleting before', delete_timestamp)
        schedule_deletes = db.update_item(
            "DELETE FROM `schedule` WHERE end_timestamp < {}".format(delete_timestamp))
        deleted_row_deletes = db.update_item(
            "DELETE FROM `deleted_rows` WHERE tstamp < {}".format(delete_timestamp))

        logger.info("purged {} old schedules and {} old deleted_rows".format(schedule_deletes, deleted_row_deletes))
