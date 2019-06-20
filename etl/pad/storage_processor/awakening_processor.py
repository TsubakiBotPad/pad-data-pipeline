import json

from pad.db.db_util import DbWrapper
from pad.storage.awakening import Awakening


class AwakeningProcessor(object):
    def __init__(self):
        with open('awakening.json') as f:
            self.awakenings = json.load(f)

    def process(self, db: DbWrapper):
        for raw in self.awakenings:
            item = Awakening.from_json(raw)
            db.insert_or_update(item)