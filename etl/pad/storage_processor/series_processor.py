from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.storage.series import Series


class SeriesProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        self.data = data

    def pre_process(self, db: DbWrapper):
        unsorted_item = Series(series_id=0,
                               name_jp='Unsorted',
                               name_na='Unsorted',
                               name_kr='Unsorted')
        db.insert_or_update(unsorted_item)

    def post_process(self, db: DbWrapper):
        pass
