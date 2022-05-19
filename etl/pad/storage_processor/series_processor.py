import json
import logging
import os
from collections import defaultdict

from pad.db.db_util import DbWrapper
from pad.raw_processor import crossed_data
from pad.storage.series import MonsterSeries
from pad.storage.series import Series

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

logger = logging.getLogger('processor')


class SeriesProcessor(object):
    def __init__(self, data: crossed_data.CrossServerDatabase):
        with open(os.path.join(__location__, 'series.json')) as f:
            self.series = json.load(f)
        self.data = data

    def process(self, db: DbWrapper):
        for raw in self.series:
            item = Series.from_json(raw)
            db.insert_or_update(item)
